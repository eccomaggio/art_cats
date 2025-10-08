from tempfile import template
import convert as shared
from dataclasses import dataclass
import argparse
from pathlib import Path
from pprint import pprint
from enum import Enum, auto
import sys
import csv

# from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QGridLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QMessageBox,
)

settings = shared.settings


@dataclass
class Brick:
    height: int
    width: int
    # role: str


@dataclass
class Cell:
    brick_id: int
    # free_cells: int
    free_down: int
    free_across: int

    def __repr__(self) -> str:
        is_occupied = self.brick_id > -1
        return f"<{f'@{self.brick_id}' if is_occupied else "##"}> 1 else " "}>"


class BRICK(Enum):
    oneone = Brick(1, 1)
    onetwo = Brick(1, 2)
    onethree = Brick(1, 3)
    onefour = Brick(1, 4)
    twoone = Brick(2, 1)
    twotwo = Brick(2, 2)
    twothree = Brick(2, 3)
    twofour = Brick(2, 4)
    threeone = Brick(3, 1)
    threetwo = Brick(3, 2)
    threethree = Brick(3, 3)
    threefour = Brick(3, 4)
    fourone = Brick(4, 1)
    fourtwo = Brick(4, 2)
    fourthree = Brick(4, 3)
    fourfour = Brick(4, 4)


brick_lookup = {
    "1:1": BRICK.oneone,
    "1:2": BRICK.onetwo,
    "1:3": BRICK.onethree,
    "1:4": BRICK.onefour,
    "2:1": BRICK.twoone,
    "2:2": BRICK.twotwo,
    "2:3": BRICK.twothree,
    "2:4": BRICK.twofour,
    "3:1": BRICK.threeone,
    "3:2": BRICK.threetwo,
    "3:3": BRICK.threethree,
    "3:4": BRICK.threefour,
    "4:1": BRICK.fourone,
    "4:2": BRICK.fourtwo,
    "4:3": BRICK.fourthree,
    "4:4": BRICK.fourfour,
}


class COL(Enum):
    sublib = 0
    langs = auto()
    isbn = auto()
    title = auto()
    tr_title = auto()
    subtitle = auto()
    tr_subtitle = auto()
    parallel_title = auto()
    tr_parallel_title = auto()
    parallel_subtitle = auto()
    tr_parallel_subtitle = auto()
    country_name = auto()
    state = auto()
    place = auto()
    publisher = auto()
    pub_year = auto()
    copyright = auto()
    extent = auto()
    size = auto()
    series_title = auto()
    series_enum = auto()
    volume = auto()
    notes = auto()
    sales_code = auto()
    sale_dates = auto()
    hol_notes = auto()
    donation = auto()
    barcode = auto()
    start = 0


def select_brick_by_content_length(length: int) -> BRICK:
    if length < 50:
        return BRICK.oneone
    elif length < 100:
        return BRICK.onetwo
    elif length < 400:
        return BRICK.twotwo
    else:
        return BRICK.fourtwo


class STATUS(Enum):
    occupied = auto()
    toosmall = auto()
    ok = auto()


default_hint = (
    ## non-algorithmic version needs to be: [title, brick-type, start-row, start-col]
    ("sublibrary", "1:2", 0, 0),
    ("Language of resource", "1:2", 0, 2),
    ("ISBN", "1:2", 0, 4),
    ("Title", "2:3", 1, 0),
    ("Title transliteration", "2:3", 1, 3),
    ("Subtitle", "2:3", 3, 0),
    ("Subtitle transliteration", "2:3", 3, 3),
    ("Parallel title (dual language only)", "2:3", 5, 0),
    ("Parallel title transliteration", "2:3", 5, 3),
    ("Parallel subtitle (dual language only)", "2:3", 7, 0),
    ("Parallel subtitle transliteration", "2:3", 7, 3),
    ("Country of publication", "1:2", 13, 0),
    ("State (US/UK/CN/AU only)", "1:2", 13, 2),
    ("Place of publication", "1:2", 13, 4),
    ("Publisher name", "1:4", 14, 0),
    ("Date of publication", "1:1", 14, 4),
    ("Copyright date", "1:1", 14, 5),
    ("Pagination", "1:1", 15, 1),
    ("Size", "1:1", 15, 0),
    ("Series title", "1:3", 12, 0),
    ("Series enumeration", "1:2", 12, 3),
    ("Volume", "1:1", 12, 5),
    ("Note", "3:3", 9, 0),
    ("Sale code", "1:1", 15, 2),
    ("Date of sale", "1:3", 15, 3),
    ("HOL notes", "3:3", 9, 3),
    ("Donor note", "1:4", 16, 0),
    ("Barcode ", "1:2", 16, 4),
)

