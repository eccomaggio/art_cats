import art_cats as shared
from dataclasses import dataclass
from turtle import width
import argparse
from pathlib import Path
from pprint import pprint
from enum import Enum, auto
import sys
# from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QLabel, QLineEdit, QTextEdit, QWidget, QVBoxLayout

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
    free_cells: int

    def __repr__(self) -> str:
        is_occupied = self.brick_id > -1
        return f"<{f'@{self.brick_id}' if is_occupied else "##" }: {self.free_cells} slot{"s" if self.free_cells > 1 else ""}>"

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
        self.rows:list[list[Cell]] = []
        self.add_a_row()
        self.widget_info: dict[int,tuple[int, int, Brick, str]] = {}    ## dict[key: (start_row, start_col, Brick(height, width), title)]

    def exceeds_grid_length(self, zero_index:int) -> bool:
        return zero_index + 1 > len(self.rows)

    def is_free(self, id:int) -> bool:
        return id == -1

    def add_a_row(self):
        self.rows.append([Cell(-1, self.grid_width - slot) for slot in range(self.grid_width)])

    def fit_brick(self, brick_id:int, brick:Brick, title:str = "") -> None:
        fit_status:STATUS
        row_index = 0
        # while row_index < 10:
        while row_index < 40:
            for col_index in range(self.grid_width):
                current_slot = self.rows[row_index][col_index]
                fit_status = self.check_col_fit(brick, current_slot)
                # print(f"brick id: {brick_id} ({row_index},{col_index}):{fit_status}->{brick}")
                match fit_status:
                    case STATUS.occupied:
                        continue
                    case STATUS.toosmall:
                        break
                    case STATUS.ok :
                        fit_status = self.check_row_fit(brick, row_index, col_index)
                        match fit_status:
                            case STATUS.occupied:
                                continue
                            case STATUS.toosmall:
                                break
                            case STATUS.ok:
                                self.add_brick(brick, brick_id, row_index, col_index, title)
                                return
            row_index += 1
            if self.exceeds_grid_length(row_index):
                self.add_a_row()

    def check_col_fit(self, brick:Brick, current_slot:Cell) -> STATUS:
        if current_slot.brick_id > -1:
            output = STATUS.occupied
        elif current_slot.free_cells < brick.width:
            output = STATUS.toosmall
        else:
            output = STATUS.ok
        return output

    def check_row_fit(self, brick:Brick, row_index: int, col_index: int) -> STATUS:
        fit_status:STATUS
        if brick.height == 1:
            fit_status = STATUS.ok
        else:
            for i in range(brick.height - 1):
                next_row = row_index + i + 1
                if self.exceeds_grid_length(next_row):
                    self.add_a_row()
                next_slot = self.rows[next_row][col_index]
                if self.is_free(next_slot.brick_id) and next_slot.free_cells >= brick.width:
                    fit_status = STATUS.ok
                else:
                    fit_status = STATUS.occupied
                # print(f"... ({next_row},{col_index}):{fit_status}->{brick} [check 1st line of brick]")
        return fit_status

    def add_brick(self, brick:Brick, brick_id:int, row_index: int, col_index: int, title:str="") -> None:
        if not title:
            title = f"input #{brick_id}"
        self.widget_info[brick_id] = (row_index, col_index, brick, title)
        for row_increment in range(brick.height):
            for col_increment in range(self.grid_width - col_index):
                new_col = col_index + col_increment
                new_row = row_index + row_increment
                next_slot = self.rows[new_row][new_col]
                if col_increment < brick.width:
                    next_slot.brick_id = brick_id
                    next_slot.free_cells = 0
                    # print(f"___add brick {brick_id}___({new_row},{new_col})")
                else:
                    next_slot.free_cells = self.update_free_slot_count(new_col)
                    # print("___updating free_slots...")

    def update_free_slot_count(self, col_index:int) -> int:
        return self.grid_width - col_index


