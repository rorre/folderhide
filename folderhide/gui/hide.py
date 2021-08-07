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
from folderhide.gui.workers import HideThread


def isValidFolder(folder):
    return os.path.exists(folder) and os.path.isdir(folder)


class Hide(QWidget):
    targetFolder: Optional[str] = None
    workingThread: Optional[HideThread] = None

    def __init__(self, parent=None):
        super().__init__(parent)

        self.progressBar = QProgressBar()
        self.progressBar.setTextVisible(False)

        self.createButtons()
        self.createLogArea()
        self.createPasswordRow()
        self.createFolderSelect()

        textGridLayout = QGridLayout()
        textGridLayout.addWidget(self.folderWidgetLabel, 0, 0)
        textGridLayout.addWidget(self.folderPathWidget, 0, 1)
        textGridLayout.addWidget(self.folderSelectButton, 0, 2)
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

        self.workingThread = HideThread(self.targetFolder, password)
        self.workingThread.total.connect(self.progressBar.setMaximum)
        self.workingThread.progress.connect(self.progressBar.setValue)
        self.workingThread.log.connect(self.logArea.append)
        self.workingThread.start()

    def _setFolder(self):
        self.progressBar.reset()

        targetFolder = QFileDialog.getExistingDirectory(caption="Select Folder...")
        self.folderPathWidget.setText(targetFolder)

        if not targetFolder:
            return

        if not isValidFolder(targetFolder):
            QMessageBox.critical(self, "Error", "Folder not found.")
            return
        self.targetFolder = targetFolder

    def _reset(self):
        self.targetFolder = None
        self.folderPathWidget.setText("")
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

    def createFolderSelect(self):
        """Creates the folder selection layout."""
        self.folderWidgetLabel = QLabel("Folder to hide")
        self.folderPathWidget = QLineEdit()
        self.folderPathWidget.setReadOnly(True)
        self.folderSelectButton = QPushButton("Browse")
        self.folderSelectButton.clicked.connect(self._setFolder)
