import art_cats as shared
from dataclasses import dataclass
from turtle import width
import argparse
from pathlib import Path
from pprint import pprint
from enum import Enum, auto
import sys
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
    QDialogButtonBox
)

parser = argparse.ArgumentParser()

parser.add_argument("--file", "-f", type=str, required=True)
args = parser.parse_args()

@dataclass
class Brick():
    height: int
    width: int
    # role: str

@dataclass
class Cell():
    brick_id: int
    # free_cells: int
    free_down: int
    free_across: int

    def __repr__(self) -> str:
        is_occupied = self.brick_id > -1
        return f"<{f'@{self.brick_id}' if is_occupied else "##"}> 1 else ""}>"

class BRICK(Enum):
    oneone = Brick(1, 1)
    onetwo = Brick(1, 2)
    onethree = Brick(1, 3)
    onefour = Brick(1, 4)
    twoone = Brick(2, 1)
    twotwo = Brick(2, 2)
    twothree = Brick(2, 3)
    twofour = Brick(2,4)
    threeone = Brick(3, 1)
    threetwo = Brick(3, 2)
    threethree = Brick(3, 3)
    threefour = Brick(3, 4)
    fourone = Brick(4, 1)
    fourtwo = Brick(4, 2)
    fourthree = Brick(4, 3)
    fourfour = Brick(4, 4)


def select_brick_by_content_length(length:int) -> BRICK:
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


class Grid():
    def __init__(self, width:int = 4) -> None:
        self.grid_width = width
        self.rows:list[list[int]] = []  ## each row is a list of brick ids OR -1 to indicate cell is unoccupied
        self.add_a_row()
        self.widget_info: dict[int,tuple[int, int, Brick, str]] = {}    ## dict[id: (start_row, start_col, Brick(height, width), title)]

    @property
    def total_rows(self) -> int:
        return len(self.rows)

    def exceeds_grid_length(self, current_row:int) -> bool:
        return current_row + 1 > self.total_rows

    def is_free(self, id:int) -> bool:
        return id == -1

    def is_occupied(self, id:int) -> bool:
        return not self.is_free(id)

    def add_a_row(self):
        self.rows.append([-1 for _ in range(self.grid_width)])

    def add_brick(self, brick_id:int, brick:Brick, title:str = "") -> None:
        if brick.width > self.grid_width:
            print("Input field has been truncated to fit the grid.")
            brick.width = self.grid_width
        if not title:
            title = f"input #{brick_id}"
        row_i = 0
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
                enough_space_across = self.count_free_spaces_across(row_i, col_i) - brick.width >= 0
                enough_space_down = self.count_free_spaces_down(row_i, col_i) - brick.height >= 0
                if enough_space_across and enough_space_down:
                    no_place_found_for_brick = False
                    self.place_brick_in_grid(brick, brick_id, row_i, col_i)
                    self.widget_info[brick_id] = (row_i, col_i, brick, title)
                    break
            row_i += 1

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
            if  self.exceeds_grid_length(row_i) or self.is_occupied(self.rows[row_i][col]):
                return free_spaces
            free_spaces += 1
            row_i += 1

    def place_brick_in_grid(self, brick: Brick, brick_id:int, start_row:int, start_col:int) -> None:
        for row_i in range(start_row, start_row + brick.height):
            for col_i in range(start_col, start_col + brick.width):
                self.rows[row_i][col_i] = brick_id