settings.flavour = {
    "title": "art_catalogue",
    "fields_to_clear": [
        COL.barcode,
        COL.hol_notes,
        COL.extent,
        COL.pub_year,
        COL.sale_dates,
        COL.copyright,
        COL.sale_dates,
    ],
}


class Grid:
    def __init__(self, width: int = 6) -> None:
        self.grid_width = width
        self.current_row = 0
        self.rows: list[list[int]] = (
            []
        )  ## each row is a list of brick ids OR -1 to indicate cell is unoccupied
        self.add_a_row()
        self.widget_info: dict[int, tuple[int, int, Brick, str]] = (
            {}
        )  ## dict[id: (start_row, start_col, Brick(height, width), title)]

    @property
    def total_rows(self) -> int:
        return len(self.rows)

    def exceeds_grid_length(self, current_row: int) -> bool:
        return current_row + 1 > self.total_rows

    def is_free(self, id: int) -> bool:
        return id == -1

    def is_occupied(self, id: int) -> bool:
        return not self.is_free(id)

    def add_a_row(self) -> None:
        # self.rows.append([-1 for _ in range(self.grid_width)])
        self.rows.append(self.make_row())

    def make_row(self) -> list:
        return [-1 for _ in range(self.grid_width)]

    def add_brick_algorithmically(
        self, brick_id: int, brick: Brick, title: str = ""
    ) -> None:
        """
        algorithm:
        1. check the brick will fit in the current grid (error if not)
        2. check the grid has sufficient empty spaces across and down for new brick
        3. expand the grid to accommodate the height of the new brick
        4. to avoid scrambling order of bricks:
            a. check for available space starting from the row where the last brick was inserted ("current_row")
            b. only insert a brick if there are no bricks after the first free space in the row
        """
        if brick.width > self.grid_width:
            print("Input field has been truncated to fit the grid.")
            brick.width = self.grid_width
        if not title:
            title = f"input #{brick_id}"
        # row_i = 0
        row_i = self.current_row
        no_place_found_for_brick = True
        while no_place_found_for_brick:
            rows_needed = row_i + brick.height
            if self.total_rows - rows_needed < 0:
                extra_rows = rows_needed - self.total_rows + 1
                for _ in range(extra_rows):
                    self.add_a_row()
            for col_i in range(self.grid_width):
                if self.is_occupied(self.rows[row_i][col_i]):
                    continue
                enough_space_across = (
                    self.count_free_spaces_across(row_i, col_i) - brick.width >= 0
                )
                enough_space_down = (
                    self.count_free_spaces_down(row_i, col_i) - brick.height >= 0
                )
                no_following_bricks = all(el == -1 for el in self.rows[row_i][col_i:])
                if enough_space_across and enough_space_down and no_following_bricks:
                    no_place_found_for_brick = False
                    self.place_brick_in_grid(brick, brick_id, row_i, col_i)
                    self.widget_info[brick_id] = (row_i, col_i, brick, title)
                    self.current_row = row_i
                    break
            row_i += 1

    def add_bricks_by_template(self, template: tuple) -> None:
        last_brick = template[-1]
        last_brick_start_col = last_brick[2]
        last_brick_height = brick_lookup[last_brick[1]].value.height
        max_row = last_brick_start_col + last_brick_height
        self.rows = [self.make_row() for _ in range(max_row)]
        for brick_id, (title, type_name, start_row, start_col) in enumerate(template):
            brick = brick_lookup[type_name].value
            self.place_brick_in_grid(brick, brick_id, start_row, start_col)
            self.widget_info[brick_id] = (start_row, start_col, brick, title)

    def count_free_spaces_across(self, row, start_col):
        free_spaces = 0
        for col_i in range(start_col, self.grid_width):
            if self.is_occupied(self.rows[row][col_i]):
                return free_spaces
            free_spaces += 1
        return free_spaces

    def count_free_spaces_down(self, start_row, col):
        free_spaces = 0
        row_i = start_row
        while True:
            if self.exceeds_grid_length(row_i) or self.is_occupied(
                self.rows[row_i][col]
            ):
                return free_spaces
            free_spaces += 1
            row_i += 1

    def place_brick_in_grid(
        self, brick: Brick, brick_id: int, start_row: int, start_col: int
    ) -> None:
        for row_i in range(start_row, start_row + brick.height):
            for col_i in range(start_col, start_col + brick.width):
                self.rows[row_i][col_i] = brick_id


