import os
from typing import Optional

from PyQt6.QtWidgets import (
    QDialogButtonBox,
    QFileDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from folderhide.gui.utils import PasswordBar
from folderhide.gui.workers import HideThread


def isValidFolder(folder):
    return os.path.exists(folder) and os.path.isdir(folder)


def isValidFile(f):
    return os.path.exists(f) and os.path.isfile(f)


class Hide(QWidget):
    targetFolder: Optional[str] = None
    targetPath: Optional[str] = None
    workingThread: Optional[HideThread] = None

    def __init__(self, parent=None):
        super().__init__(parent)

        self.progressBar = QProgressBar()
        self.progressBar.setTextVisible(False)

        self.createButtons()
        self.createLogArea()
        self.createPasswordRow()
        self.createFolderSelect()
        self.createConfigRow()

        textGridLayout = QGridLayout()
        textGridLayout.addWidget(self.folderWidgetLabel, 0, 0)
        textGridLayout.addWidget(self.folderPathWidget, 0, 1)
        textGridLayout.addWidget(self.folderSelectButton, 0, 2)

        textGridLayout.addWidget(self.configWidgetLabel, 1, 0)
        textGridLayout.addWidget(self.configPathWidget, 1, 1)
        textGridLayout.addWidget(self.configSelectButton, 1, 2)

        textGridLayout.addWidget(self.passwordLabel, 2, 0, 1, 1)
        textGridLayout.addWidget(self.passwordBar, 2, 1, 1, 2)

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

        if not self.targetFolder:
            QMessageBox.critical(self, "Error", "No folder selected to hide.")
            return

        if not self.targetPath:
            QMessageBox.critical(self, "Error", "Output config path is empty.")
            return

        self.workingThread = HideThread(self.targetFolder, password, self.targetPath)
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

    def _setConfigPath(self):
        self.progressBar.reset()

        targetPath, _ = QFileDialog.getSaveFileName(
            caption="Save config to...", filter="Encrypted Config File (*.enc)"
        )
        if isValidFile(targetPath):
            answer = QMessageBox.question(
                self,
                "File already exists.",
                f"File {targetPath} already exists. Are you sure you want to replace it?",
            )
            if answer != QMessageBox.Yes:
                return

        self.targetPath = targetPath
        self.configPathWidget.setText(targetPath)

    def _reset(self):
        self.targetFolder = None
        self.targetPath = None
        self.folderPathWidget.setText("")
        self.configPathWidget.setText("")
        self.passwordBar.setText("")
        self.logArea.setText("")

    def createConfigRow(self):
        self.configWidgetLabel = QLabel("Config output")
        self.configPathWidget = QLineEdit()
        self.configPathWidget.setReadOnly(True)
        self.configSelectButton = QPushButton("Browse")
        self.configSelectButton.clicked.connect(self._setConfigPath)

    def createButtons(self):
        startButton = QPushButton("Start")
        startButton.clicked.connect(self._hide)
        resetButton = QPushButton("Reset")
        resetButton.clicked.connect(self._reset)

        self.buttonArea = QDialogButtonBox()
        self.buttonArea.addButton(startButton, QDialogButtonBox.ButtonRole.ActionRole)
        self.buttonArea.addButton(resetButton, QDialogButtonBox.ButtonRole.ResetRole)

    def createLogArea(self):
        self.logArea = QTextEdit()
        self.logArea.setReadOnly(True)

    def createPasswordRow(self):
        self.passwordLabel = QLabel("Password")
        self.passwordBar = PasswordBar()

    def createFolderSelect(self):
        """Creates the folder selection layout."""
        self.folderWidgetLabel = QLabel("Folder to hide")
        self.folderPathWidget = QLineEdit()
        self.folderPathWidget.setReadOnly(True)
        self.folderSelectButton = QPushButton("Browse")
        self.folderSelectButton.clicked.connect(self._setFolder)
