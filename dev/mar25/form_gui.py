"""
Common resources
"""

import logging
from tkinter import W
import pprint

from . import log_setup


from enum import Enum, EnumType
from .settings import Default_settings
from . import marc_21
from . import validation
from . import io
from . import logic

# import argparse
from datetime import datetime

# import yaml
import sys

# import csv
from enum import Enum, auto
from dataclasses import dataclass, fields
from collections import namedtuple
from typing import Any
from pathlib import Path

from pprint import pprint
from PySide6.QtWidgets import (
    QApplication,
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
    QSizePolicy,
    QTextBrowser,
    QCheckBox,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QHBoxLayout,
    QSpinBox,
    QFrame,
    # QSpacerItem,
)
from PySide6.QtCore import (
    Qt,
    QUrl,
    # QTimer,
    QEvent,
    Signal,
    QObject,
)
from PySide6.QtGui import (
    QMouseEvent,
    QEnterEvent,
    QDesktopServices,
    QFont,
)

# from art_cats import settings
# from . import io
# from art_cats import settings

logger = logging.getLogger(__name__)


@dataclass
class Brick:
    height: int
    width: int
    # role: str


@dataclass
class Cell:
    brick_id: int
    free_down: int
    free_across: int

    def __repr__(self) -> str:
        is_occupied = self.brick_id > -1
        return f"<{f'@{self.brick_id}' if is_occupied else "##"}> 1 else " "}>"


# def select_brick_by_content_length(length: int) -> (BRICK, widget-type):
def select_brick_by_content_length(length: int) -> tuple[Brick, str]:
    if length < 50:
        # return BRICK.oneone
        return (Brick(1, 1), "line")
    elif length < 100:
        # return BRICK.onetwo
        return (Brick(1, 2), "line")
    elif length < 400:
        # return BRICK.twotwo
        return (Brick(2, 2), "text")
    else:
        # return BRICK.fourtwo
        return (Brick(4, 2), "text")


class STATUS(Enum):
    occupied = auto()
    toosmall = auto()
    ok = auto()


class Grid:
    def __init__(self, width: int = 6) -> None:
        self.grid_width = width
        self.current_row = 0
        ## each row is a list of brick ids OR -1 to indicate cell is unoccupied
        self.rows: list[list[int]] = []
        self.add_a_row()
        ## dict[id: (start_row, start_col, Brick(height, width), title, name, widget-type)]
        self.widget_info: dict[int, tuple[int, int, Brick, str, str, str]] = {}

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
        self, brick_id: int, brick: Brick, title="", name="", widget_type=""
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
            logger.info("Input field has been truncated to fit the grid.")
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
                    self.widget_info[brick_id] = (
                        row_i,
                        col_i,
                        brick,
                        title,
                        name,
                        widget_type,
                    )
                    self.current_row = row_i
                    break
            row_i += 1

    def add_bricks_by_template(self, template: list) -> None:
        # print(f"add bricks by template: {template=}")
        last_brick = template[-1]
        _, (lb_height, lb_length), lb_start_row, _, _ = last_brick
        # lb_height = brick_lookup[lb_brick_type].value.height
        max_row = lb_start_row + lb_height
        # print(f"@@@ {lb_height=}, {lb_start_row} -> {max_row=}")
        self.rows = [self.make_row() for _ in range(max_row)]
        for brick_id, (
            brick_enum,
            # brick_type,
            (brick_height, brick_length),
            start_row,
            start_col,
            widget_type,
        ) in enumerate(template):
            title = brick_enum.display_title
            name = brick_enum.name
            # brick = brick_lookup[brick_type].value
            brick = Brick(brick_height, brick_length)
            self.place_brick_in_grid(brick, brick_id, start_row, start_col)
            self.widget_info[brick_id] = (
                start_row,
                start_col,
                brick,
                title,
                name,
                widget_type,
            )

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


class WindowWithRightTogglePanel(QWidget):
    saved_editor_width = 0
    GRID_BUFFER = 3  # Buffer for layout margins/spacing

    def __init__(
        self,
        grid: Grid,
        rows: list[list[str]],
        settings: Default_settings,
        headers: list[str],
        COL: Enum,
        app,
    ):
        super().__init__()

        self.COL = COL
        self.settings = settings
        self.main_grid = QGridLayout(self)
        self.main_grid.setContentsMargins(0, 0, 0, 0)
        # self.main_grid.setSpacing(3)
        self.main_grid.setSpacing(self.GRID_BUFFER)

        self.EDIT_PANEL_INITIAL_WIDTH = 800
        self.HELP_PANEL_WIDTH = 350

        # --- 1. Main Editor Setup (Column 0, Expanding) ---
        self.edit_panel_widget = Editor(grid, rows, self, settings, headers, COL, app)
        self.edit_panel_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # --- 2. Help Panel Setup (Column 1, Fixed Width) ---
        self.help_widget = QTextBrowser()
        ## NB pyside6 does not natively implement internal links in markdown (hence the use of html)
        html_path = Path.cwd() / settings.files.app_dir / settings.files.help_file
        html_content = io.load_plaintext_from_file(str(html_path))
        self.help_widget.setHtml(html_content)
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
                self.layout().invalidate()  # type: ignore
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
            # self.edit_panel_widget.help_btn.setText(LABELS["help"]["show"])
            self.edit_panel_widget.help_btn.setText(self.settings.labels.show_help)

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
            self.edit_panel_widget.help_btn.setText(self.settings.labels.hide_help)
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


