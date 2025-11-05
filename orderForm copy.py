"""
Order form for TAY / ART libraries to replace excel-based form.
Contact: Ross Jones, Osney One
"""

import inspect  ## for debugging only
from app import convert as shared
from dataclasses import dataclass
from collections import namedtuple
from typing import Any
import argparse
import datetime
import yaml
from pathlib import Path
from pprint import pprint
from enum import Enum, auto
import sys
import csv
from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
    QGridLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QMessageBox,
    QSizePolicy,
    QTextBrowser,
    QSpacerItem,
    # QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
)
from PySide6.QtCore import (
    Qt,
    QUrl,
    QTimer,
    QEvent,
    Signal,
    QAbstractTableModel,
)
from PySide6.QtGui import (
    QMouseEvent,
    QEnterEvent,
    QDesktopServices,
)
# from PySide6.QtCore import Qt, QUrl, QTimer
# from PySide6.QtGui import QDesktopServices


class COL(Enum):
    @staticmethod
    def _generate_next_value_(count):
        return count

    def __new__(cls, title: str):
        member = object.__new__(cls)
        member._value_ = cls._generate_next_value_(len(cls.__members__))
        member.title = title
        return member

    def __init__(self, title: str):
            self.title = title

    Subject_consultant = "Subject consultant"
    Fund_code = "Fund code"
    Order_type = "Order type"
    Bib_info = "Bibliographic information"
    Creator = "Creator"
    Date = "Publishing date"
    Isbn = "ISBN"
    Library = "Library"
    Location = "Location"
    Item_policy = "Item policy"
    Reporting_code_1 = "Reporting code 1"
    Reporting_code_2 = "Reporting code 2"
    Reporting_code_3 = "Reporting code 3"
    Hold_for = "Hold for"
    Notify = "Notify"
    Additional_info = "Additional order instructions"
    Table_view = (
        "Items added to order (click on one to jump to it if you need to amend)"
    )


combo_lookup = {
  COL.Subject_consultant.name :"Subject_consultant",
  COL.Order_type.name:"Order_type",
  COL.Library.name:"Library",
  COL.Item_policy.name:"Item_policy",
  COL.Reporting_code_1.name:"Reporting_code_1",
  COL.Reporting_code_2.name:"Reporting_code_2",
  COL.Reporting_code_3.name:"Reporting_code_3",
}

shared.settings.out_file = f"one_off_order.{str(datetime.datetime.now())[:19].replace(" ", "_").replace(":", "")}.csv"
# name = f"one_off_order_form.{timestamp}.csv"
shared.settings.help_file = "help_orders.html"
shared.settings.flavour = {
    "title": "order_form",
    "fields_to_clear": [
        COL.Isbn,
        COL.Reporting_code_1,
        COL.Reporting_code_2,
        COL.Reporting_code_3,
        COL.Notify,
        COL.Hold_for,
        COL.Bib_info,
        COL.Additional_info
    ],
    "fields_to_fill": [
        # [COL.sublib, "ARTBL"],
    ],
    "combo_default_text": " >> Choose <<",
    "combo_following_default_text": " (first select ",
    "independent_inputs": [COL.Subject_consultant.name, COL.Order_type.name, COL.Library.name, COL.Item_policy.name, COL.Reporting_code_1.name, COL.Reporting_code_2.name, COL.Reporting_code_3.name],
    "leaders": [COL.Subject_consultant.name,COL.Library.name],
    "followers": [COL.Fund_code.name,COL.Location.name],
    "headers": [member.title for member in COL],
    "required_fields": [COL.Subject_consultant.name, COL.Fund_code.name, COL.Order_type.name, COL.Bib_info.name, COL.Library.name, COL.Location.name, COL.Item_policy.name, COL.Bib_info.name],
    "validate_always": [],
    "validate_if_present": [COL.Isbn.name, COL.Hold_for.name, COL.Notify.name],
    "validation_skip": (COL.Additional_info.name, "*dummy*"),
    "locking_is_enabled": False,
}
shared.settings.flavour["dictByLeader"] = dict(zip(shared.settings.flavour["leaders"], shared.settings.flavour["followers"]))
shared.settings.flavour["dictByFollower"] = dict(zip(shared.settings.flavour["followers"], shared.settings.flavour["leaders"]))

shared.settings.styles = {
    "text_changed": "border: 1px solid red; background-color: white;",
    "labels": "font-weight: bold;",
    "label_active": "color: #7c6241;",
    "label_locked": "color: darkgrey;",
    "input_active": "border: 1px solid lightgrey; background-color: white;",
    "input_locked": "border: 1px solid whitesmoke; background-color: whitesmoke;",
    "combo_dropdown": "QComboBox QAbstractItemView {selection-background-color: #3B82F6; selection-color: white;}",
}

LABELS = {
    "help" : {"show": "Show help", "hide": "Hide help"}
}

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
    ## format: row-column
    oneone = Brick(1, 1)
    onetwo = Brick(1, 2)
    onethree = Brick(1, 3)
    onefour = Brick(1, 4)
    twoone = Brick(2, 1)
    twotwo = Brick(2, 2)
    twothree = Brick(2, 3)
    twofour = Brick(2, 4)
    twosix = Brick(2, 6)
    threeone = Brick(3, 1)
    threetwo = Brick(3, 2)
    threethree = Brick(3, 3)
    threefour = Brick(3, 4)
    fourone = Brick(4, 1)
    fourtwo = Brick(4, 2)
    fourthree = Brick(4, 3)
    fourfour = Brick(4, 4)
    foursix = Brick(4, 6)


brick_lookup = {
    "1:1": BRICK.oneone,
    "1:2": BRICK.onetwo,
    "1:3": BRICK.onethree,
    "1:4": BRICK.onefour,
    "2:1": BRICK.twoone,
    "2:2": BRICK.twotwo,
    "2:3": BRICK.twothree,
    "2:4": BRICK.twofour,
    "2:6": BRICK.twosix,
    "3:1": BRICK.threeone,
    "3:2": BRICK.threetwo,
    "3:3": BRICK.threethree,
    "3:4": BRICK.threefour,
    "4:1": BRICK.fourone,
    "4:2": BRICK.fourtwo,
    "4:3": BRICK.fourthree,
    "4:4": BRICK.fourfour,
    "4:6": BRICK.foursix,
}


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


