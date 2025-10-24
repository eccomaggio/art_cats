import sys
import re
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QHBoxLayout,
)
from PySide6.QtCore import (
    Qt,
    Signal,
    QTimer,
    QEvent,
)
from PySide6.QtGui import (
    QMouseEvent,
    QEnterEvent,
)

# Note: QLeaveEvent is often unavailable by name. We use QEvent as the type hint.


class ClickableLabel(QLabel):
    """
    QLabel subclass: emits signals when clicked and visually reacts to hovering.
    """

    clicked = Signal()

    def __init__(self, text="Click Me", parent=None):
        super().__init__(text, parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.WhatsThisCursor)
        self.default_style = "text-decoration: none;"
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


class ExampleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Accessing Sender Widget Example")

        self.main_layout = QVBoxLayout(self)

        # Display Area
        self.count = 0
        self.display = QLineEdit(f"Count: {self.count}")
        self.display.setReadOnly(True)
        self.display.setStyleSheet(
            "font-size: 24px; padding: 10px; background-color: #e8e8e8;"
        )
        self.display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.display)

        # Button Container
        self.button_container = QHBoxLayout()
        self.main_layout.addLayout(self.button_container)

        # --- Create Buttons with Parameters ---

        # List of step values and their corresponding button texts
        steps = [1, 5, 8]
        texts = [f"Add {s}" for s in steps]

        for step, text in zip(steps, texts):
            label = ClickableLabel(text)
            # label.help_txt = step
            label.help_txt = text.lower().replace(" ", "_")

            self.button_container.addWidget(label)

            # 2. Modify the lambda to pass the widget itself (label)
            # We use 'l=label' to correctly capture the current label instance in the loop.
            label.clicked.connect(
                lambda checked=False, l=label: self.show_help_topic(l)
            )

    def show_help_topic(self, sender_label: ClickableLabel):
        """Slot runs when label is clicked, accessing custom property."""
        link = sender_label.help_txt
        self.display.setText(link)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExampleWindow()
    window.show()
    sys.exit(app.exec())