class ClickableLabel(QLabel):
    """
    QLabel subclass: emits signals when clicked and visually reacts to hovering.
    """

    clicked = Signal()

    def __init__(self, settings, text="Click Me", parent=None):
        super().__init__(text, parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.WhatsThisCursor)
        # self.default_style = "text-decoration: none;"
        self.default_style = settings.styles.label_active
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
        "checkbox": QCheckBox,
    }

    # def __init__(self, grid: Grid, excel_rows: list[list[str]], file_name: str, caller:WindowWithRightTogglePanel, settings:Settings, COL, app):
    def __init__(
        self,
        grid: Grid,
        excel_rows: list[list[str]],
        caller: WindowWithRightTogglePanel,
        settings: Default_settings,
        headers: list[str],
        COL,
        app,
    ):
        super().__init__()
        self.setWindowTitle("Editor")
        self.setGeometry(100, 100, 1200, 800)

        self.data = logic.Data()

        self.master_layout = QVBoxLayout()
        self.caller = caller
        self.settings = settings
        inputs_layout = QGridLayout()

        # self.container = QFrame()
        # self.container.setObjectName("myContainer") # ID for targeted CSS
        # self.container.setStyleSheet("#myContainer { background-color: #2c3e50; border-radius: 10px; }")

        # nav_grid = QGridLayout(self.container)
        nav_grid = QGridLayout()
        self.nav_grouped_layout = QGroupBox("Navigation")

        self.app = app
        self.COL = COL
        self.grid = grid

        ## Set up record information
        self.data.headers = headers
        if excel_rows:
            self.data.excel_rows = excel_rows
            self.data.has_records = True
        else:
            self.data.excel_rows = [["" for _ in range(len(settings.layout_template))]]
            self.data.has_records = False

        self.data.file_name = settings.files.in_file
        self.data.current_row_index = len(excel_rows) - 1
        self.data.record_is_locked = True
        self.data.all_text_is_saved = True

        self.add_input_widgets(inputs_layout)
        self.build_nav_buttons(caller, nav_grid)

        self.master_layout.addLayout(inputs_layout)
        self.master_layout.addWidget(self.nav_grouped_layout)
        # self.master_layout.addWidget(self.container)
        self.setLayout(self.master_layout)

        self.customize_fields()
        if self.data.has_records:
            self.load_record_into_gui(self.data.current_row)
        else:
            self.load_record_into_gui()
        self.update_title_with_record_number()
        self.update_nav_buttons()
        self.add_signal_to_fire_on_text_change()

    def add_input_widgets(self, inputs_layout):
        self.labels: list[QLabel] = []
        self.inputs: list[QWidget] = []
        self.follower_inputs: dict[str, QComboBox] = {}
        self.leader_inputs: dict[str, QComboBox] = {}
        for id, (
            start_row,
            start_col,
            brick,
            title,
            name,
            widget_type,
        ) in self.grid.widget_info.items():
            row_span, col_span = brick.height, brick.width
            tmp_input: QWidget = self.widget_lookup[widget_type]()
            tmp_input.setObjectName(name)
            if isinstance(tmp_input, QComboBox):
                if name in self.settings.combos.followers:
                    self.follower_inputs[name] = tmp_input
                elif name in self.settings.combos.leaders:
                    self.leader_inputs[name] = tmp_input
                tmp_input.setStyleSheet(self.settings.styles.combo_dropdown)
            self.update_input_styling(tmp_input, "input_active")
            self.inputs.append(tmp_input)

            tmp_wrapper = QVBoxLayout()
            if name in self.settings.validation.required_fields:
                title = f"* {title}"
            if (
                self.settings.auto_submit_form_on_x_field
                and name.lower() == self.settings.auto_submit_form_field_name.lower()
                and isinstance(tmp_input, QLineEdit)
            ):
                # print("Adding submit on barcode connection...")
                # tmp_input.textEdited.connect(self.choose_to_save_on_barcode)
                tmp_input.editingFinished.connect(self.choose_to_save_on_barcode)
                self.settings.auto_submit_form_field = tmp_input
            # print(f" >>>> {name}-> {title}")
            tmp_label = ClickableLabel(self.settings, title)
            tmp_label.help_txt = name
            tmp_label.clicked.connect(
                lambda checked=False, l=tmp_label: self.show_help_topic(l)
            )
            font = tmp_label.font()
            font.setBold(True)
            tmp_label.setFont(font)
            self.labels.append(tmp_label)

            tmp_wrapper.addWidget(tmp_label)
            tmp_wrapper.addWidget(tmp_input)
            if isinstance(tmp_input, QLineEdit):
                tmp_wrapper.addStretch(1)
            tmp_wrapper.setSpacing(3)
            if row_span > 1 or col_span > 1:
                layout_params = (tmp_wrapper, start_row, start_col, row_span, col_span)
            else:
                layout_params = (tmp_wrapper, start_row, start_col)
            inputs_layout.addLayout(*layout_params)

        ## TODO: work out why HOL_notes does react to changed text!!
        # self.add_signal_to_fire_on_text_change()

    def build_nav_buttons(self, caller, nav_grid):
        if self.settings.show_table_view:
            self.tableView = QTableWidget()
            self.tableView.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectRows
            )
            self.tableView.setSelectionMode(
                QAbstractItemView.SelectionMode.SingleSelection
            )
            # self.tableView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) #
            # self.tableView.setMinimumHeight(250)  #
            tmp_label = QLabel(
                "Items added to order (click on one to jump to it if you need to amend)"
            )
            table_wrapper = QVBoxLayout()
            table_wrapper.addWidget(tmp_label)
            table_wrapper.addWidget(self.tableView)

        self.submit_btn = QPushButton("Save item")
        self.submit_btn.setStyleSheet("font-weight: bold;")
        self.submit_btn.clicked.connect(self.handle_submit)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.handle_close)
        # self.help_btn = QPushButton("Hide Help Panel")
        # self.help_btn = QPushButton(LABELS["help"]["hide"])
        self.help_btn = QPushButton(self.settings.labels.hide_help)
        self.help_btn.clicked.connect(caller.toggle_help_panel)
        # self.help_btn.clicked.connect(self.window.toggle_help_panel)
        self.load_file_btn = QPushButton("Load file")
        self.load_file_btn.clicked.connect(self.handle_open_new_file)

        self.first_btn = QPushButton("First")
        self.first_btn.clicked.connect(self.go_to_first_record)
        self.last_btn = QPushButton("Last")
        self.last_btn.clicked.connect(self.go_to_last_record)
        self.prev_btn = QPushButton("<")
        self.prev_btn.clicked.connect(self.go_to_previous_record)
        self.next_btn = QPushButton(">")
        self.next_btn.clicked.connect(self.go_to_next_record)
        self.clear_btn = QPushButton("Clear")
        # self.clear_btn.setStyleSheet("color: red;")
        self.clear_btn.clicked.connect(self.handle_clear_form)
        self.new_btn = QPushButton("New")
        self.new_btn.clicked.connect(self.handle_create_new_record)
        # self.save_btn = QPushButton("Save")
        # self.save_btn.clicked.connect(self.save_as_csv)
        # self.save_btn.setEnabled(False)
        # self.marc_btn = QPushButton("Export as MARC")
        # self.marc_btn.clicked.connect(self.save_as_marc)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.handle_close)
        self.unlock_btn = QPushButton("Unlock")
        if self.settings.locking_is_enabled:
            self.unlock_btn.clicked.connect(self.handle_unlock)
        else:
            self.unlock_btn.setEnabled(False)

        ## Add nav buttons to layout
        last_id = len(self.grid.widget_info) - 1
        last_widget = self.grid.widget_info[last_id]
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
        # nav_grid.addWidget(self.save_btn, last_row, 1, 1, 1)
        nav_grid.addWidget(self.close_btn, last_row, 2, 1, 1)
        nav_grid.addWidget(self.help_btn, last_row, 3, 1, 1)
        if self.settings.show_marc_button:
            self.marc_btn = QPushButton("Export as MARC")
            # self.marc_btn.clicked.connect(self.save_as_marc)
            self.marc_btn.clicked.connect(self.handle_marc_files)
            self.marc_btn.setEnabled(False)
            nav_grid.addWidget(self.marc_btn, last_row, 1, 1, 1)
        # else:
        if self.settings.show_table_view:
            last_row += 1
            nav_grid.addWidget(self.tableView, last_row, 0, 1, 6)
        self.nav_grouped_layout.setLayout(nav_grid)

    def customize_fields(self) -> None:
        ## ** CUSTOMISED BEHAVIOUR GOES HERE
        if self.settings.title == "art_cats":
            sale_dates = self.inputs[self.COL.sale_dates.value]
            if isinstance(sale_dates, QLineEdit):
                sale_dates.editingFinished.connect(self.saledates_action)
            for label in self.labels:
                if "transliteration" in label.text():
                    font = label.font()
                    font.setBold(False)
                    font.setItalic(True)
                    label.setFont(font)

        # elif self.settings.title == "order_form":
        if self.settings.combos.leaders:
            self.setup_combo_boxes()
            self.load_table(self.tableView, self.data.excel_rows)

    def setup_combo_boxes(self) -> None:
        ## set up lists of leaders & followers & populate drop down lists for leaders
        for input_widget in self.inputs:
            if isinstance(input_widget, QComboBox):
                name = input_widget.objectName()
                if name in self.settings.combos.independents:
                    # print(f" ======= {name} is independent")
                    raw_options = self.get_raw_combo_options(
                        self.transform_into_yaml_lookup(name)
                    )
                    options, _ = self.get_normalized_combo_list(
                        input_widget.objectName(), raw_options
                    )
                else:
                    leader_name = self.settings.combos.dict_by_follower[name]
                    leader_widget = self.leader_inputs[leader_name]
                    # print(f" ======= {name} is a follower -> {leader_name}")
                    leader_widget.currentTextChanged.connect(
                        self.handle_update_follower
                    )
                    source = self.get_combo_options_source(input_widget)
                    raw_options = self.get_raw_combo_options(source)
                    options, _ = self.get_normalized_combo_list(
                        input_widget.objectName(), raw_options
                    )
                input_widget.clear()
                input_widget.addItems(options)
                input_widget.setCurrentIndex(0)

    def handle_update_follower(self) -> None:
        # leader: QComboBox = self.sender()
        leader: QObject = self.sender()
        follower_name = self.settings.combos.dict_by_leader[leader.objectName()]
        self.load_combo_box(self.follower_inputs[follower_name])

    def transform_into_yaml_lookup(self, object_name: str) -> str:
        ## transforms the objectName of the widget so that it matches the yaml file
        # name = combo_lookup[object_name]
        # return name
        return object_name

    def get_combo_options_source(self, combo_box: QComboBox) -> str:
        ## TODO: (probably) combine with / call only from get_raw_combo_options()
        name = combo_box.objectName()
        if name in self.settings.combos.followers:
            ## need to get the selected value in leader
            leader_name = self.settings.combos.dict_by_follower[name]
            leader = self.leader_inputs[leader_name]
            match_for_yaml_lookup = leader.currentText()
            if (
                not match_for_yaml_lookup
                or match_for_yaml_lookup == self.settings.combos.default_text
            ):
                match_for_yaml_lookup = f"*!*leader:{name}"
        else:
            match_for_yaml_lookup = self.transform_into_yaml_lookup(
                name
            )  ## name to match to in yaml file
        # print(f"\tSource = {match_for_yaml_lookup}")
        return match_for_yaml_lookup

    def get_raw_combo_options(self, key: str) -> list:
        if key:
            if key.startswith("*!*"):
                # raw_options = [f" (first select {key.split(":")[1]}) "]
                raw_options = [
                    f"{self.settings.combos.following_default_text}{key.split(":")[1]}) "
                ]
                # raw_options = [f"{self.settings.flavour["combo_following_default_text"]}{key.split(":")[1]}) "]
            else:
                options = self.settings.combos.data
                raw_options = options.get(key, [])
        else:
            # raw_options = ["TBA"]
            raw_options = []
        # print(f"\t** get raw combo options: {key=} -> raw_options={raw_options[:2]}... >> {inspect.stack()[1].function}")
        return raw_options

    def get_normalized_combo_list(
        self, combo_name: str, raw_combo_options: list, selected_item=""
    ) -> tuple[list[str], int]:
        """
        returns list with default "choose" text if more than one option
        and the index of any selected item or default -1
        """
        default_text = self.settings.combos.default_text
        ## If more than one option, add in instruction to select an option
        option_count = len(raw_combo_options)
        new_combo_options = []
        if option_count == 0:
            logger.warning("\t\t-- Combo list missing options!!")
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
            # print(f">>> 1: {selected_item=}, {type(selected_item)}")
            # if isinstance(selected_item, bool):
            #     selected_item = "True" if selected_item else "False"
            # print(f">>> 2: {selected_item=}, {type(selected_item)}")
            if selected_item:
                try:
                    index = new_combo_options.index(selected_item)
                    ## Case-insensitive index search for transitional data using True/TRUE
                    # index = next(
                    #     (
                    #         i
                    #         for i, x in enumerate(new_combo_options)
                    #         if x.lower() == selected_item.lower()
                    #     ),
                    #     None,
                    # )
                except ValueError:
                    logger.warning(
                        f"The option *{selected_item}* is not an item in the combo box '{combo_name}'!"
                    )
                    index = 0
            else:
                # the default index if no selection
                index = 0
        # print(f"\tget normalized combo list: {len(new_combo_options)}, {selected_item=}->{index=}, {new_combo_options[:2]}...\n")
        return (new_combo_options, index)

    def highlight_row_by_index(self, table_widget: QTableWidget, row_index: int):
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
        # print(f"--- the link is: #{link}")

    def handle_submit(self, optional_msg="") -> bool:
        """
        Gather data from form & save it to file
        """
        # print(f"\tCHECKETY-CHECK2:{self.settings.file_newly_created=}")
        self.settings.file_newly_created = False
        authorised_to_continue = logic.gatekeeper("submit", self)
        if authorised_to_continue:
            csv_file = io.get_csv_file_name_and_path(self.settings)
            headers = [el[3] for el in self.grid.widget_info.values()]
            print(f"handle_submit:\n{headers}\n{self.data.headers}")
            io.write_to_csv(csv_file, self.data.excel_rows, headers)
            io.write_data_to_excel(
                [headers, *self.data.excel_rows], csv_file.with_suffix(".xlsx")
            )
            self.data.all_text_is_saved = True
            self.update_nav_buttons()
            self.load_record_into_gui(self.data.current_row)
            if self.settings.show_marc_button:
                self.marc_btn.setEnabled(True)
            self.submit_btn.setEnabled(False)
        return authorised_to_continue

    def highlight_fields(self, field_names: list[str]) -> None:
        for input in self.inputs:
            if input.objectName() in field_names:
                self.update_input_styling(input, "validation_error")

    def get_all_inputs(self) -> tuple[dict, bool]:
        record_as_dict = {}
        is_empty = True
        # is_dummy = False
        for input in self.inputs:
            name = input.objectName()
            value = self.get_content(input)
            record_as_dict[name] = value
            ## ** ignore auto-fill fields when checking if record is empty
            if (
                value
                and not isinstance(input, QCheckBox)
                # and name not in self.settings.validation.fields_to_autofill
            ):
                is_empty = False
        return (record_as_dict, is_empty)

    def show_alert_box(self, msg: str) -> None:
        alert = QMessageBox()
        alert.setText(msg)
        alert.exec()

    def get_content(self, widget: QWidget) -> str:
        content = ""
        match widget:
            case QLineEdit():
                content = widget.text()
            case QTextEdit():
                content = widget.toPlainText()
            case QComboBox():
                content = widget.currentText()
                if content == self.settings.combos.default_text or content.startswith(
                    self.settings.combos.following_default_text
                ):
                    content = ""
            case QCheckBox():
                content = "True" if widget.isChecked() else "False"
            case _:
                msg = f"No reader set up for {widget}!"
                logger.critical(msg)
        return content.strip()

    def handle_close(self) -> None:
        authorised_to_continue = logic.gatekeeper("close", self)
        if not authorised_to_continue:
            return
        # self.close()
        self.app.quit()

    def go_to_first_record(self) -> None:
        self.update_current_position("first")

    def go_to_last_record(self) -> None:
        self.update_current_position("last")

    def go_to_previous_record(self) -> None:
        self.update_current_position("back")

    def go_to_next_record(self) -> None:
        self.update_current_position("forwards")

    def go_to_record_number(self, record_number: int) -> None:
        self.update_current_position("exact", record_number)

    def update_current_position(self, direction, record_number=-1) -> None:
        # print(f">>>{self.record_count=}, {self.current_row_index=}, {self.current_record_is_new=}, {self.has_records=} {self.all_text_is_saved=}")
        authorised_to_continue = logic.gatekeeper("jump", self)
        if not authorised_to_continue:
            return
        # index_of_last_record = len(self.excel_rows) - 1
        match direction:
            case "first":
                self.data.current_row_index = 0
            case "last":
                self.data.current_row_index = self.data.index_of_last_record
            case "back":
                if self.data.current_row_index > 0:
                    self.data.current_row_index -= 1
            case "exact" if record_number >= 0:
                if record_number < self.data.column_count:
                    self.data.current_row_index = record_number
            case _:
                if self.data.current_row_index < self.data.index_of_last_record:
                    self.data.current_row_index += 1
        msg = logic.get_human_readable_record_number(self.data.current_row_index)
        msg += self.update_nav_buttons()
        self.update_title_with_record_number(msg)
        # self.load_record_into_gui(self.excel_rows[self.current_row_index])
        self.load_record_into_gui(self.data.current_row)
        # self.all_text_is_saved = True

    def saledates_action(self) -> None:
        # print("sales_date filled in!!")
        sender = self.sender()
        # sender = self.inputs[COL.sale_dates.value]
        pubdate = self.inputs[self.COL.pub_year.value]
        if isinstance(sender, QLineEdit) and isinstance(pubdate, QLineEdit):
            if not pubdate.text():
                year_of_pub = sender.text().strip()[:4]
                # print(f">>>>>>>>> {year_of_pub}")
                pubdate.setText(f"{year_of_pub}?")
        else:
            logger.warning("Can't access salecode or pubdate fields...")

    def update_title_with_record_number(self, prefix="Record no. ") -> None:
        # text = f"{self.get_human_readable_record_number()} of {self.data.record_count}"
        text = f"{logic.get_human_readable_record_number(self.data.current_row_index)} of {self.data.record_count}"
        if self.settings.locking_is_enabled:
            if self.data.record_is_locked:
                status = "locked"
            else:
                status = "editable"
            status = f"          [{status}]"
        else:
            status = ""
        # print(f"title >>> {self.record_is_locked=}, {status}")
        if self.data.has_records:
            file = self.settings.files.out_file
        else:
            file = "*unsaved*"
        # status_line = f"FILE: {file} -- {prefix}{text}{status}"
        status_line = f"{prefix}{text} in {file}{status}"
        self.caller.setWindowTitle(status_line)
        # print(f"{status_line=}")

    def add_signal_to_fire_on_text_change(self):
        # for input in self.inputs:
        for i, input in enumerate(self.inputs):
            # print(f">>>> {self.label
            # s[i].text()} {input=}")
            match input:
                case QLineEdit():
                    input.textEdited.connect(self.handle_text_change)
                case QTextEdit():
                    input.textChanged.connect(self.handle_text_change)
                case QComboBox():
                    input.currentTextChanged.connect(self.handle_text_change)
                case QCheckBox():
                    input.checkStateChanged.connect(self.handle_text_change)

    def handle_text_change(self) -> None:
        # print(f"Text changed...{datetime.datetime.now()}")
        sender: QObject = self.sender()
        style = "text_changed"
        match sender:
            case QLineEdit():
                sender.textEdited.disconnect(self.handle_text_change)
            case QTextEdit():
                sender.textChanged.disconnect(self.handle_text_change)
            case QComboBox():
                sender.currentTextChanged.disconnect(self.handle_text_change)
            case QCheckBox():
                sender.checkStateChanged.disconnect(self.handle_text_change)
            case _:
                logger.warning("Huston, we have a problem with text input...")
        self.update_input_styling(sender, style)
        self.data.all_text_is_saved = False
        self.data.form_has_been_cleared = False
        self.submit_btn.setEnabled(True)

    def update_input_styling(self, widget: QObject, style_name: str) -> None:
        style = getattr(self.settings.styles, style_name)
        # print(f"Text changed for {widget.objectName()} to '{style_name}' <{style}>")
        match widget:
            case QLineEdit():
                widget.setStyleSheet(style)
            case QTextEdit():
                widget.setStyleSheet(style)
            case QComboBox():
                widget.setStyleSheet(style)
            case QCheckBox():
                ## styling overwrites the check itself!
                # if style_name == "text_changed":
                #     style = getattr(self.settings.styles, "text_changed_checkbox")
                # else:
                #     style = getattr(self.settings.styles, "border_only_active")
                #     # style = "border_only_active"
                # widget.setStyleSheet(style)
                pass
            case _:
                logger.warning("Huston, we have a problem with input styling")

    def load_record_into_gui(self, row_to_load: list | None = None) -> None:
        """
        Iterate through input boxes:
        if there is a record (i.e. row in list) then populate with this
        else fill with default (usually empty string)
        NB. the order of the inputs in self.inputs matches the column order
        ...but the display order does not necessarily match
        """
        # print(f"load_record_into_gui: {row_to_load=}, {len(self.data.excel_rows)=} & {self.settings.column_names}")
        for col_i, input_widget in enumerate(self.inputs):
            # print(f"{col_i=}")
            # TODO: if keeping 'autofill' functionality, need to add in autofill fields here...
            cell_contents = "" if not row_to_load else row_to_load[col_i]
            # print(f"{input_widget.objectName()=} -> {cell_contents}")
            self.load_record(input_widget, cell_contents)
            self.update_input_styling(input_widget, "input_active")
        self.add_signal_to_fire_on_text_change()
        if self.settings.show_table_view:
            self.load_table(self.tableView, self.data.excel_rows, self.data.headers)
            self.highlight_row_by_index(self.tableView, self.data.current_row_index)
        mode = "lock" if row_to_load else "edit"
        self.toggle_record_editable(mode)
        self.update_title_with_record_number()
        if self.settings.show_marc_button and self.marc_btn and self.data.has_records:
            self.marc_btn.setEnabled(True)
        # print(f">>>>>{mode=}, {row_to_load=} {self.has_records=}, {self.headers}")
        self.data.all_text_is_saved = True

    def handle_clear_form(self) -> None:
        authorised_to_continue = logic.gatekeeper("clear", self)
        if not authorised_to_continue:
            return
        self.data.form_has_been_cleared = True
        self.load_record_into_gui()
        self.data.form_has_been_cleared = True
        self.data.all_text_is_saved = False
        # self.toggle_record_editable("edit")

    def handle_create_new_record(self) -> None:
        authorised_to_continue = logic.gatekeeper("new", self)
        if not authorised_to_continue:
            return
        self.data.current_row_index = -1

        if (
            self.settings.validation.clear_all_fields
            and not self.settings.validation.fields_to_clear
        ):
            fields_to_clear = self.COL
        else:
            fields_to_clear = self.settings.validation.fields_to_clear
        for field in fields_to_clear:
            input_widget = self.inputs[field.value]
            self.load_record(input_widget, "")
        self.data.all_text_is_saved = True
        self.toggle_record_editable("edit")
        self.update_title_with_record_number()

    def load_record(self, input_widget: QWidget, value: Any, options=[]) -> None:
        if (
            not value
            and input_widget.objectName() in self.settings.validation.fields_to_autofill
        ):
            value = self.settings.validation.fields_to_autofill_info[
                input_widget.objectName()
            ]
        match input_widget:
            case QComboBox():
                self.load_combo_box(input_widget, value)
            case QLineEdit():
                self.load_line_edit(input_widget, value)
            case QTextEdit():
                self.load_text_edit(input_widget, value)
            case QCheckBox():
                self.load_checkbox(input_widget, value)
            # elif isinstance(input_widget, QTableWidget):
            #     ## the entire table is loaded from scratch, not just a single value, as for others
            #     self.load_table(input_widget, value)
            case _:
                logger.warning(f"!!!! Problem: current widget ({type(input_widget)})")

    def load_checkbox(self, widget: QCheckBox, value="") -> None:
        if value == "True" or value == True:
            state = True
        else:
            state = False
        widget.setChecked(state)
        # print(f"+++++++{widget.objectName} {value=} -> {state=} [{widget.checkState()=}]")

    def load_combo_box(self, combo_box: QComboBox, value="") -> None:
        """
        The list of options is populated from the baseName() value
        If a record exists, a value is passed which is rendered as the correct display index
        otherwise, the default of -1 is set as the index
        """
        source = self.get_combo_options_source(combo_box)
        raw_options = self.get_raw_combo_options(source)
        options, index = self.get_normalized_combo_list(
            combo_box.objectName(), raw_options, value
        )
        # print(f"load_combo_box {combo_box.objectName()} >>> {match_for_yaml_lookup=}: {value=}, {index=}, {options[:2]=}...\n")
        combo_box.clear()
        combo_box.addItems(options)
        combo_box.setCurrentIndex(index)

    def load_table(self, table: QTableWidget, rows: list[list], headers=[]) -> None:
        table.setEnabled(True)
        if not headers:
            headers = self.data.headers
        if not self.data.has_records:
            rows = [["" for _ in headers]]
            table.setEnabled(False)
        table.setColumnCount(len(rows[0]))
        table.setRowCount(len(rows))
        if headers:
            table.setHorizontalHeaderLabels(headers)
        if self.data.has_records:
            for row_i, row in enumerate(rows):
                for col_i, column in enumerate(row):
                    table.setItem(row_i, col_i, QTableWidgetItem(column))
                table.setRowHeight(row_i, 30)
        else:
            table.setSpan(0, 0, 1, len(self.data.headers))
            empty_cell = QTableWidgetItem("no order items added yet")
            table.setItem(0, 0, empty_cell)
        table.cellClicked.connect(self.pass_table_row_index)
        row_count = max(2, min(len(rows), 5))
        row_height = 30  # or whatever you use for row height
        table.setMinimumHeight(
            row_count * row_height + table.horizontalHeader().height()
        )
        table.setMaximumHeight(
            row_count * row_height + table.horizontalHeader().height()
        )

    def pass_table_row_index(self, row, column) -> None:
        self.highlight_row_by_index(self.tableView, row)
        self.go_to_record_number(row)

    def load_line_edit(self, input_widget: QLineEdit, value="") -> None:
        input_widget.setText(value)

    def load_text_edit(self, input_widget: QTextEdit, value="") -> None:
        input_widget.setPlainText(value)

    def handle_unlock(self) -> None:
        # print(f"... handling unlock (currently {self.record_is_locked=})")
        if self.data.record_is_locked:
            ## ** a record can always be unlocked
            self.toggle_record_editable("edit")
        else:
            authorised_to_continue = logic.gatekeeper("lock", self)
            if not authorised_to_continue:
                return
            self.toggle_record_editable("lock")

    def toggle_record_editable(self, mode="edit") -> None:
        # print(f"\tCHECKETY-CHECK1:{self.settings.file_newly_created=}")
        if not self.settings.locking_is_enabled or self.settings.file_newly_created:
            return
        Option = namedtuple(
            "Option", ["label_style", "input_style", "locked_status", "btn_text"]
        )
        css = self.settings.styles
        if mode == "edit":
            status = Option(
                label_style=css.label_active,
                input_style=css.input_active,
                locked_status=False,
                btn_text="Lock",
            )
            self.data.record_is_locked = False
        else:
            status = Option(
                label_style=css.label_locked,
                input_style=css.input_locked,
                locked_status=True,
                btn_text="Edit",
            )
            self.data.record_is_locked = True
        for label in self.labels:
            label.setStyleSheet(status.label_style)
        for input in self.inputs:
            match input:
                case QCheckBox() | QComboBox():
                    input.setEnabled(not status.locked_status)
                case QLineEdit() | QTextEdit():
                    input.setStyleSheet(status.input_style)
                    input.setReadOnly(status.locked_status)
                case _:
                    logger.warning("Widget type {input} isn't fully supported.")
        self.unlock_btn.setText(status.btn_text)
        can_save = (
            not status.locked_status and
            not self.data.all_text_is_saved
        )
        self.submit_btn.setEnabled(can_save)
        # self.submit_btn.setEnabled(not status.locked_status)
        self.clear_btn.setEnabled(not status.locked_status)
        button_text_override = "" if status.locked_status else "color: red;"
        self.clear_btn.setStyleSheet(button_text_override)
        self.update_title_with_record_number()

    def update_nav_buttons(self) -> str:
        # print(f"nav status: {self.record_count=}")
        msg = ""
        if self.data.record_count == 1:
            self.first_btn.setEnabled(False)
            self.prev_btn.setEnabled(False)
            self.last_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
        elif self.data.current_row_index == 0:
            msg += " (first)"
            self.first_btn.setEnabled(False)
            self.prev_btn.setEnabled(False)
            self.last_btn.setEnabled(True)
            self.next_btn.setEnabled(True)
        elif self.data.current_row_index == self.data.index_of_last_record:
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

    def handle_marc_files(self) -> None:
        authorised_to_continue = logic.gatekeeper("marc", self)
        if not authorised_to_continue:
            return
        file_name_with_path = (
            self.settings.files.full_output_dir / self.settings.files.out_file
        )
        rows_to_export = logic.remove_dummy_rows(
            self.data.excel_rows, self.settings, self.COL
        )
        rows_to_export = logic.remove_empty_rows(
            rows_to_export, self.settings, self.COL
        )
        rows_in_marc_format = logic.format_list_for_marc(rows_to_export, self.settings)
        files_successfully_created = marc_21.save_as_marc_files(
            self.data,
            rows_in_marc_format,
            file_name_with_path,
            self.settings,
        )
        if files_successfully_created:
            msg = f'The {len(rows_to_export)} records in "{self.settings.files.in_file}" have been successfully saved as "{file_name_with_path.stem}.mrk" in *{self.settings.files.full_output_dir}*.'
        else:
            msg = "Not all files were successfully created."
        logger.info(msg)
        msg_box = QMessageBox()
        msg_box.setText(msg)
        msg_box.exec()

    def choose_to_save_on_barcode(self) -> None:
        if (
            self.data.record_is_locked
            or self.is_modal_open()
            or validation.barcode(
                "barcode", self.get_content(self.settings.auto_submit_form_field)
            )
        ):
            print(
                f"Auto-submit on {self.settings.auto_submit_form_field_name} suppressed."
            )
        else:

            authorised_to_continue = logic.gatekeeper("barcode", self)
            if authorised_to_continue:
                dialogue = DialogueOkCancel(
                    self,
                    "Are you sure you want to save this record?",
                )
                if dialogue.exec() == 1:
                    self.handle_submit()

    def choose_to_abort_on_unsaved_text(self) -> int:
        """
        abort (i.e. treat text as unsaved)  = False
        continue (i.e. treat text as saved) = True
        """
        # print("unsaved text alert...", s)
        dialogue = DialogueOkCancel(
            self,
            "There is unsaved text in this record. Are you OK to contine and lose this text?",
        )
        continue_because_saved = dialogue.exec() == 1
        abort_because_unsaved = not continue_because_saved
        return abort_because_unsaved
        # return dialogue.exec() != 1

    def abort_on_clearing_existing_record(self, s) -> int:
        # print("unsaved text alert...", s)
        dialogue = DialogueOkCancel(
            self,
            # "If you save this record now, it will be deleted. If you simply navigate away or close the app, the record will remain as it was before you cleared the form.",
            "If you clear this record and save it, it will be deleted. If you navigate away without saving, the record will not be cleared.",
            # "This wipes the existing record when you save it. Are you OK to contine and lose this text?",
        )
        return dialogue.exec() != 1

    def handle_open_new_file(self):
        """Opens the native file selection dialog and processes the result."""
        authorised_to_continue = logic.gatekeeper("discard", self)
        if not authorised_to_continue:
            return
        file_dialog = QFileDialog()
        # This returns a tuple: (file_path, filter_used)
        file, _ = file_dialog.getOpenFileName(
            parent=self,  # The parent widget (for centering)
            caption="Select a file.",
            dir=f"./{self.settings.files.data_dir}",
            filter="Database Files (*.xls *.xlsx *.xlsm *.csv *.tsv)",
        )
        if file:
            file_path = Path(file)
            logger.info(f"File Selected: {self.settings.files.in_file} ({file_path})")
            tmp_headers, tmp_excel_rows = io.parse_file_into_rows(
                Path(file_path), self.settings.first_row_is_header
            )
            if logic.is_expected_filetype(tmp_headers, self.COL):
                self.data.headers = tmp_headers
                self.data.excel_rows = tmp_excel_rows
                self.settings.files.in_file = file_path.name
                self.settings.files.out_file = io.get_base_filename(file_path)
            else:
                msg = f"This template expects {len(self.COL)} fields, \nbut {file_path.name} has {len(tmp_headers)}. \nPlease try with another file."
                self.show_alert_box(msg)
                logger.error(msg)
                return

            if not self.settings.use_default_layout:
                logger.warning("Haven't coded for non-default layout yet!")
            logger.info(
                f"\n** file dialog -> records loaded: {len(self.data.excel_rows)}"
            )
            self.data.all_text_is_saved = True
            self.data.has_records = True
            if self.settings.show_marc_button:
                self.marc_btn.setEnabled(True)
            self.go_to_last_record()
            logger.info(
                f"Just opened {file_path} containing {self.data.record_count} records."
            )
        else:
            print("File selection cancelled.")
            logger.warning("File selection cancelled.")

    def is_modal_open(self):
        active_window = QApplication.activeModalWidget()
        # Or check activeWindow() if activeModalWidget() is None
        if active_window:
            return True
        return False


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