class MainWindow(QMainWindow):
    def __init__(self, grid:Grid, excel_rows:list[list[str]]):
        super().__init__()
        self.excel_rows = excel_rows
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

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setStyleSheet("font-weight: bold;")
        self.submit_btn.clicked.connect(self.handle_submit)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.handle_close)

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
        self.save_btn = QPushButton("Save as .csv file")
        self.save_btn.clicked.connect(self.save_as_csv)
        self.save_btn.setEnabled(False)
        self.marc_btn = QPushButton("Save as MARC")
        self.marc_btn.clicked.connect(self.save_as_marc)
        self.marc_btn.setEnabled(False)

        self.inputs = []
        for id, (start_row, start_col, brick, title) in grid.widget_info.items():
            row_span, col_span = brick.height, brick.width
            tmp_input: QLineEdit | QTextEdit
            tmp_input = QLineEdit() if row_span == 1 else QTextEdit()
            self.inputs.append(tmp_input)

            tmp_wrapper = QVBoxLayout()
            tmp_wrapper.addWidget(QLabel(title))
            tmp_wrapper.addWidget(tmp_input)
            if isinstance(tmp_input, QLineEdit):
                tmp_wrapper.addStretch(1)
            tmp_wrapper.setSpacing(3)
            inputs_layout.addLayout(tmp_wrapper, start_row, start_col, row_span, col_span)
        self.add_signal_to_fire_on_text_change()

        last_id = list(grid.widget_info.keys())[-1]
        last_widget = grid.widget_info[last_id]
        last_row = last_widget[0] + last_widget[2].height
        nav_layout.addWidget(self.first_btn, last_row,0,1,1)
        nav_layout.addWidget(self.prev_btn, last_row,1,1,1)
        nav_layout.addWidget(self.next_btn, last_row,2,1,1)
        nav_layout.addWidget(self.last_btn, last_row,3,1,1)
        last_row += 1
        nav_layout.addWidget(self.new_btn, last_row,0,1,1)
        nav_layout.addWidget(self.submit_btn, last_row,1,1,2)
        nav_layout.addWidget(self.clear_btn, last_row,3,1,1)
        last_row += 1
        nav_layout.addWidget(self.save_btn, last_row,0,1,1)
        nav_layout.addWidget(self.marc_btn, last_row,1,1,1)
        nav_layout.addWidget(self.close_btn, last_row,2,1,2)

        master_layout.addLayout(inputs_layout)
        # master_layout.addLayout(nav_layout)
        self.fieldset.setLayout(nav_layout)
        master_layout.addWidget(self.fieldset)
        master_layout.addStretch(1)
        widget = QWidget()
        widget.setLayout(master_layout)
        self.setCentralWidget(widget)
        self.update_current_position("last")

    @property
    def current_record_is_new(self):
        return self.current_row == -1

    def handle_submit(self):
        ## TODO add request for confirmation (as this could be destructive)
        log_text = ""
        data = []
        for i, el in enumerate(self.inputs):
            if isinstance(el, QLineEdit):
                data.append(el.text())
                log_text += f"id:{i}='{el.text()}'"
            elif isinstance(el, QTextEdit):
                data.append(el.toPlainText())
                log_text += f"id:{i}='{el.toPlainText()}'"
            else:
                print(f"Huston, we have a problem with submitting record no. {self.current_row}")
            # try:
            #     output += f"id:{i}='{el.text()}'"
            # except AttributeError:
            #     output += f"id:{i}='{el.toPlainText()}'"
        if self.current_row < 0:
            self.excel_rows.append(data)
            self.current_row = len(self.excel_rows) - 1
            self.update_title_with_record_number()
            self.update_input_styles()
        else:
            self.excel_rows[self.current_row] = data
        print(f"Submitted record no. {self.current_row}: {log_text}")

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

    def update_title_with_record_number(self, text="", prefix="Record no. "):
        text = text if text else str(self.current_row)
        self.setWindowTitle(prefix + text)
        self.update_input_styles()

    def update_input_styles(self, mode="default"):
        stylesheet = self.style_for_default_input if mode == "default" else self.style_if_text_changed
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
        msg = "record loaded" if excel_row else "record cleared"
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
        print(msg)

    def clear_form(self) -> None:
        # if self.current_row != -1 and self.abort_on_clearing_existing_record(self):
        if not self.current_record_is_new and self.abort_on_clearing_existing_record(self):
            return
        ## TODO add request for confirmation (as this could be destructive)
        self.load_record_into_gui()

    def start_new_record(self) -> None:
        print("new record")
        self.current_row = -1
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
        pass

    def save_as_marc(self) -> None:
        pass

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

class DialogueOkCancel(QDialog):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.text = text

        button = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(button)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel(text)
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


def launch_gui(grid:Grid, excel_rows:list[list[str]]) -> None:
    app = QApplication(sys.argv)
    window = MainWindow(grid, excel_rows)
    window.show()
    app.exec()

def create_max_lengths(rows:list[list[str]]) -> list[int]:
    max_lengths:list[list[int]] = [[] for _ in rows[0]]
    for row in rows:
        for i, col in enumerate(row):
            max_lengths[i].append(len(col))
    return [max(col) for col in max_lengths]

def main():
    if args.file:
        print(f"processing file: {args.file}")
        file = Path(args.file)
        headers, rows = shared.parse_excel_into_rows(file)
        print(f"no. of rows = {len(rows[0])}")
        # max_lengths = [max([len(content) for content in rows[i]]) for i in range(len(rows[0]))]
        # max_lengths = [[] for _ in rows[0]]
        # for row in rows:
        #     for i, col in enumerate(row):
        #         max_lengths[i].append(len(col))
        # max_lengths = [max(col) for col in max_lengths]
        max_lengths = create_max_lengths(rows)
        # print(max_lengths)

        layout = [select_brick_by_content_length(length) for length in max_lengths]
        # layout = [BRICK.oneone, BRICK.twotwo, BRICK.oneone, BRICK.onetwo, BRICK.onetwo, BRICK.fourtwo, BRICK.twotwo, BRICK.twotwo, BRICK.twotwo]
        # layout = [BRICK.onetwo, BRICK.onetwo, BRICK.onefour, BRICK.fourfour]
        # layout = [BRICK.twothree, BRICK.onetwo, BRICK.threethree, BRICK.fourfour]
        # print(headers)
        # print(max_lengths)
        # print(layout)
        pprint(list(zip(headers, max_lengths, layout)))
        grid = Grid(6)
        print("\n\n")
        pprint(grid.rows)
        for id, brick_enum in enumerate(layout):
            brick = brick_enum.value
            # grid.add_brick(id, brick)
            grid.add_brick(id, brick, headers[id])
            # print(f">>>>>>> Brick {id} just fitted")

        pprint(grid.rows)
        pprint(grid.widget_info)

        launch_gui(grid, rows)

if __name__ == "__main__":
    main()