default_template = (
    ## non-algorithmic version needs to be: [title, brick-type, start-row, start-col, widget-type=line/area/drop]
    (COL.Subject_consultant, "1:2", 0, 0, "combo"),
    (COL.Fund_code, "1:2", 1, 0, "combo"),
    (COL.Order_type, "1:2", 2, 0, "combo"),
    (COL.Bib_info, "2:6", 3, 0, "text"),
    (COL.Creator, "1:2", 7, 0, "line"),
    (COL.Date, "1:2", 7, 2, "line"),
    (COL.Isbn, "1:2", 7, 4, "line"),
    (COL.Library, "1:2", 0, 2, "combo"),
    (COL.Location, "1:2", 1, 2, "combo"),
    (COL.Item_policy, "1:2", 2, 2, "combo"),
    (COL.Reporting_code_1, "1:2", 0, 4, "combo"),
    (COL.Reporting_code_2, "1:2", 1, 4, "combo"),
    (COL.Reporting_code_3, "1:2", 2, 4, "combo"),
    (COL.Hold_for, "1:2", 8, 0, "line"),
    (COL.Notify, "1:2", 9, 0, "line"),
    (COL.Additional_info, "2:4", 8, 2, "text"),
    (COL.Table_view, "4:6", 10, 0, "table"),
)


class Grid:
    def __init__(self, width: int = 6) -> None:
        self.grid_width = width
        self.current_row = 0
        self.rows: list[list[int]] = (
            []
        )  ## each row is a list of brick ids OR -1 to indicate cell is unoccupied
        self.add_a_row()
        ## dict[id: (start_row, start_col, Brick(height, width), title, name, widget-type)]
        self.widget_info: dict[int, tuple[int, int, Brick, str, str, str]] = ({})

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
        self, brick_id: int, brick: Brick, title: str = "", name=""
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
                    self.widget_info[brick_id] = (row_i, col_i, brick, title, name, "")
                    self.current_row = row_i
                    break
            row_i += 1

    def add_bricks_by_template(self, template: tuple) -> None:
        last_brick = template[-1]
        _, lb_brick_type, lb_start_row, _, _ = last_brick
        lb_height = brick_lookup[lb_brick_type].value.height
        max_row = lb_start_row + lb_height
        # print(f"@@@ {lb_height=}, {lb_start_row} -> {max_row=}")
        self.rows = [self.make_row() for _ in range(max_row)]
        for brick_id, (brick_enum, brick_type, start_row, start_col, widget_type) in enumerate(template):
            title = brick_enum.title
            name = brick_enum.name
            brick = brick_lookup[brick_type].value
            self.place_brick_in_grid(brick, brick_id, start_row, start_col)
            self.widget_info[brick_id] = (start_row, start_col, brick, title, name, widget_type)


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
                # print(f">>> {brick_id}: {row_i=}, {col_i=} {self.rows=}")
                self.rows[row_i][col_i] = brick_id