class LauncherDialog(QDialog):
    def __init__(self, directory: str, file_patterns: list[str]):
        super().__init__()
        self.directory = directory
        self.setWindowTitle("Project Starter")
        self.setFixedSize(350, 250)

        # Data to be retrieved
        self.selected_path: str = ""  # None
        self.column_count: int = 0  # None
        self.pattern_name: str = ""  # file_patterns

        main_layout = QVBoxLayout(self)

        # --- Section 1: Open Existing ---
        self.btn_open = QPushButton("Open Existing Data File")
        self.btn_open.clicked.connect(lambda: self.handle_open_file(self.directory))
        main_layout.addWidget(self.btn_open)

        main_layout.addWidget(QLabel("OR", alignment=Qt.AlignmentFlag.AlignCenter))

        # --- Section 2: Create new from columns ---
        select_columns_layout = QHBoxLayout()
        select_columns_layout.addWidget(QLabel("New File Columns:"))
        self.spin_columns = QSpinBox()
        self.spin_columns.setRange(1, 50)
        self.spin_columns.setValue(10)  # Default
        select_columns_layout.addWidget(self.spin_columns)

        self.btn_cols_create = QPushButton("Create New")
        self.btn_cols_create.clicked.connect(self.handle_new_columns)
        select_columns_layout.addWidget(self.btn_cols_create)
        main_layout.addLayout(select_columns_layout)

        main_layout.addWidget(QLabel("OR", alignment=Qt.AlignmentFlag.AlignCenter))

        # --- Section 3: Create new from pattern ---
        select_pattern_layout = QHBoxLayout()
        select_pattern_layout.addWidget(QLabel("Existing Patterns:"))
        self.pattern_combo = QComboBox(self)
        self.pattern_combo.addItems(file_patterns)
        select_pattern_layout.addWidget(self.pattern_combo)

        self.btn_pattern_create = QPushButton("Create New")
        self.btn_pattern_create.clicked.connect(self.handle_new_pattern)
        select_pattern_layout.addWidget(self.btn_pattern_create)
        main_layout.addLayout(select_pattern_layout)

    def handle_open_file(self, directory: str):
        # file_filter = "Data Files (*.csv *.tsv *.xlsx *.xls *.xlsm)"
        file_filter = (
            "Data Files (*.csv *.tsv *.xlsx *.xls *.xlsm);;"
            "Excel Files (*.xlsx *.xls *.xlsm);;"
            "Text Tables (*.csv *.tsv);;"
            "All Files (*.*)"
        )
        # path, _ = QFileDialog.getOpenFileName(self, "Select File", "", file_filter)
        path, _ = QFileDialog.getOpenFileName(
            self, "Select File", dir=directory, filter=file_filter
        )
        if path:
            self.selected_path = path
            self.accept()  # Closes dialog with 'Accepted' result

    def handle_new_columns(self) -> None:
        self.column_count = self.spin_columns.value()
        self.accept()

    def handle_new_pattern(self) -> None:
        self.pattern_name = self.pattern_combo.currentText()
        self.accept()


