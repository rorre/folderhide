import os
from typing import Optional
from PyQt5.QtWidgets import (
    QWidget,
    QFileDialog,
    QPushButton,
    QLineEdit,
    QProgressBar,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QTextEdit,
    QDialogButtonBox,
    QGridLayout,
)
from folderhide.gui.workers import UnhideThread


def isValidFile(f):
    return os.path.exists(f) and os.path.isfile(f)


class Unhide(QWidget):
    configFile: Optional[str] = None
    workingThread: Optional[UnhideThread] = None

    def __init__(self, parent=None):
        super().__init__(parent)

        self.progressBar = QProgressBar()
        self.progressBar.setTextVisible(False)

        self.createButtons()
        self.createLogArea()
        self.createPasswordRow()
        self.createFileSelect()

        textGridLayout = QGridLayout()
        textGridLayout.addWidget(self.fileWidgetLabel, 0, 0)
        textGridLayout.addWidget(self.filePathWidget, 0, 1)
        textGridLayout.addWidget(self.fileSelectButton, 0, 2)
        textGridLayout.addWidget(self.passwordLabel, 1, 0, 1, 1)
        textGridLayout.addWidget(self.passwordBar, 1, 1, 1, 2)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(textGridLayout)
        mainLayout.addWidget(self.progressBar)
        mainLayout.addWidget(self.logArea)
        mainLayout.addWidget(self.buttonArea)

        self.setLayout(mainLayout)

    def _hide(self):
        password = self.passwordBar.text()
        if not password:
            QMessageBox.critical(self, "Error", "Password is empty.")
            return

        if not self.configFile:
            QMessageBox.critical(self, "Error", "No config file selected.")
            return

        self.workingThread = UnhideThread(self.configFile, password)
        self.workingThread.total.connect(self.progressBar.setMaximum)
        self.workingThread.progress.connect(self.progressBar.setValue)
        self.workingThread.log.connect(self.logArea.append)
        self.workingThread.start()

    def _setFile(self):
        self.progressBar.reset()

        targetFile, _ = QFileDialog.getOpenFileName(caption="Select config file...")
        self.filePathWidget.setText(targetFile)

        if not targetFile:
            return

        if not isValidFile(targetFile):
            QMessageBox.critical(self, "Error", "File not found.")
            return
        self.configFile = targetFile

    def _reset(self):
        self.configFile = None
        self.filePathWidget.setText("")
        self.passwordBar.setText("")
        self.logArea.setText("")

    def createButtons(self):
        startButton = QPushButton("Start")
        startButton.clicked.connect(self._hide)
        resetButton = QPushButton("Reset")
        resetButton.clicked.connect(self._reset)

        self.buttonArea = QDialogButtonBox()
        self.buttonArea.addButton(startButton, QDialogButtonBox.ActionRole)
        self.buttonArea.addButton(resetButton, QDialogButtonBox.ResetRole)

    def createLogArea(self):
        self.logArea = QTextEdit()
        self.logArea.setReadOnly(True)

    def createPasswordRow(self):
        self.passwordLabel = QLabel("Password")
        self.passwordBar = QLineEdit()

    def createFileSelect(self):
        """Creates the folder selection layout."""
        self.fileWidgetLabel = QLabel("Config file")
        self.filePathWidget = QLineEdit()
        self.filePathWidget.setReadOnly(True)
        self.fileSelectButton = QPushButton("Browse")
        self.fileSelectButton.clicked.connect(self._setFile)