class WindowWithRightTogglePanel(QWidget):
    saved_editor_width = 0
    GRID_BUFFER = 3  # Buffer for layout margins/spacing

    def __init__(self, grid:Grid, rows:list[list[str]], settings:shared.Settings ):
        # print(f"<><><><>init:{headers=}")
        super().__init__()
        self.main_grid = QGridLayout(self)
        self.main_grid.setContentsMargins(0, 0, 0, 0)
        # self.main_grid.setSpacing(3)
        self.main_grid.setSpacing(self.GRID_BUFFER)

        self.EDIT_PANEL_INITIAL_WIDTH = 800
        self.HELP_PANEL_WIDTH = 350

        # --- 1. Main Editor Setup (Column 0, Expanding) ---
        self.edit_panel_widget = Editor(grid, rows, settings.in_file, self, settings)
        self.edit_panel_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # --- 2. Help Panel Setup (Column 1, Fixed Width) ---
        self.help_widget = QTextBrowser()
        ## NB pyside6 does not natively implement internal links in markdown (hence the use of html)
        html_path = Path.cwd() / settings.app_dir / settings.help_file
        html_content = load_text_from_file(str(html_path))
        self.help_widget.setHtml(html_content)
        # self.help_widget.anchorClicked.connect(self.handle_internal_link)
        self.help_widget.anchorClicked.connect(self.handle_link_click)

        self.help_widget.setReadOnly(True)
        self.help_widget.setFixedWidth(self.HELP_PANEL_WIDTH)

        # Add panes to the main grid layout
        self.main_grid.addWidget(self.edit_panel_widget, 0, 0)
        self.main_grid.addWidget(self.help_widget, 0, 1)
        self.saved_height = self.height()

        # Set Column Stretch Factors for the 2-column layout:
        self.main_grid.setColumnStretch(0, 10)  # Editor column (Expands)
        self.main_grid.setColumnStretch(1, 0)  # Help panel column (Fixed)
        self.setLayout(self.main_grid)

        # Initial layout sizing
        self.adjustSize()

        # Capture the correct initial size after layout setup
        self.saved_editor_width = self.edit_panel_widget.width()
        self.centre_window_in_display()

    def centre_window_in_display(self) -> None:
        screen_geometry = QApplication.primaryScreen().geometry()
        window_frame = self.frameGeometry()
        center_point = screen_geometry.center()
        window_frame.moveCenter(center_point)
        self.move(window_frame.topLeft())

    def resizeEvent(self, event):
        """
        Handles manual resizing when the help panel is closed by restoring the
        editor's Expanding policy so it can fill the window.
        """
        super().resizeEvent(event)

        # If the help panel is hidden, the user wants the editor to absorb the resize space.
        if not self.help_widget.isVisible():
            # Check if the policy is currently Fixed (i.e., we need to restore it)
            if (
                self.edit_panel_widget.sizePolicy().horizontalPolicy()
                == QSizePolicy.Policy.Fixed
            ):

                # 1. Restore the Expanding policy
                self.edit_panel_widget.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
                )

                # 2. Remove the fixed width constraint
                self.edit_panel_widget.setFixedWidth(16777215)  # QWIDGETSIZE_MAX

                # 3. Force a layout update to make the editor stretch immediately
                self.layout().invalidate()
                self.update()

    def toggle_help_panel(self):
        """
        Toggles the help panel visibility while managing the editor's size policy
        to achieve the sticky width and correct window resizing on all toggles.
        """
        is_visible = self.help_widget.isVisible()
        self.saved_height = self.height()
        if is_visible:
            # --- Hiding Panel (Shrinking Window) ---
            self.saved_editor_width = self.edit_panel_widget.width()

            # 2. Temporarily set the editor's policy to Fixed and constrain its width
            self.edit_panel_widget.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
            )
            self.edit_panel_widget.setFixedWidth(self.saved_editor_width)

            # 3. Hide the help panel.
            self.help_widget.setVisible(False)

            # 4. Tell the window to adjust to the new minimum size.
            # This is more reliable than self.resize() for layouts.
            self.adjustSize()
            self.resize(self.width(), self.saved_height)

            # 5. Update button text
            self.edit_panel_widget.help_btn.setText(LABELS["help"]["show"])

        else:
            # --- Showing Panel (Expanding Window) ---
            self.saved_editor_width = self.edit_panel_widget.width()
            # 2. Restore the editor's policy to Expanding
            self.edit_panel_widget.setFixedWidth(16777215)
            self.edit_panel_widget.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            self.help_widget.setVisible(True)
            # 4. Calculate the full width needed (New Editor Width + Help Panel Width + buffer)
            new_width = (
                self.saved_editor_width + self.HELP_PANEL_WIDTH + self.GRID_BUFFER
            )
            # self.edit_panel_widget.help_btn.setText("Hide Help Panel")
            self.edit_panel_widget.help_btn.setText(LABELS["help"]["hide"])
            # self.resize(new_width, self.height())
            self.resize(new_width, self.saved_height)

    def handle_internal_link(self, url: QUrl):
        """Scrolls the QTextBrowser to the target anchor within the document."""
        anchor_name = url.toString().split("#")[-1]
        if anchor_name:
            self.help_widget.scrollToAnchor(anchor_name)

    def handle_link_click(self, url: QUrl):
        """
        Custom slot to decide whether to open the link externally
        or let QTextBrowser handle it internally.
        """
        # A URL is considered "external" if it has a non-empty scheme
        # (like 'http', 'https', 'ftp', 'mailto', etc.).
        # Internal anchor links (e.g., "#section") have an empty scheme and no host.
        scheme = url.scheme()
        if scheme in ("http", "https", "mailto", "ftp"):
            # Open external links in the system's default browser
            QDesktopServices.openUrl(url)
            self.help_widget.setSource(QUrl())
            # self.status_label.setText(f"External link opened: {url.toString()}")
        else:
            self.handle_internal_link(url)
            # self.help_widget.setSource(url)
            # self.status_label.setText(f"Internal link/anchor handled: {url.toString()}")


class ClickableLabel(QLabel):
    """
    QLabel subclass: emits signals when clicked and visually reacts to hovering.
    """

    clicked = Signal()

    def __init__(self, text="Click Me", parent=None):
        super().__init__(text, parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.WhatsThisCursor)
        # self.default_style = "text-decoration: none;"
        self.default_style = shared.settings.styles["label_active"]
        self.hover_style = "text-decoration: underline overline;"
        self.pressed_style = "font-style: italic;"
        self.setStyleSheet(self.default_style)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Initialize placeholder for custom property
        self.help_txt = ""

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setStyleSheet(self.pressed_style)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.underMouse():
                self.setStyleSheet(self.hover_style)
            else:
                self.setStyleSheet(self.default_style)
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def enterEvent(self, event: QEnterEvent):
        self.setStyleSheet(self.hover_style)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        self.setStyleSheet(self.default_style)
        super().leaveEvent(event)