def create_max_lengths(rows: list[list[str]]) -> list[int]:
    """
    Given a spreadsheet (i.e. list of rows, i.e. list[list[str]])
    return the maximum number of characters of any row in each column.
    Used to decide the size of input boxes in algorithmically generated layouts.
    """
    max_lengths: list[list[int]] = [[] for _ in rows[0]]
    for row in rows:
        for i, col in enumerate(row):
            length_of_content = 10 if not col else len(col)
            # max_lengths[i].append(len(col))
            max_lengths[i].append(length_of_content)
    return [max(col) for col in max_lengths]


## TODO: if this functionality is needed: write a separate wrapper file around this file to inject cli parameters
# def read_cli_into_settings(settings: Default_settings) -> None:
#     parser = argparse.ArgumentParser()

#     parser.add_argument(
#         "--file",
#         "-f",
#         type=str,
#         required=False,
#         help="file to edit",
#     )
#     # parser.add_argument(
#     #     "--out",
#     #     "-o",
#     #     type=str,
#     #     required=False,
#     #     help="name to give saved file",)
#     args = parser.parse_args()
#     settings.files.in_file = args.file
#     if file := args.file:
#         settings.files.in_file = file
#         settings.is_existing_file = True
#     else:
#         settings.files.in_file = settings.files.out_file
#         settings.is_existing_file = False
#     # settings.layout_template = default_template


