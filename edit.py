from dataclasses import dataclass
from turtle import width
import art_cats as shared
import argparse
from pathlib import Path
from pprint import pprint
from enum import Enum, auto

import sys
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QLabel, QLineEdit, QTextEdit, QWidget, QVBoxLayout

parser = argparse.ArgumentParser()

parser.add_argument("--file", "-f", type=str, required=True)
args = parser.parse_args()

@dataclass
class Brick():
    height: int
    width: int

@dataclass
class Slot():
    brick_id: int
    free_slots: int

    def __repr__(self) -> str:
        is_occupied = self.brick_id > -1
        return f"<{f'@{self.brick_id}' if is_occupied else "##" }: {self.free_slots} slot{"s" if self.free_slots > 1 else ""}>"

class BRICK(Enum):
    oneone = Brick(1, 1)
    onetwo = Brick(1, 2)
    onethree = Brick(1, 3)
    onefour = Brick(1, 4)
    twotwo = Brick(2, 2)
    twothree = Brick(2, 3)
    twofour = Brick(2,4)
    threethree = Brick(3, 3)
    threefour = Brick(3, 4)
    fourfour = Brick(4, 4)

class STATUS(Enum):
    occupied = auto()
    toosmall = auto()
    ok = auto()


class Grid():
    def __init__(self, width:int = 4) -> None:
        self.grid_width = width
        self.rows:list[list[Slot]] = []
        self.add_a_row()
        self.bricks_with_coordinates: dict[int,tuple[int, int, Brick]] = {}

    def exceeds_grid_length(self, zero_index:int) -> bool:
        return zero_index + 1 > len(self.rows)

    def is_free(self, id:int) -> bool:
        return id == -1

    def add_a_row(self):
        self.rows.append([Slot(-1, self.grid_width - slot) for slot in range(self.grid_width)])

    def fit_brick(self, brick_id:int, brick:Brick) -> None:
        fit_status:STATUS
        row_index = 0
        while row_index < 10:
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
                                self.add_brick(brick, brick_id, row_index, col_index)
                                return
            row_index += 1
            if self.exceeds_grid_length(row_index):
                self.add_a_row()

    def check_col_fit(self, brick:Brick, current_slot:Slot) -> STATUS:
        if current_slot.brick_id > -1:
            output = STATUS.occupied
        elif current_slot.free_slots < brick.width:
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
                if self.is_free(next_slot.brick_id) and next_slot.free_slots >= brick.width:
                    fit_status = STATUS.ok
                else:
                    fit_status = STATUS.occupied
                # print(f"... ({next_row},{col_index}):{fit_status}->{brick} [check 1st line of brick]")
        return fit_status

    def add_brick(self, brick:Brick, brick_id:int, row_index: int, col_index: int) -> None:
        self.bricks_with_coordinates[brick_id] = (row_index, col_index, brick)
        for row_increment in range(brick.height):
            for col_increment in range(self.grid_width - col_index):
                new_col = col_index + col_increment
                new_row = row_index + row_increment
                next_slot = self.rows[new_row][new_col]
                if col_increment < brick.width:
                    next_slot.brick_id = brick_id
                    next_slot.free_slots = 0
                    # print(f"___add brick {brick_id}___({new_row},{new_col})")
                else:
                    next_slot.free_slots = self.update_free_slot_count(new_col)
                    # print("___updating free_slots...")

    def update_free_slot_count(self, col_index:int) -> int:
        return self.grid_width - col_index


class MainWindow(QMainWindow):
    def __init__(self, grid):
        super().__init__()
        self.setWindowTitle("Input form")
        layout = QGridLayout()

        self.zero = QLineEdit()
        self.one = QLineEdit()
        self.two = QLineEdit()
        self.three = QTextEdit()
        self.data = [self.zero, self.one, self.two, self.three]

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setCheckable(True)
        self.submit_btn.clicked.connect(self.handle_submit)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.handle_close)

        wrapper_0 = QVBoxLayout()
        wrapper_0.addWidget(QLabel("Zero"))
        wrapper_0.addWidget(self.zero)
        # wrapper_0.setContentsMargins(0,0,0,0)
        wrapper_0.setSpacing(3)

        wrapper_1 = QVBoxLayout()
        wrapper_1.addWidget(QLabel("One"))
        wrapper_1.addWidget(self.one)
        wrapper_1.setSpacing(3)

        wrapper_2 = QVBoxLayout()
        wrapper_2.addWidget(QLabel("Two"))
        wrapper_2.addWidget(self.two)
        wrapper_2.setSpacing(3)

        wrapper_3 = QVBoxLayout()
        wrapper_3.addWidget(QLabel("Three"))
        wrapper_3.addWidget(self.three)
        wrapper_3.setSpacing(3)

        layout.addLayout(wrapper_0, 0, 0, 1, 2)
        layout.addLayout(wrapper_1, 0, 2, 1, 2)
        layout.addLayout(wrapper_2, 1, 0, 1, 4)
        layout.addLayout(wrapper_3, 2, 0, 4, 4)
        layout.addWidget(self.submit_btn, 6,1,1,2)
        layout.addWidget(self.close_btn, 6,3,1,1)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def handle_submit(self):
        output = ""
        for i, el in enumerate(self.data):
            try:
                output += f"id:{i}='{el.text()}'"
            except AttributeError:
                output += f"id:{i}='{el.toPlainText()}'"
        print(f"Submitted: {output}")

    def handle_close(self):
        self.close()


def pyside_test(grid:Grid) -> None:
    app = QApplication(sys.argv)
    window = MainWindow(grid)
    window.show()
    app.exec()


def main():
    if args.file:
        print(f"processing file: {args.file}")
        file = Path(args.file)
        rows = shared.parse_excel_into_rows(file)
        # pprint(rows[0])
        # pprint(rows[1])
        print(f"no. of rows = {len(rows[0])}")
        max_lens = [0 for _ in range(len(rows[0]))]
        headers = []
        for num, row in enumerate(rows):
            if num == 0:
                headers = row
                continue
            for i, col in enumerate(row):
                if (latest_len := len(col)) > max_lens[i]:
                    max_lens[i] = latest_len
        print(headers)
        print(max_lens)


        test_layout = [BRICK.onetwo, BRICK.onetwo, BRICK.onefour, BRICK.fourfour]

        grid = Grid()
        pprint(grid.rows)
        for id, brick_enum in enumerate(test_layout):
            brick = brick_enum.value
            grid.fit_brick(id, brick)
            # print(f">>>>>>> Brick {id} just fitted")

        pprint(grid.rows)
        pprint(grid.bricks_with_coordinates)

        pyside_test(grid)

if __name__ == "__main__":
    main()
