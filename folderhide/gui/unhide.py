from PyQt5.QtWidgets import QWidget


class Unhide(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.window = QWidget()