def create_dynamic_enum(
    class_name: str, internal_names: list[str], display_labels: list[str]
) -> Enum:
    # 1. Define the logic in a plain object mixin (NOT an Enum yet)
    class MemberMixin:
        _value_: str
        display_title: str

        def __new__(cls, value, display_title):
            member = object.__new__(cls)
            member._value_ = value
            member.display_title = display_title
            return member

    # 2. Build the members dictionary: { 'name': (value, label) }
    members = {
        n: (i, l.strip())
        for i, (n, l) in enumerate(zip(internal_names, display_labels))
    }

    # 3. Use the functional API with explicit inheritance
    # By passing (MemberMixin, Enum) as the bases, we force the
    # unpacking logic to be active during member creation.
    return Enum(
        value=class_name,
        names=members,
        module=__name__,
        type=MemberMixin,  # In some 3.13 builds, this is the key
    )


# def analyse_existing_file(settings: Default_settings, grid:Grid, COL):
def get_existing_file(settings: Default_settings, COL):
    logging.info(f"processing file: {settings.files.in_file}")
    headers, rows = io.parse_file_into_rows(
        Path(settings.files.in_file), settings.first_row_is_header
    )
    settings.files.out_file = f"{Path(settings.files.in_file).stem}.new"
    pattern_name = get_identity_of_file_pattern(settings, headers)
    # logger.info(f"{10*"*"}\nMatches: {pattern_name or "...nowt..."}\n{10*"*"}")
    logger.info(f"{10*"*"} Matches: {pattern_name or "...nowt... "} {10*"*"}\n")
    if pattern_name:
        ## *NAMED PATTERN i.e. it recognises the file
        _, cols, headers = settings.known_types[pattern_name]
        COL = update_settings_and_columns(settings, pattern_name, headers, cols)
        grid = get_grid_from_pattern(settings, pattern_name, COL)
        # data_report = validation.check_records_on_load(settings, settings.column_names, rows)
    else:
        ## *UNKNOWN PATTERN i.e. it doesn't recognise the file
        COL = update_settings_and_columns(settings, "default", headers)
        grid = get_grid_from_algorithm(settings, rows, headers)

        # print(f"{col_names=}\n\tHeader count matches cols?: {len(headers)==len(col_names)}")
        # show_col(COL)
        # print("**Layout:**")
        # pprint(layout)
        # pprint(grid.rows)
    return (headers, rows, grid, COL)


