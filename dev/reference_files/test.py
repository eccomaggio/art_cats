import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QTextEdit,
    QTextBrowser,
)
from PySide6.QtCore import Qt, QUrl, QTimer


class FixedRightPanelWindow(QWidget):
    saved_editor_width = 0
    GRID_BUFFER = 15  # Buffer for layout margins/spacing

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simplified Layout with Sticky Editor")
        self.setGeometry(100, 100, 1200, 800)

        self.main_grid = QGridLayout(self)
        self.main_grid.setContentsMargins(0, 0, 0, 0)
        self.main_grid.setSpacing(3)

        self.EDIT_PANEL_INITIAL_WIDTH = 800
        self.EDIT_PANEL_HEIGHT = 700
        self.HELP_PANEL_WIDTH = 350

        # --- 1. Main Editor Setup (Column 0, Expanding) ---
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)

        self.edit_panel = QTextEdit()
        self.edit_panel.setPlaceholderText(
            "Editor size is sticky when toggling help panel."
        )

        self.edit_panel.setMinimumSize(
            self.EDIT_PANEL_INITIAL_WIDTH, self.EDIT_PANEL_HEIGHT
        )
        self.edit_panel.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.toggle_button = QPushButton("Hide Help Panel")
        self.toggle_button.clicked.connect(self.toggle_help_panel)

        editor_layout.addWidget(self.edit_panel)
        editor_layout.addWidget(self.toggle_button)
        editor_layout.addStretch(1)

        # --- 2. Help Panel Setup (Column 1, Fixed Width) ---
        self.help_widget = QTextBrowser()
        long_spacer = "<br>" * 50
        html_content = f"""
        <h1>Table of Contents</h1>
        <p><a href="#appendix">Jump to Appendix</a></p>
        <p>This document is long enough to scroll.</p>
        {long_spacer}
        <h1 id="appendix">Appendix A: Key Data</h1>
        <p>This is the destination of the link.</p>
        <p><a href="#">Return to Top</a></p>"""

        self.help_widget.setHtml(html_content)
        self.help_widget.anchorClicked.connect(self.handle_internal_link)
        self.help_widget.setReadOnly(True)
        self.help_widget.setFixedWidth(self.HELP_PANEL_WIDTH)

        # Add panes to the main grid layout
        self.main_grid.addWidget(editor_container, 0, 0)
        self.main_grid.addWidget(self.help_widget, 0, 1)

        # Set Column Stretch Factors for the 2-column layout:
        self.main_grid.setColumnStretch(0, 10)  # Editor column (Expands)
        self.main_grid.setColumnStretch(1, 0)  # Help panel column (Fixed)

        # Initial layout sizing
        self.adjustSize()

        # Capture the correct initial size after layout setup
        self.saved_editor_width = self.edit_panel.width()

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
                self.edit_panel.sizePolicy().horizontalPolicy()
                == QSizePolicy.Policy.Fixed
            ):

                # 1. Restore the Expanding policy
                self.edit_panel.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
                )

                # 2. Remove the fixed width constraint
                self.edit_panel.setFixedWidth(16777215)  # QWIDGETSIZE_MAX

                # 3. Force a layout update to make the editor stretch immediately
                self.layout().invalidate()
                self.update()

    def toggle_help_panel(self):
        """
        Toggles the help panel visibility while managing the editor's size policy
        to achieve the sticky width and correct window resizing on all toggles.
        """

        is_visible = self.help_widget.isVisible()

        if is_visible:
            # --- Hiding Panel (Shrinking Window) ---

            # 1. Save the current width (the user's preferred size)
            self.saved_editor_width = self.edit_panel.width()

            # 2. Temporarily set the editor's horizontal policy to Fixed
            self.edit_panel.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
            )
            self.edit_panel.setFixedWidth(self.saved_editor_width)

            # 3. Hide the panel.
            self.help_widget.setVisible(False)

            # 4. Calculate new width (saved editor width + buffer)
            new_width = self.saved_editor_width + self.GRID_BUFFER
            self.toggle_button.setText("Show Help Panel")

            # 5. Delay the resize to let the Fixed policy take effect
            QTimer.singleShot(1, lambda: self.resize(new_width, self.height()))

        else:
            # --- Showing Panel (Expanding Window) ---
            self.saved_editor_width = self.edit_panel.width()
            # 2. Restore the editor's policy to Expanding
            self.edit_panel.setFixedWidth(16777215)
            self.edit_panel.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            self.help_widget.setVisible(True)
            # 4. Calculate the full width needed (New Editor Width + Help Panel Width + buffer)
            new_width = (
                self.saved_editor_width + self.HELP_PANEL_WIDTH + self.GRID_BUFFER
            )
            self.toggle_button.setText("Hide Help Panel")
            self.resize(new_width, self.height())

    def handle_internal_link(self, url: QUrl):
        """Scrolls the QTextBrowser to the target anchor within the document."""
        anchor_name = url.toString().split("#")[-1]
        if anchor_name:
            self.help_widget.scrollToAnchor(anchor_name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FixedRightPanelWindow()
    window.show()
    sys.exit(app.exec())