class MainWindow(QMainWindow):
    def __init__(self, grid: Grid, excel_rows: list[list[str]], file_name: str):
        super().__init__()
        self.grid = grid
        self.excel_rows = excel_rows
        self.col_count = len(excel_rows[0])
        self.file_name = file_name
        self.short_file_name = self.get_filename_only(settings.in_file)
        self.current_row = len(excel_rows) - 1
        master_layout = QVBoxLayout()
        inputs_layout = QGridLayout()
        nav_layout = QGridLayout()
        self.fieldset = QGroupBox("Navigation")
        # self.fieldset.setStyleSheet(
        #    "QGroupBox {background-color: lightgrey;}"
        # )
        self.has_unsaved_text = False

        self.style_for_default_input = "border: 2px solid lightgrey;"
        self.style_if_text_changed = "border: 2px solid red;"
        self.style_for_labels = "font-weight: bold;"

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setStyleSheet("font-weight: bold;")
        self.submit_btn.clicked.connect(self.handle_submit)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.handle_close)
        self.load_file_btn = QPushButton("Load file")
        self.load_file_btn.clicked.connect(self.open_file_dialog)

        self.first_btn = QPushButton("First")
        self.first_btn.clicked.connect(self.go_to_first_record)
        self.last_btn = QPushButton("Last")
        self.last_btn.clicked.connect(self.go_to_last_record)
        self.prev_btn = QPushButton("<")
        self.prev_btn.clicked.connect(self.go_to_previous_record)
        self.next_btn = QPushButton(">")
        self.next_btn.clicked.connect(self.go_to_next_record)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet("color: red;")
        self.clear_btn.clicked.connect(self.clear_form)
        self.new_btn = QPushButton("New")
        self.new_btn.clicked.connect(self.start_new_record)
        self.save_btn = QPushButton("Export as .csv file")
        self.save_btn.clicked.connect(self.save_as_csv)
        # self.save_btn.setEnabled(False)
        self.marc_btn = QPushButton("Export as MARC")
        self.marc_btn.clicked.connect(self.save_as_marc)
        # self.marc_btn.setEnabled(False)

        self.inputs = []
        self.labels = []
        for id, (start_row, start_col, brick, title) in self.grid.widget_info.items():
            row_span, col_span = brick.height, brick.width
            tmp_input: QLineEdit | QTextEdit
            tmp_input = QLineEdit() if row_span == 1 else QTextEdit()
            self.inputs.append(tmp_input)

            tmp_wrapper = QVBoxLayout()
            tmp_label = QLabel(title)
            # tmp_label.setStyleSheet(self.style_for_labels)
            font = tmp_label.font()
            font.setBold(True)
            tmp_label.setFont(font)
            self.labels.append(tmp_label)

            tmp_wrapper.addWidget(tmp_label)
            # tmp_wrapper.addWidget(QLabel(title))
            tmp_wrapper.addWidget(tmp_input)
            if isinstance(tmp_input, QLineEdit):
                tmp_wrapper.addStretch(1)
            tmp_wrapper.setSpacing(3)
            inputs_layout.addLayout(
                tmp_wrapper, start_row, start_col, row_span, col_span
            )
        self.add_signal_to_fire_on_text_change()

        last_id = list(grid.widget_info.keys())[-1]
        last_widget = grid.widget_info[last_id]
        last_row = last_widget[0] + last_widget[2].height
        nav_layout.addWidget(self.first_btn, last_row, 0, 1, 1)
        nav_layout.addWidget(self.prev_btn, last_row, 1, 1, 1)
        nav_layout.addWidget(self.next_btn, last_row, 2, 1, 1)
        nav_layout.addWidget(self.last_btn, last_row, 3, 1, 1)
        last_row += 1
        nav_layout.addWidget(self.new_btn, last_row, 0, 1, 1)
        nav_layout.addWidget(self.submit_btn, last_row, 1, 1, 2)
        nav_layout.addWidget(self.clear_btn, last_row, 3, 1, 1)
        last_row += 1
        nav_layout.addWidget(self.load_file_btn, last_row, 0, 1, 1)
        nav_layout.addWidget(self.save_btn, last_row, 1, 1, 1)
        nav_layout.addWidget(self.marc_btn, last_row, 2, 1, 1)
        nav_layout.addWidget(self.close_btn, last_row, 3, 1, 1)

        master_layout.addLayout(inputs_layout)
        # master_layout.addLayout(nav_layout)
        self.fieldset.setLayout(nav_layout)
        master_layout.addWidget(self.fieldset)
        master_layout.addStretch(1)
        widget = QWidget()
        widget.setLayout(master_layout)
        self.setCentralWidget(widget)
        self.update_current_position("last")
        self.add_custom_behaviour()

    def add_custom_behaviour(self) -> None:
        if settings.flavour["title"] == "art_catalogue":
            sale_dates = self.inputs[COL.sale_dates.value]
            if isinstance(sale_dates, QLineEdit):
                sale_dates.editingFinished.connect(self.saledates_action)
            for label in self.labels:
                if "transliteration" in label.text():
                    font = label.font()
                    font.setBold(False)
                    font.setItalic(True)
                    label.setFont(font)

    @property
    def current_record_is_new(self):
        return self.current_row == -1

    def handle_submit(self):
        ## TODO add request for confirmation (as this could be destructive)
        # log_text = ""
        data = []
        for i, el in enumerate(self.inputs):
            if isinstance(el, QLineEdit):
                data.append(el.text())
                # log_text += f"id:{i}='{el.text()}'"
            elif isinstance(el, QTextEdit):
                data.append(el.toPlainText())
                # log_text += f"id:{i}='{el.toPlainText()}'"
            else:
                print(
                    f"Huston, we have a problem with submitting record no. {self.current_row}"
                )
        if self.current_row < 0:
            self.excel_rows.append(data)
            self.current_row = len(self.excel_rows) - 1
            self.update_title_with_record_number()
            self.update_input_styles()
        else:
            self.excel_rows[self.current_row] = data
        self.has_unsaved_text = False
        self.update_input_styles()
        self.add_signal_to_fire_on_text_change()
        # print(f"Submitted record no. {self.current_row}: {log_text}")

    def handle_close(self) -> None:
        self.close()

    def go_to_first_record(self) -> None:
        self.update_current_position("first")

    def go_to_last_record(self) -> None:
        self.update_current_position("last")

    def go_to_previous_record(self) -> None:
        self.update_current_position("back")

    def go_to_next_record(self) -> None:
        self.update_current_position("forwards")

    def saledates_action(self) -> None:
        # print("sales_date filled in!!")
        sender = self.sender()
        # sender = self.inputs[COL.sale_dates.value]
        pubdate = self.inputs[COL.pub_year.value]
        if isinstance(sender, QLineEdit) and isinstance(pubdate, QLineEdit):
            if not pubdate.text():
                year_of_pub = sender.text().strip()[:4]
                # print(f">>>>>>>>> {year_of_pub}")
                pubdate.setText(year_of_pub)
        else:
            print("Can't access salecode or pubdate fields...")

    def update_title_with_record_number(self, text="", prefix="Record no. "):
        text = text if text else str(self.current_row)
        # self.setWindowTitle(f"[{self.short_file_name}]: {prefix}{text}")
        self.setWindowTitle(f"[{settings.in_file}]: {prefix}{text}")
        self.update_input_styles()

    def update_input_styles(self, mode="default"):
        stylesheet = (
            self.style_for_default_input
            if mode == "default"
            else self.style_if_text_changed
        )
        for input in self.inputs:
            input.setStyleSheet(stylesheet)

    def add_signal_to_fire_on_text_change(self):
        for input in self.inputs:
            if isinstance(input, QLineEdit):
                input.textEdited.connect(self.alert_on_textchange)
            elif isinstance(input, QTextEdit):
                input.textChanged.connect(self.alert_on_textchange)

    def alert_on_textchange(self) -> None:
        sender = self.sender()
        if isinstance(sender, QLineEdit):
            sender.setStyleSheet(self.style_if_text_changed)
            sender.textEdited.disconnect(self.alert_on_textchange)
        elif isinstance(sender, QTextEdit):
            sender.setStyleSheet(self.style_if_text_changed)
            sender.textChanged.disconnect(self.alert_on_textchange)
        else:
            print("Huston, we have a problem with text input...")
        self.has_unsaved_text = True
        # print("text changed")

    def load_record_into_gui(self, excel_row=None) -> None:
        # msg = "record loaded" if excel_row else "record cleared"
        for i, el in enumerate(self.inputs):
            data = "" if not excel_row else excel_row[i]
            if isinstance(el, QLineEdit):
                el.setText(data)
            elif isinstance(el, QTextEdit):
                el.setPlainText(data)
            else:
                print("Huston, we have a problem loading data into the form...")
        self.update_input_styles()
        self.add_signal_to_fire_on_text_change()
        # print(msg)

    def clear_form(self) -> None:
        # if self.current_row != -1 and self.abort_on_clearing_existing_record(self):
        if not self.current_record_is_new and self.abort_on_clearing_existing_record(
            self
        ):
            return
        self.load_record_into_gui()

    def start_new_record(self) -> None:
        # print("new record")
        self.current_row = -1
        if settings.flavour["title"] == "art_catalogue":
            for field in settings.flavour["fields_to_clear"]:
                self.inputs[field.value].setText("")
            self.inputs[COL.sublib.value].setText("ARTBL")
        # fields_to_clear = [COL.barcode, COL.hol_notes, COL.extent, COL.pub_year, COL.sale_dates, COL.copyright, COL.sale_dates]
        # for field in fields_to_clear:
        #     self.inputs[field.value].setText("")
        # self.inputs[COL.sublib.value].setText("ARTBL")
        self.has_unsaved_text = True
        self.update_title_with_record_number("[new]")

    def update_current_position(self, direction) -> None:
        if self.has_unsaved_text and self.abort_on_unsaved_text(self):
            return
        index_of_last_record = len(self.excel_rows) - 1
        match direction:
            case "first":
                self.current_row = 0
            case "last":
                self.current_row = index_of_last_record
            case "back":
                if self.current_row > 0:
                    self.current_row -= 1
            case _:
                if self.current_row < index_of_last_record:
                    self.current_row += 1
        msg = str(self.current_row)
        if self.current_row == 0:
            msg += " (first)"
            self.first_btn.setEnabled(False)
            self.prev_btn.setEnabled(False)
            self.last_btn.setEnabled(True)
            self.next_btn.setEnabled(True)
        elif self.current_row == index_of_last_record:
            msg += " (last)"
            self.last_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self.first_btn.setEnabled(True)
            self.prev_btn.setEnabled(True)
        else:
            self.first_btn.setEnabled(True)
            self.prev_btn.setEnabled(True)
            self.last_btn.setEnabled(True)
            self.next_btn.setEnabled(True)

        self.update_title_with_record_number(msg)
        self.load_record_into_gui(self.excel_rows[self.current_row])
        self.has_unsaved_text = False
        # self.load_record_into_gui()
        self.update_input_styles()

    def save_as_csv(self) -> None:
        headers = [el[3] for el in self.grid.widget_info.values()]
        file_name = (
            f"{settings.out_file}.csv"
            if settings.out_file
            else settings.default_output_filename
        )
        write_to_csv(file_name, self.excel_rows, headers)
        msg = f"The {len(self.excel_rows)} records in {settings.in_file} have been successfully saved as {file_name}."
        logger.info(msg)
        msg_box = QMessageBox()
        msg_box.setText(msg)
        msg_box.exec()

    def save_as_marc(self) -> None:
        # records = shared.parse_rows_into_records(self.excel_rows)
        marc_records = shared.build_marc_records(
            shared.parse_rows_into_records(self.excel_rows)
        )
        file_name = (
            settings.out_file
            if settings.out_file
            else settings.default_output_filename
        )
        # print(f">>>>>>> out_file = {file_name}")
        shared.write_marc_files(marc_records, Path(file_name))
        msg = f"The {len(self.excel_rows)} records in {settings.in_file} have been successfully saved as {file_name}.mrk/.mrc in {settings.output_dir}."
        logger.info(msg)
        msg_box = QMessageBox()
        msg_box.setText(msg)
        msg_box.exec()

    def abort_on_unsaved_text(self, s) -> int:
        # print("unsaved text alert...", s)
        dialogue = DialogueOkCancel(
            self,
            "There is unsaved text in this record. Are you OK to contine and lose this text?",
        )
        return dialogue.exec() != 1

    def abort_on_clearing_existing_record(self, s) -> int:
        # print("unsaved text alert...", s)
        dialogue = DialogueOkCancel(
            self,
            "This wipes the existing record when you save it. Are you OK to contine and lose this text?",
        )
        return dialogue.exec() != 1

    def open_file_dialog(self):
        """Opens the native file selection dialog and processes the result."""
        # This returns a tuple: (file_path, filter_used)
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            parent=self,  # The parent widget (for centering)
            caption="Select a file.",
            dir="./excel_files",
            filter="Database Files (*.xls *.xlsx *.xlsm *.csv *.tsv)",
        )
        if file_path:
            # self.short_file_name = self.get_filename_only(file_path)
            settings.in_file_full = file_path
            settings.in_file = self.get_filename_only(file_path)
            settings.out_file = settings.in_file
            print(f"File Selected: {settings.in_file} ({file_path})")
            # headers, self.excel_rows = shared.parse_file_into_rows(Path(file_path))
            headers, self.excel_rows = shared.parse_file_into_rows(Path(file_path))
            if not settings.use_default_layout:
                print("Haven't coded for non-default layout yet!")
                ## TODO: code for change of layout on file loading (i.e. make a standalone: 'load file and update grid' function)
            self.update_current_position("last")
            logger.info(f"Just opened {file_path}")
        else:
            print("Selection cancelled.")

    def get_filename_only(self, file_path: str) -> str:
        if name_start_index := file_path.rfind("/") + 1:
            file_name = file_path[name_start_index:]
        else:
            file_name = file_path
        return file_name