class Editor(QWidget):
    widget_lookup = {
        "line": QLineEdit,
        "text": QTextEdit,
        "combo": QComboBox,
        "label": QLabel,
        "table": QTableWidget,
    }
    def __init__(self, grid: Grid, excel_rows: list[list[str]], file_name: str, caller:WindowWithRightTogglePanel, settings:shared.Settings):
        super().__init__()
        self.setWindowTitle("Editor")
        self.setGeometry(100, 100, 1200, 800)

        self.master_layout = QVBoxLayout()
        self.caller = caller
        self.settings = settings
        inputs_layout = QGridLayout()
        nav_grid = QGridLayout()
        self.nav_grouped_layout = QGroupBox("Navigation")

        self.grid = grid
        # self.headers_backup = headers
        self.headers = self.settings.flavour["headers"]
        if excel_rows:
            self.excel_rows = excel_rows
            # self.headers = headers
            self.has_records = True
        else:
            self.excel_rows = [["" for _ in range(len(shared.settings.layout_template))]]
            # self.headers = []
            # self.headers = headers
            self.has_records = False
        # print(f"<><><>{self.headers=}{self.settings.flavour["headers"]}")

        self.file_name = file_name
        self.short_file_name = self.get_filename_only(settings.in_file)
        self.current_row_index = len(excel_rows) - 1
        self.record_is_locked = True
        self.all_text_is_saved = True

        self.add_input_widgets(inputs_layout)
        self.build_nav_buttons(caller, nav_grid)

        self.master_layout.addLayout(inputs_layout)
        self.master_layout.addWidget(self.nav_grouped_layout)
        self.setLayout(self.master_layout)

        self.add_custom_behaviour()
        self.update_title_with_record_number()
        # if self.has_records:
        #     self.load_record_into_gui(self.current_row)
        # else:
        #     self.handle_new_record()
        self.update_nav_buttons()
        self.add_signal_to_fire_on_text_change()


    def add_input_widgets(self, inputs_layout):
        self.labels:list[QLabel] = []
        self.inputs:list[QWidget] = []
        self.follower_inputs:dict[str, QComboBox] = {}
        self.leader_inputs:dict[str, QComboBox] = {}
        self.tableView:QTableWidget
        for id, (start_row, start_col, brick, title, name, widget_type) in self.grid.widget_info.items():
            row_span, col_span = brick.height, brick.width
            # widget_name = make_snake_name(title)
            tmp_input: QWidget = self.widget_lookup[widget_type]()
            tmp_input.setObjectName(name)
            if isinstance(tmp_input, QComboBox):
                # name = make_snake_name(title)
                ## TODO: continue moving derived titles over to 'name'
                if name in self.settings.flavour["followers"]:
                    self.follower_inputs[name] = tmp_input
                elif name in self.settings.flavour["leaders"]:
                    self.leader_inputs[name] = tmp_input
                tmp_input.setStyleSheet(self.settings.styles["combo_dropdown"])
            if isinstance(tmp_input, QTableWidget):
                tmp_input.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
                tmp_input.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
                self.tableView = tmp_input
            else:
                self.inputs.append(tmp_input)

            tmp_wrapper = QVBoxLayout()
            # tmp_label = QLabel(title)
            if name in shared.settings.flavour["required_fields"]:
                title = f"*{title}*"
            # print(f" >>>> {name}-> {title}")
            tmp_label = ClickableLabel(title)
            # tmp_label.help_txt = title.lower().replace(" ", "_")
            tmp_label.help_txt = name
            tmp_label.clicked.connect(lambda checked=False, l=tmp_label: self.show_help_topic(l))
            font = tmp_label.font()
            font.setBold(True)
            tmp_label.setFont(font)
            self.labels.append(tmp_label)

            tmp_wrapper.addWidget(tmp_label)
            tmp_wrapper.addWidget(tmp_input)
            if isinstance(tmp_input, QLineEdit):
                tmp_wrapper.addStretch(1)
            tmp_wrapper.setSpacing(3)
            inputs_layout.addLayout(
                tmp_wrapper, start_row, start_col, row_span, col_span
            )
        ## TODO: work out why HOL_notes does react to changed text!!
        # self.add_signal_to_fire_on_text_change()

    def build_nav_buttons(self, caller, nav_grid):
        self.submit_btn = QPushButton("Save item")
        self.submit_btn.setStyleSheet("font-weight: bold;")
        self.submit_btn.clicked.connect(self.handle_submit)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.handle_close)
        # self.help_btn = QPushButton("Hide Help Panel")
        self.help_btn = QPushButton(LABELS["help"]["hide"])
        self.help_btn.clicked.connect(caller.toggle_help_panel)
        # self.help_btn.clicked.connect(self.window.toggle_help_panel)
        self.load_file_btn = QPushButton("Load file")
        self.load_file_btn.clicked.connect(self.handle_file_dialog)

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
        self.new_btn.clicked.connect(self.handle_new_record)
        self.save_btn = QPushButton("Save")
        # self.save_btn.clicked.connect(self.save_as_csv)
        self.save_btn.setEnabled(False)
        # self.marc_btn = QPushButton("Export as MARC")
        # self.marc_btn.clicked.connect(self.save_as_marc)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.handle_close)
        self.unlock_btn = QPushButton("Unlock")
        if self.settings.flavour["locking_is_enabled"]:
            self.unlock_btn.clicked.connect(self.handle_unlock)
        else:
            self.unlock_btn.setEnabled(False)

        ## Add nav buttons to layout
        last_id = len(grid.widget_info) - 1
        last_widget = grid.widget_info[last_id]
        last_row = last_widget[0] + last_widget[2].height
        ## addWidget(widget, row, column, rowspan, colspan)
        nav_grid.addWidget(self.first_btn, last_row, 0, 1, 1)
        nav_grid.addWidget(self.prev_btn, last_row, 1, 1, 1)
        nav_grid.addWidget(self.next_btn, last_row, 2, 1, 1)
        nav_grid.addWidget(self.last_btn, last_row, 3, 1, 1)
        nav_grid.addWidget(self.unlock_btn, last_row, 4, 1, 1)
        last_row += 1
        nav_grid.addWidget(self.new_btn, last_row, 0, 1, 1)
        nav_grid.addWidget(self.submit_btn, last_row, 1, 1, 2)
        nav_grid.addWidget(self.clear_btn, last_row, 3, 1, 1)
        last_row += 1
        nav_grid.addWidget(self.load_file_btn, last_row, 0, 1, 1)
        nav_grid.addWidget(self.save_btn, last_row, 1, 1, 1)
        # nav_grid.addWidget(self.marc_btn, last_row, 2, 1, 1)
        nav_grid.addWidget(self.close_btn, last_row, 2, 1, 1)
        nav_grid.addWidget(self.help_btn, last_row, 3, 1, 1)
        self.nav_grouped_layout.setLayout(nav_grid)

    def add_custom_behaviour(self) -> None:
        if self.settings.flavour["title"] == "order_form":
            ## set up lists of leaders & followers & populate drop down lists for leaders
            for input_widget in [widget for widget in self.inputs if isinstance(widget, QComboBox)]:
                name = input_widget.objectName()
                if name in self.settings.flavour["independent_inputs"]:
                    # print(f" ======= {name} is independent")
                    raw_options = self.get_raw_combo_options(self.transform_into_yaml_lookup(name))
                    options, _ = self.get_normalized_combo_list(raw_options)
                else:
                    leader_name = self.settings.flavour["dictByFollower"][name]
                    leader_widget = self.leader_inputs[leader_name]
                    # print(f" ======= {name} is a follower -> {leader_name}")
                    leader_widget.currentTextChanged.connect(self.handle_update_follower)
                    source = self.get_combo_options_source(input_widget)
                    raw_options = self.get_raw_combo_options(source)
                    options, _ = self.get_normalized_combo_list(raw_options)
                input_widget.clear()
                input_widget.addItems(options)
                input_widget.setCurrentIndex(0)
            self.load_table(self.tableView, self.excel_rows)


    def handle_update_follower(self) -> None:
        leader:QComboBox = self.sender()
        follower_name = self.settings.flavour["dictByLeader"][leader.objectName()]
        # print(f"%%%  handle_update_follower: {leader.objectName()} -> {follower_name}")
        self.load_combo_box(self.follower_inputs[follower_name])


    def transform_into_yaml_lookup(self, object_name:str) -> str:
        ## transforms the objectName of the widget so that it matches the yaml file
        # name = combo_lookup[object_name]
        # return name
        return object_name


    def get_combo_options_source(self, combo_box:QComboBox) -> str:
        ## TODO: (probably) combine with / call only from get_raw_combo_options()
        name = combo_box.objectName()
        if name in self.settings.flavour["followers"]:
            ## need to get the selected value in leader
            leader_name = self.settings.flavour["dictByFollower"][name]
            leader = self.leader_inputs[leader_name]
            match_for_yaml_lookup = leader.currentText()
            if not match_for_yaml_lookup or match_for_yaml_lookup == self.settings.flavour["combo_default_text"]:
                match_for_yaml_lookup = f"*!*leader:{name}"
        else:
            match_for_yaml_lookup = self.transform_into_yaml_lookup(name)  ## name to match to in yaml file
        # print(f"\tSource = {match_for_yaml_lookup}")
        return match_for_yaml_lookup


    def get_raw_combo_options(self, key:str) -> list:
        if key:
            if key.startswith("*!*"):
                # raw_options = [f" (first select {key.split(":")[1]}) "]
                raw_options = [f"{self.settings.flavour["combo_following_default_text"]}{key.split(":")[1]}) "]
            else:
                options = self.settings.flavour["combo_data"]
                raw_options = options.get(key, [])
        else:
            # raw_options = ["TBA"]
            raw_options = []
        # print(f"\t** get raw combo options: {key=} -> raw_options={raw_options[:2]}... >> {inspect.stack()[1].function}")
        return raw_options


    def get_normalized_combo_list(self, raw_combo_options:list, selected_item="") -> tuple[list[str], int]:
        """
        returns list with default "choose" text if more than one option
        and the index of any selected item or default -1
        """
        default_text = self.settings.flavour["combo_default_text"]
        ## If more than one option, add in instruction to select an option
        option_count = len(raw_combo_options)
        new_combo_options = []
        if option_count == 0:
            print("\t\t-- Combo list missing options!!")
            new_combo_options = ["<missing data>"]
            index = 0
        elif option_count == 1:
            ## if only one option, select it
            new_combo_options = raw_combo_options
            index = 0
        else:
            ## if several options, add in an instruction to choose one
            new_combo_options = [default_text, *raw_combo_options]
            if selected_item == default_text:
                selected_item = ""
            if selected_item:
                try:
                    # index_in_list = new_combo_options.index(selected_item)
                    index = new_combo_options.index(selected_item)
                except ValueError:
                    print(f"The option *{selected_item}* is not an item in this combo box!")
                    index = 0
            else:
                # the default index if no selection
                index = 0
        # print(f"\tget normalized combo list: {len(new_combo_options)}, {selected_item=}->{index=}, {new_combo_options[:2]}...\n")
        return (new_combo_options, index)


    def highlight_row_by_index(self, table_widget:QTableWidget, row_index: int):
            """
            Highlights the entire row in the QTableWidget.
            Args: row_index: The zero-based index of the row to highlight.
            """
            table_widget.clearSelection()
            # SelectionBehavior=SelectRows, so any col highlights the whole row (here, col 0 for convenience).
            table_widget.setCurrentCell(row_index, 0)
            # table_widget.scrollToItem(self.table_widget.item(row_index, 0))


    def show_help_topic(self, sender_label: ClickableLabel):
        """Slot runs when label is clicked, accessing custom property."""
        link = sender_label.help_txt
        self.caller.handle_internal_link(QUrl(f"#{link}"))
        # self.display.setText(link)
        print(f"--- the link is: #{link}")

    @property
    def row_count(self) -> int:
        return len(self.excel_rows)

    @property
    def column_count(self) -> int:
        return len(self.excel_rows[0])

    @property
    def current_record_is_new(self) -> int:
        return self.current_row_index == -1

    @property
    def record_count(self) -> int:
        return len(self.excel_rows)

    @property
    def index_of_last_record(self) -> int:
        return self.record_count - 1

    @property
    def current_row(self) -> list:
        return self.excel_rows[self.current_row_index]

    @current_row.setter
    def current_row(self, row:list) -> None:
        self.excel_rows[self.current_row_index] = row

    def handle_submit(self, optional_msg="") -> bool:
        """
        Gather data from form & save it to file
        """
        if not optional_msg:
            optional_msg = ""
        data = []
        data_are_valid = self.data_is_valid(optional_msg)
        # print(f">>>>>>>>>> {data_are_valid=}")
        if not data_are_valid:
            return False
        # print("OK... data passes as valid for submission...")
        for input_widget in self.inputs:
            # data.append(self.get_input_data(input_widget))
            data.append(self.get_content(input_widget))
        if self.current_record_is_new:
            # print(f"***{self.has_records=}, record count: {self.record_count} {data=}")
            if self.has_records:
                self.excel_rows.append(data)
            else:
                self.excel_rows = [data]
                # self.headers = []
                # self.headers = self.headers_backup
                self.has_records = True
            self.current_row_index = self.index_of_last_record
            self.update_title_with_record_number()
        else:
            ## Update existing record
            self.current_row = data
        self.save_as_csv(self.settings.out_file)
        self.update_nav_buttons()
        self.load_record_into_gui(self.current_row)
        return True

    def data_is_valid(self, optional_msg="") -> bool:
        missing = []
        invalid = []
        errors = []
        msg = optional_msg
        # errors = []
        # barcode = self.inputs[COL.barcode.value].text().strip()
        # if barcode == "*dummy*":
        #     return True
        rules = self.settings.flavour
        skip_validation_field, skip_validation_text = rules["validation_skip"]
        if skip_validation_field == skip_validation_text:
            return True
        for widget in self.inputs:
            name = widget.objectName()
            # print(f"....{name} in {rules["required_fields"]}-> {name in rules['required_fields']}")
            if name in rules["required_fields"]:
                if not self.get_content(widget):
                    missing.append(name)
                    continue
            if name in rules["validate_always"] or name in rules["validate_if_present"]:
                if (error_msg := self.validate_input(widget)) :
                    invalid.append(f"{name}: {error_msg}")
            # elif name in rules["validate_if_present"]:
            #     if (error_msg := self.validate_input(widget)) :
            #         invalid.append(f"{name}: {error_msg}")
        if missing:
            errors.append(f"The following fields are missing: {', '.join(missing)}")
        if invalid:
            errors.append(f"Please correct the following problem(s): {'; '.join(invalid)}")
        msg = "\n".join(errors)
        if msg:
            alert = QMessageBox()
            alert.setText(msg)
            alert.exec()
            return False
        print(f"%%% {msg}")
        return True

    def validate_input(self, widget:QWidget) -> str:
        ## Valid = empty string
        # error_msg = ""
        match widget.objectName():
            case "hold_for" | "notify":
                uni_number = self.get_content(widget)
                if uni_number and (len(uni_number) != 7 or int(uni_number[0]) in [1, 3, 6, 7]):
                    return "This is not a valid University number."
            case "isbn":
                isbn = self.get_content(widget)
                if 10 > len(isbn) > 13:
                    return "The ISBN is not valid."
        return ""


    def get_content(self, widget:QWidget) -> str:
        content = ""
        if isinstance(widget, QLineEdit):
            content = widget.text()
        elif isinstance(widget, QTextEdit):
            content = widget.toPlainText()
        elif isinstance(widget, QComboBox):
            content = widget.currentText()
            if content == self.settings.flavour["combo_default_text"] or content.startswith(self.settings.flavour["combo_following_default_text"]):
                content = ""
        else:
            msg = f"No reader set up for {widget}!"
            print(msg)
            # logging.critical(msg)
        return content.strip()

    def handle_close(self) -> None:
        # self.close()
        app.quit()

    def go_to_first_record(self) -> None:
        self.update_current_position("first")

    def go_to_last_record(self) -> None:
        self.update_current_position("last")

    def go_to_previous_record(self) -> None:
        self.update_current_position("back")

    def go_to_next_record(self) -> None:
        self.update_current_position("forwards")

    def go_to_record_number(self, record_number:int) -> None:
        self.update_current_position("exact", record_number)

    def update_current_position(self, direction, record_number=-1) -> None:
        # print(f">>>{self.record_count=}, {self.current_row_index=}, {self.current_record_is_new=}, {self.has_records=} {self.all_text_is_saved=}")
        if not self.all_text_is_saved and self.choose_to_abort_on_unsaved_text():
            return
        # index_of_last_record = len(self.excel_rows) - 1
        match direction:
            case "first":
                self.current_row_index = 0
            case "last":
                self.current_row_index = self.index_of_last_record
            case "back":
                if self.current_row_index > 0:
                    self.current_row_index -= 1
            case "exact" if record_number >=0:
                if record_number < self.column_count:
                    self.current_row_index = record_number
            case _:
                if self.current_row_index < self.index_of_last_record:
                    self.current_row_index += 1
        # msg = str(self.current_row)
        msg = self.get_human_readable_record_number()
        msg += self.update_nav_buttons()
        self.update_title_with_record_number(msg)
        # self.load_record_into_gui(self.excel_rows[self.current_row_index])
        self.load_record_into_gui(self.current_row)
        # self.all_text_is_saved = True


    def update_title_with_record_number(self, prefix="Record no. "):
        text = f"{self.get_human_readable_record_number()} of {self.record_count}"
        # status = " **locked**" if self.record_is_locked else " (editable)"
        if self.settings.flavour["locking_is_enabled"]:
            if self.record_is_locked:
                status = " **locked**"
            else:
                status =" (editable)"
        else:
            status = ""
        # print(f"title >>> {self.record_is_locked=}, {status}")
        # self.caller.setWindowTitle(f"<file: {self.settings.in_file}.new.csv>: {prefix}{text}{status}")
        if self.has_records:
            # file = self.settings.in_file
            file = self.settings.out_file
        else:
            file = "*unsaved*"
        self.caller.setWindowTitle(f"FILE: {file} -- {prefix}{text}{status}")
        # self.update_input_styles()

    def add_signal_to_fire_on_text_change(self):
        # for input in self.inputs:
        for i, input in enumerate(self.inputs):
            # print(f">>>> {self.labels[i].text()} {input=}")
            if isinstance(input, QLineEdit):
                input.textEdited.connect(self.handle_text_change)
            elif isinstance(input, QTextEdit):
                input.textChanged.connect(self.handle_text_change)
            elif isinstance(input, QComboBox):
                input.currentTextChanged.connect(self.handle_text_change)


    def handle_text_change(self) -> None:
        # print(f"Text changed...{datetime.datetime.now()}")
        sender = self.sender()
        style = "text_changed"
        if isinstance(sender, QLineEdit):
            sender.setStyleSheet(self.settings.styles[style])
            sender.textEdited.disconnect(self.handle_text_change)
        elif isinstance(sender, QTextEdit):
            sender.setStyleSheet(self.settings.styles[style])
            sender.textChanged.disconnect(self.handle_text_change)
        elif isinstance(sender, QComboBox):
            sender.setStyleSheet(self.settings.styles[style])
            sender.currentTextChanged.disconnect(self.handle_text_change)
        else:
            print("Huston, we have a problem with text input...")
        self.all_text_is_saved = False


    def load_record_into_gui(self, row_to_load:list | None=None) -> None:
        """
        Iterate through input boxes:
        if there is a record (i.e. row in list) then populate with this
        else fill with default (usually empty string)
        NB. the order of the inputs in self.inputs matches the column order
        ...but the display order does not necessarily match
        """
        # need_to_load_table = True
        for col_i, input_widget in enumerate(self.inputs):
            cell_contents = "" if not row_to_load else row_to_load[col_i]
            self.load_record(input_widget, cell_contents)
            input_widget.setStyleSheet(self.settings.styles["input_active"])
        self.load_table(self.tableView, self.excel_rows, self.headers)
        self.highlight_row_by_index(self.tableView, self.current_row_index)
        self.add_signal_to_fire_on_text_change()
        mode = "lock" if row_to_load else "edit"
        self.toggle_record_editable(mode)
        self.update_title_with_record_number()
        # print(f">>>>>{mode=}, {row_to_load=} {self.has_records=}, {self.headers}")
        self.all_text_is_saved = True

    def clear_form(self) -> None:
        if not self.current_record_is_new and self.abort_on_clearing_existing_record(
            self
        ):
            return
        self.load_record_into_gui()
        # self.toggle_record_editable("edit")

    def handle_new_record(self) -> None:
        ## TODO: should i add in a routine to save the previous record here?
        self.current_row_index = -1
        if self.settings.flavour["title"] == "order_form":
            for field in self.settings.flavour["fields_to_clear"]:
                input_widget = self.inputs[field.value]
                self.load_record(input_widget, "")
        self.all_text_is_saved = True
        self.toggle_record_editable("edit")
        self.update_title_with_record_number()

    def load_record(self, input_widget:QWidget, value:Any, options=[]) -> None:
        # caller = inspect.stack()[1].function
        # print(f"++++++ [load rec] {input_widget.objectName()}: <{input_widget.__class__.__name__}> {value=}, {caller=}")
        if isinstance(input_widget, QComboBox):
            self.load_combo_box(input_widget, value)
        elif isinstance(input_widget, QLineEdit):
            self.load_line_edit(input_widget, value)
        elif isinstance(input_widget, QTextEdit):
            self.load_text_edit(input_widget, value)
        # elif isinstance(input_widget, QTableWidget):
        #     ## the entire table is loaded from scratch, not just a single value, as for others
        #     self.load_table(input_widget, value)
        else:
            print(f"!!!! Problem: current widget ({type(input_widget)})")

    def load_combo_box(self, combo_box:QComboBox, value="") -> None:
        """
        The list of options is populated from the baseName() value
        If a record exists, a value is passed which is rendered as the correct display index
        otherwise, the default of -1 is set as the index
        """
        source = self.get_combo_options_source(combo_box)
        raw_options = self.get_raw_combo_options(source)
        options, index = self.get_normalized_combo_list(raw_options, value)
        # print(f"load_combo_box {combo_box.objectName()} >>> {match_for_yaml_lookup=}: {value=}, {index=}, {options[:2]=}...\n")
        combo_box.clear()
        combo_box.addItems(options)
        combo_box.setCurrentIndex(index)

    def load_table(self, table:QTableWidget, rows:list[list], headers=[]) -> None:
        # print(f"   === {rows=}, {headers=}")
        # if not rows or rows == [[]]:
        # if not rows:
        table.setEnabled(True)
        if not headers:
            headers = self.headers
        if not self.has_records:
            # headers = ["empty"]
            # rows = [["no order items added yet"]]
            rows = [["" for _ in headers]]
            # rows[0][0] = "no order items added yet"
            table.setSpan(0,0,0, len(self.headers))
            table.setItem(0,0, QTableWidgetItem("no order items added yet"))
            table.setEnabled(False)
        # elif rows and not headers:
            # headers = self.headers
        # table.setSpan(0,0,0, len(self.headers))
        table.setColumnCount(len(rows[0]))
        table.setRowCount(len(rows))
        # print(f"<><>{self.headers=}")
        if headers:
            table.setHorizontalHeaderLabels(headers)
        if self.has_records:
            for row_i, row in enumerate(rows):
                for col_i, column in enumerate(row):
                    table.setItem(row_i, col_i, QTableWidgetItem(column))
                table.setRowHeight(row_i, 30)
        table.cellClicked.connect(self.pass_table_row_index)
        table.setMinimumHeight(200)

    def pass_table_row_index(self, row, column) -> None:
        # print(f"$$$$$$$$$ {row=}, {column=}")
        self.highlight_row_by_index(self.tableView, row)
        self.go_to_record_number(row)

    def load_line_edit(self, input_widget:QLineEdit, value="") -> None:
        input_widget.setText(value)

    def load_text_edit(self, input_widget:QTextEdit, value="") -> None:
        # self.inputs[input_widget.value].setText(value)
        input_widget.setPlainText(value)


    def handle_unlock(self) -> None:
        # print(f"... handling unlock (currently {self.record_is_locked=})")
        if self.record_is_locked:
            self.toggle_record_editable("edit")
        else:
            if not self.handle_submit("Only completed records can be locked.\n\n"):
                return
            self.toggle_record_editable("lock")

    def toggle_record_editable(self, mode="edit") -> None:
        if not self.settings.flavour["locking_is_enabled"]:
            return
        Option = namedtuple("Option", ["label_style", "input_style", "locked_status", "btn_text"])
        css = self.settings.styles
        if mode == "edit":
            status = Option(
                label_style=css["label_active"],
                input_style=css["input_active"],
                locked_status=False,
                btn_text="Lock")
            self.record_is_locked = False
        else:
            status = Option(
                label_style=css["label_locked"],
                input_style=css["input_locked"],
                locked_status=True,
                btn_text="Edit")
            self.record_is_locked = True
        for label in self.labels:
            label.setStyleSheet(status.label_style)
        for input in self.inputs:
            input.setStyleSheet(status.input_style)
            input.setEnabled(not status.locked_status)
        self.unlock_btn.setText(status.btn_text)
        self.submit_btn.setEnabled(not status.locked_status)

    def update_nav_buttons(self) -> str:
        # print(f"nav status: {self.record_count=}")
        msg = ""
        if self.record_count == 1:
            self.first_btn.setEnabled(False)
            self.prev_btn.setEnabled(False)
            self.last_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
        elif self.current_row_index == 0:
            msg += " (first)"
            self.first_btn.setEnabled(False)
            self.prev_btn.setEnabled(False)
            self.last_btn.setEnabled(True)
            self.next_btn.setEnabled(True)
        elif self.current_row_index == self.index_of_last_record:
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
        return msg

    def get_human_readable_record_number(self, number=-100):
        if number == -100:
            number = self.current_row_index
        if number == -1:
            out = "[new]"
        else:
            out = str(number + 1)
        return out

    def save_as_csv(self, file_name="") -> None:
        # is_backup_file = bool(file_name)
        headers = [el[3] for el in self.grid.widget_info.values()]
        # write_to_csv(self.settings.out_file, self.excel_rows, headers)
        write_to_csv(file_name, self.excel_rows, headers)
        self.all_text_is_saved = True
        # print(f"*** records saved as {self.settings.out_file}")

    def choose_to_abort_on_unsaved_text(self) -> int:
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

    def handle_file_dialog(self):
        """Opens the native file selection dialog and processes the result."""
        if not self.all_text_is_saved and self.choose_to_abort_on_unsaved_text():
            # print(f"&&&&&&&&& Should abort!")
            return
        file_dialog = QFileDialog()
        # This returns a tuple: (file_path, filter_used)
        file_path, _ = file_dialog.getOpenFileName(
            parent=self,  # The parent widget (for centering)
            caption="Select a file.",
            # dir="./excel_files",
            dir=f"./{self.settings.data_dir}",
            filter="Database Files (*.xls *.xlsx *.xlsm *.csv *.tsv)",
        )
        if file_path:
            # self.short_file_name = self.get_filename_only(file_path)
            self.settings.in_file_full = file_path
            self.settings.in_file = self.get_filename_only(file_path)
            self.settings.out_file = self.settings.in_file
            print(f"File Selected: {self.settings.in_file} ({file_path})")
            self.headers, self.excel_rows = shared.parse_file_into_rows(Path(file_path))
            if not self.settings.use_default_layout:
                print("Haven't coded for non-default layout yet!")
                ## TODO: code for change of layout on file loading (i.e. make a standalone: 'load file and update grid' function)
            print(f"\n** file dialog -> records: {len(self.excel_rows)}")
            self.all_text_is_saved = True
            self.has_records = True
            # self.update_current_position("last")
            self.go_to_last_record()
            shared.logger.info(f"Just opened {file_path} containing {self.record_count} records.")
        else:
            print("Selection cancelled.")

    def get_filename_only(self, file_path: str) -> str:
        if name_start_index := file_path.rfind("/") + 1:
            file_name = file_path[name_start_index:]
        else:
            file_name = file_path
        return file_name


    def drop_csv_suffix(self, name:str) -> str:
        file_name = name.split(".")
        index = 0
        for el in reversed(file_name):
            if el in ["csv", "tsv", "new"]:
                index -= 1
                continue
            break
        out = ".".join(file_name[:index])
        return out

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