def update_settings_and_columns(
    settings: Default_settings,
    pattern_name,
    headers: list[str],
    cols: None | list[str] = None,
) -> Enum:
    if not cols:
        col_names = [f"col{i}" for i, _ in enumerate(headers)]
    else:
        col_names = [col[0].lower() for col in cols]
    COL = create_dynamic_enum("COL", col_names, headers)
    # show_col(COL)
    logic.update_settings(settings, COL, pattern_name)
    settings.column_names = col_names
    return COL


def show_col(enum) -> None:
    print("COL =")
    for member in enum:
        print(f"\t{member.value}: {member.name}->{member.display_title}")


def get_identity_of_file_pattern(settings: Default_settings, headers: list[str]) -> str:
    # print(f"******{headers}")
    col_count_of_new_file = len(headers)
    for title, ((index1, index2), cols, display_titles) in settings.known_types.items():
        # print(f"{col_count_of_new_file=}=={len(cols)=} {index1=}, {index2=}")
        # if index1 <= col_count_of_new_file:
        #     print(f"Identifying column A ({index1}): {headers[index1][:4].lower()} == {cols[index1][0][:4]}")
        # if index2 <= col_count_of_new_file:
        #     print(f"Identifying column B ({index2}): {headers[index2][:4].lower()} == {cols[index2][0][:4]}")
        if (
            len(headers) == len(cols)
            and index1 <= col_count_of_new_file
            and index2 <= col_count_of_new_file
            and headers[index1][:4].lower() == cols[index1][0][:4]
            and headers[index2][:4].lower() == cols[index2][0][:4]
        ):
            return title
    return ""