class DialogueOkCancel(QDialog):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.text = text

        button = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(button)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel(text)
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


def launch_gui(grid: Grid, excel_rows: list[list[str]], file_name: str) -> None:
    app = QApplication(sys.argv)
    window = MainWindow(grid, excel_rows, file_name)
    window.show()
    app.exec()


def create_max_lengths(rows: list[list[str]]) -> list[int]:
    max_lengths: list[list[int]] = [[] for _ in rows[0]]
    for row in rows:
        for i, col in enumerate(row):
            max_lengths[i].append(len(col))
    return [max(col) for col in max_lengths]


def write_to_csv(file_name: str, data: list[list[str]], headers: list[str]) -> None:
    out_file = Path(settings.output_dir) / Path(file_name)
    with open(out_file, "w", newline="") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(headers)
        csvwriter.writerows(data)


def read_cli_into_settings() -> None:
    parser = argparse.ArgumentParser()

    # parser.add_argument("--file", "-f", type=str, required=True)
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        required=False,
        help="file to edit",
    )
    # parser.add_argument(
    #     "--out",
    #     "-o",
    #     type=str,
    #     required=False,
    #     help="name to give saved file",)
    args = parser.parse_args()
    settings.in_file = args.file
    if file := args.file:
        settings.in_file = file
    else:
        settings.is_existing_file = False
        settings.in_file = settings.default_output_filename
    settings.layout_template = default_hint