def create_max_lengths(rows: list[list[str]]) -> list[int]:
    max_lengths: list[list[int]] = [[] for _ in rows[0]]
    for row in rows:
        for i, col in enumerate(row):
            max_lengths[i].append(len(col))
    return [max(col) for col in max_lengths]


def write_to_csv(file_name: str, data: list[list[str]], headers: list[str]) -> None:
    out_file = Path(shared.settings.output_dir) / Path(file_name)
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(headers)
        csvwriter.writerows(data)


def load_text_from_file(file_name: str) -> str:
    """Reads the content of the specified file, returning a default message on error."""
    path = Path(file_name)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except IOError as e:
            return f"<h1>Error loading help content!</h1><p>Could not read file: {path}. Error: {e}</p>"
    else:
        return f"<h1>Help File Not Found</h1><p>Please create a file named '<b>{file_name}</b>' in the current directory.</p>"


def read_cli_into_settings() -> None:
    parser = argparse.ArgumentParser()

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
    shared.settings.in_file = args.file
    if file := args.file:
        shared.settings.in_file = file
    else:
        shared.settings.is_existing_file = False
        shared.settings.in_file = shared.settings.default_output_filename
    shared.settings.layout_template = default_template


def save_as_yaml(file:str, data) -> None:
    with open(file, mode="wt", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False)

