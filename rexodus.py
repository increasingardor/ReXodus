import datetime
import os
import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QFileDialog, QLabel, QMainWindow, QWidget, QStatusBar
from background_threads import GetImages
from connector import Connector
from main_ui import Ui_MainWindow

class Rexodus(QMainWindow, Ui_MainWindow):
    def __init__(self, parent: QWidget=None):
        self.statusBar: QStatusBar
        super().__init__(parent)
        self.setupUi(self)
        self.postCount = 0
        self.postTextLabel = QLabel("Posts processed:")
        self.postCountLabel = QLabel(str(self.postCount))
        self.downloadCount = 0
        self.downloadTextLabel = QLabel("Files downloaded:")
        self.downloadCountLabel = QLabel(f"{self.downloadCount} ")
        self.counter = 0
        self.counterLabel = QLabel(str(datetime.timedelta(seconds=self.counter)))
        self.widgets = [self.counterLabel, self.postTextLabel, self.postCountLabel, self.downloadTextLabel, self.downloadCountLabel]
        self.doNotEnable = []
        self.addPermanentWidgets()

        self.locationText.linkActivated.connect(self.onLocationClicked)
        self.locationText.linkHovered.connect(self.onLocationHover)
        self.browseButton.clicked.connect(self.onBrowseClicked)
        self.getFiles.clicked.connect(self.onGetFilesClicked)
        self.cancel.clicked.connect(self.onCancelClicked)

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.updateTimer(self.counter + 1))

    def addPermanentWidgets(self):
        for widget in self.widgets:
            self.statusBar.addPermanentWidget(widget)

    def updateTimer(self, counterValue: int):
        self.counter = counterValue
        self.counterLabel.setText(str(datetime.timedelta(seconds=self.counter)))
        self.repaint()

    def onBrowseClicked(self):
        self.location = QFileDialog.getExistingDirectory(self, "Select Save Location")
        self.locationText.setText(f"<a href='{self.location}'>{self.location}</a>")

    def onLocationHover(self, link):
        if link:
            self.statusBar.showMessage(link)
        else:
            self.statusBar.clearMessage()

    def onLocationClicked(self):
        os.startfile(self.location)

    def onGetFilesClicked(self):
        self.inputWidgets = [self.browseButton, self.cancel, self.getFiles, self.redditName]
        self.toggleWidgetsEnabled()
        self.updateTimer(0)
        self.postCount = 0
        self.downloadCount = 0
        self.add_message("Connecting to Reddit...", self.postCount, self.downloadCount)
        sources = {"Imgur": self.Imgur.isChecked(), "Reddit": self.Reddit.isChecked(), "Erome": self.Erome.isChecked(), "Redgifs": self.Redgifs.isChecked(), "GfyCat": self.GfyCat.isChecked(), "Others": self.Others.isChecked()}
        connector = Connector(self.redditName.text(), sources)
        self.getImages = GetImages({}, connector, self.location)
        self.getImages.downloads.connect(self.add_message)
        self.getImages.start()
        self.timer.start(1000)
        self.getImages.onComplete(self.toggleWidgetsEnabled, self.timer.stop)

    def onCancelClicked(self):
        self.doNotEnable.append(self.cancel)
        self.cancel.setEnabled(False)
        self.getImages.ctrl["stop"] = True
        self.add_message("Stopping Downloads...", self.postCount, 0)
        #self.getImages.finished.connect(lambda: self.add_message("Downloads stopped", self.postCount, 0))
        self.getImages.onComplete(lambda: self.add_message("Downloads stopped", self.postCount, 0))

    def toggleWidgetsEnabled(self):
        for widget in self.inputWidgets:
            if widget not in self.doNotEnable:
                widget.setEnabled(not widget.isEnabled())
        self.doNotEnable = []

    def add_message(self, message: str, postCount: int, downloadCount: int):
        self.statusBar.showMessage(message)
        self.postCount = postCount
        self.postCountLabel.setText(str(self.postCount))
        self.downloadCount += downloadCount
        self.downloadCountLabel.setText(f"{self.downloadCount} ")
        self.repaint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Rexodus()
    win.show()
    sys.exit(app.exec())