def main():
    read_cli_into_settings()
    grid = Grid()
    if settings.is_existing_file:
        print(f"processing file: {settings.in_file}")
        headers, rows = shared.parse_file_into_rows(Path(settings.in_file))
        if settings.use_default_layout:
            grid.add_bricks_by_template(settings.layout_template)
        else:
            # print(f"no. of rows = {len(rows[0])}")
            max_lengths = create_max_lengths(rows)
            layout = [select_brick_by_content_length(length) for length in max_lengths]
            # layout = [BRICK.oneone, BRICK.twotwo, BRICK.oneone, BRICK.onetwo, BRICK.onetwo, BRICK.fourtwo, BRICK.twotwo, BRICK.twotwo, BRICK.twotwo]
            # layout = [BRICK.onetwo, BRICK.onetwo, BRICK.onefour, BRICK.fourfour]
            # layout = [BRICK.twothree, BRICK.onetwo, BRICK.threethree, BRICK.fourfour]
            # layout = [BRICK.oneone, BRICK.onetwo, BRICK.onethree, BRICK.onefour, BRICK.twoone,BRICK.twotwo, BRICK.twothree, BRICK.twofour, BRICK.threeone, BRICK.threetwo, BRICK.threethree, BRICK.threefour, BRICK.fourone, BRICK.fourtwo, BRICK.fourthree, BRICK.fourfour]
            # headers = [f"col {i}" for i in range(len(layout))]
            # print(headers)
            # print(max_lengths)
            # print(layout)

            # pprint(list(zip(headers, max_lengths, layout)))
            # print("\n\n")
            # pprint(grid.rows)
            for id, brick_enum in enumerate(layout):
                brick = brick_enum.value
                grid.add_brick_algorithmically(id, brick, headers[id])
    else:
        print("creating new file")
        template = settings.layout_template
        rows = [["" for _ in range(len(template))]]
        grid.add_bricks_by_template(template)

    # pprint(grid.rows)
    # pprint(grid.widget_info)

    launch_gui(grid, rows, settings.in_file)


if __name__ == "__main__":
    logger = shared.logging.getLogger(__name__)
    shared.logger = shared.logging.getLogger(__name__)
    main()