def open_yaml_file(file:str):
  with open(file, mode="rt", encoding="utf-8") as f:
    return yaml.safe_load(f)


def make_snake_name(text:str):
    return text.lower().replace(" ", "_")

def get_settings():
    read_cli_into_settings()
    grid = Grid()
    headers = []
    if shared.settings.is_existing_file:
        print(f"processing file: {shared.settings.in_file}")
        headers, rows = shared.parse_file_into_rows(Path(shared.settings.in_file))
        if shared.settings.use_default_layout:
            grid.add_bricks_by_template(shared.settings.layout_template)
        else:
            headers = shared.settings.flavour["headers"]
            max_lengths = create_max_lengths(rows)
            layout = [select_brick_by_content_length(length) for length in max_lengths]
            for id, brick_enum in enumerate(layout):
                brick = brick_enum.value
                grid.add_brick_algorithmically(id, brick, headers[id])
    else:
        print("creating new file")
        # rows = [["" for _ in range(len(template))]]
        rows = []
        # template = shared.settings.layout_template
        # grid.add_bricks_by_template(template)
        grid.add_bricks_by_template(shared.settings.layout_template)
    # if shared.settings.out_file:
    #     drop_csv_suffix(self.settings.out_file)
    # else:
    #     name = self.settings.default_output_filename
    return (grid, rows, headers)


if __name__ == "__main__":
    shared.settings.flavour["combo_data"] = open_yaml_file("./app/bodleian.yaml")
    # print(info)
    grid, rows, headers = get_settings()
    app = QApplication(sys.argv)
#     app.setStyleSheet(
#         """QComboBox QAbstractItemView {
#     selection-background-color: #3B82F6;
#     selection-color: white;
# } """)
    print(f"headers: {headers}")
    window = WindowWithRightTogglePanel(grid, rows, shared.settings)
    window.show()
    sys.exit(app.exec())