class MainWindow(QMainWindow):
    def __init__(self, grid:Grid, excel_rows:list[list[str]]):
        super().__init__()
        self.excel_rows = excel_rows
        self.current_row = len(excel_rows) - 1
        # self.setWindowTitle("Input form")
        layout = QGridLayout()

        # self.DEFAULT_STYLE = "QLineEdit { border: 1px solid gray; }"
        # self.MODIFIED_STYLE = "QLineEdit { border: 2px solid red; }"
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

        self.inputs = []
        for id, (start_row, start_col, brick, title) in grid.widget_info.items():
            row_span, col_span = brick.height, brick.width
            tmp_input: QLineEdit | QTextEdit
            # if row_span < 4:
            #     tmp_input = QLineEdit()
            #     tmp_input.textEdited.connect(self.alert_on_textchange)
            # else:
            #     tmp_input = QTextEdit()
            #     tmp_input.textChanged.connect(self.alert_on_textchange)
            tmp_input = QLineEdit() if row_span < 4 else QTextEdit()
            self.inputs.append(tmp_input)

            tmp_wrapper = QVBoxLayout()
            tmp_wrapper.addWidget(QLabel(title))
            tmp_wrapper.addWidget(tmp_input)
            tmp_wrapper.setSpacing(3)
            layout.addLayout(tmp_wrapper, start_row, start_col, row_span, col_span)
        self.add_signal_to_fire_on_text_change()

        last_id = list(grid.widget_info.keys())[-1]
        last_widget = grid.widget_info[last_id]
        last_row = last_widget[0] + last_widget[2].height
        layout.addWidget(self.first_btn, last_row,0,1,1)
        layout.addWidget(self.prev_btn, last_row,1,1,1)
        layout.addWidget(self.next_btn, last_row,2,1,1)
        layout.addWidget(self.last_btn, last_row,3,1,1)
        last_row += 1
        layout.addWidget(self.new_btn, last_row,0,1,2)
        layout.addWidget(self.clear_btn, last_row,2,1,2)
        last_row += 1
        layout.addWidget(self.submit_btn, last_row,0,1,3)
        layout.addWidget(self.close_btn, last_row,3,1,1)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.update_current_position("last")

    def handle_submit(self):
        ## TODO add request for confirmation (as this could be destructive)
        output = ""
        for i, el in enumerate(self.inputs):
            try:
                output += f"id:{i}='{el.text()}'"
            except AttributeError:
                output += f"id:{i}='{el.toPlainText()}'"
        print(f"Submitted: {output}")

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
        # self.update_input_styles("changed")
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
        # print(f"text changed to: {new_text}")
        print("text changed")

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
        ## TODO add request for confirmation (as this could be destructive)
        self.load_record_into_gui()

    def start_new_record(self) -> None:
        print("new record")
        self.update_title_with_record_number("[new]")

    def update_current_position(self, direction) -> None:
        ## TODO add request for confirmation (as this could be destructive)
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
        # self.load_record_into_gui()
        self.update_input_styles()


def launch_gui(grid:Grid, excel_rows:list[list[str]]) -> None:
    app = QApplication(sys.argv)
    window = MainWindow(grid, excel_rows)
    window.show()
    app.exec()



def main():
    if args.file:
        print(f"processing file: {args.file}")
        file = Path(args.file)
        headers, rows = shared.parse_excel_into_rows(file)
        print(f"no. of rows = {len(rows[0])}")
        max_lengths = [max([len(content) for content in rows[i]]) for i in range(len(rows[0]))]
        layout = [select_brick_by_content_length(length) for length in max_lengths]
        # print(headers)
        # print(max_lengths)
        # print(layout)
        pprint(list(zip(headers, max_lengths, layout)))
        # layout = [BRICK.onetwo, BRICK.onetwo, BRICK.onefour, BRICK.fourfour]
        grid = Grid()
        # pprint(grid.rows)
        for id, brick_enum in enumerate(layout):
            brick = brick_enum.value
            grid.fit_brick(id, brick, headers[id])
            # print(f">>>>>>> Brick {id} just fitted")

        pprint(grid.rows)
        pprint(grid.widget_info)

        launch_gui(grid, rows)

if __name__ == "__main__":
    main()