def get_grid_from_pattern(
    settings: Default_settings, pattern_name: str, COL: Enum
) -> Grid:
    template = []
    grid = Grid()
    _, cols, headers = settings.known_types[pattern_name]
    for i, col in enumerate(COL):
        line = (col, *cols[i][1:])
        template.append(line)
    settings.template = template
    grid.add_bricks_by_template(settings.template)
    return grid


def get_grid_from_algorithm(
    settings: Default_settings, rows: list[list[str]], headers: list[str]
) -> Grid:
    grid = Grid()
    max_lengths = create_max_lengths(rows)
    layout = [select_brick_by_content_length(length) for length in max_lengths]
    for id, (brick, widget_type) in enumerate(layout):
        # grid.add_brick_algorithmically(id, brick, headers[id], "", widget_type)
        grid.add_brick_algorithmically(
            id, brick, headers[id], settings.column_names[id], widget_type
        )
    return grid


def create_file_from_column_count(
    settings: Default_settings, column_count: int
) -> tuple[list[str], list[list[str]], Grid, Enum]:
    ## need to create new file + add in programmatic col names
    print(f"**Loading UI for new file with {column_count} columns")
    headers = [f"Col{i}" for i in range(0, column_count)]
    COL = update_settings_and_columns(settings, "default", headers)
    settings.files.out_file = f"tmp_{column_count}_cols.csv"
    rows = [["" for _ in range(0, column_count)]]
    grid = get_grid_from_algorithm(settings, rows, headers)
    # sys.exit(0)
    return (headers, rows, grid, COL)


