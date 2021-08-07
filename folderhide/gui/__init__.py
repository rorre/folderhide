from PyQt5.QtWidgets import QApplication
from folderhide.gui.hide import Hide
from folderhide.gui.unhide import Unhide
from PyQt5.QtWidgets import QMainWindow, QTabWidget


class Main(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.hideWidget = Hide()
        self.unhideWidget = Unhide()

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.hideWidget, "Hide")
        self.tabWidget.addTab(self.unhideWidget, "Unhide")
        self.setCentralWidget(self.tabWidget)

        self.setMinimumSize(800, 600)


def run(args):
    app = QApplication(args)
    win = Main()
    win.show()
    app.exec_()