def create_file_from_pattern(
    settings: Default_settings, pattern_name: str
) -> tuple[list[str], list[list[str]], Grid, Enum]:
    ## need to create new file + add in settings & col names from settings.known_patterns
    print(f"**Loading UI for new file using the {pattern_name} pattern")
    _, cols, headers = settings.known_types[pattern_name]
    COL = update_settings_and_columns(settings, pattern_name, headers, cols)
    settings.files.out_file = f"tmp_{pattern_name}_cols.csv"
    rows = [["" for _ in range(0, len(settings.column_names))]]
    grid = get_grid_from_pattern(settings, pattern_name, COL)
    # rows = []
    # sys.exit(0)
    return (headers, rows, grid, COL)


def setup_environment(settings: Default_settings, headers: list[str], COL):
    """
    NB. further updates settings
    """
    # read_cli_into_settings(settings)
    app = QApplication(sys.argv)
    grid = Grid()
    undefined_file_pattern = len(COL) == 0
    if undefined_file_pattern:
        ## * entry point for universal.py; generalise for all files
        from_file, column_count, pattern_name = get_file_pattern_and_name_from_user(
            settings
        )
        if from_file:
            headers, rows, grid, COL = get_existing_file(settings, COL)
        elif column_count:
            headers, rows, grid, COL = create_file_from_column_count(
                settings, column_count
            )
            settings.file_newly_created = True
        else:
            headers, rows, grid, COL = create_file_from_pattern(settings, pattern_name)
            rows = []
            settings.file_newly_created = True

    else:
        ## * entry point for art.py / strachan.py / orders.py routes
        ## NOW DEPRECATED
        print("creating new file")
        rows = []
        grid.add_bricks_by_template(settings.template)
    # show_col(COL)
    if settings.combos.data_file:
        settings.combos.data = io.open_yaml_file(
            settings.files.app_dir / settings.combos.data_file
        )
    # print(f"setup_environ: {len(rows)=}, {len(rows[0])=}, {headers=}")
    return (grid, rows, headers, COL, app)


def get_file_pattern_and_name_from_user(
    settings: Default_settings,
) -> tuple[bool, int, str]:
    file_patterns = list(settings.known_types.keys())
    launcher = LauncherDialog(f"./{settings.files.data_dir}", file_patterns)
    ##* exec() blocks until accept() or reject() is called
    if launcher.exec() == QDialog.DialogCode.Accepted:
        if launcher.selected_path:
            print(f"Loading UI for file: {launcher.selected_path}")
            settings.files.in_file = launcher.selected_path
            settings.is_existing_file = True
            return (True, 0, "")
        elif launcher.column_count:
            return (False, launcher.column_count, "")
        elif launcher.pattern_name:
            return (False, 0, launcher.pattern_name)
    else:
        print("User exited.")
        sys.exit(0)


def run(settings: Default_settings, headers: list[str], COL):
    grid, rows, headers, COL, app = setup_environment(settings, headers, COL)
    # if settings.file_newly_created:
    #     rows = []
    # print(f"form_gui.run(): {rows=}, {headers=}\n")
    window = WindowWithRightTogglePanel(grid, rows, settings, headers, COL, app)
    window.show()
    sys.exit(app.exec())
