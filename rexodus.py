import datetime
import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QFileDialog, QLabel, QMainWindow, QWidget
from background_threads import GetImages
from main_ui import Ui_MainWindow


class Rexodus(QMainWindow, Ui_MainWindow):
    def __init__(self, parent: QWidget=None):
        super().__init__(parent)
        self.setupUi(self)
        self.postCount = 0
        self.postTextLabel = QLabel("Posts processed:")
        self.postCountLabel = QLabel(str(self.postCount))
        self.downloadCount = 0
        self.downloadTextLabel = QLabel("Files downloaded:")
        self.downloadCountLabel = QLabel(str(self.downloadCount))
        self.counter = 0
        self.counterLabel = QLabel(str(datetime.timedelta(seconds=self.counter)))
        self.widgets = [self.counterLabel, self.postTextLabel, self.postCountLabel, self.downloadTextLabel, self.downloadCountLabel]
        self.addPermanentWidgets()

        self.browseButton.clicked.connect(self.onBrowseClicked)
        self.getFiles.clicked.connect(self.onGetFilesClicked)
        self.cancel.clicked.connect(self.onCancelClicked)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTimer)

    def addPermanentWidgets(self):
        for widget in self.widgets:
            self.statusBar.addPermanentWidget(widget)

    def updateTimer(self):
        self.counter += 1
        self.counterLabel.setText(str(datetime.timedelta(seconds=self.counter)))
        self.repaint()

    def onBrowseClicked(self):
        location = QFileDialog.getExistingDirectory(self, "Select Save Location")
        self.location.setText(location)

    def onGetFilesClicked(self):
        self.postCount = 0
        self.downloadCount = 0
        sources = {"Imgur": self.Imgur.isChecked(), "Reddit": self.Reddit.isChecked(), "Erome": self.Erome.isChecked(), "Redgifs": self.Redgifs.isChecked(), "GfyCat": self.GfyCat.isChecked(), "Others": self.Others.isChecked()}
        self.getImages = GetImages(self.redditName.text(), self.location.text(), {}, sources)
        self.getImages.downloads.connect(self.add_message)
        self.getImages.start()
        self.timer.start(1000)
        self.inputWidgets = [self.browseButton, self.cancel, self.getFiles, self.redditName]
        self.toggleWidgetsEnabled()
        self.getImages.finished.connect(self.toggleWidgetsEnabled)
        self.getImages.finished.connect(self.timer.stop)

    def onCancelClicked(self):
        self.getImages.ctrl["stop"] = True
        self.add_message("Stopping Downloads...", 0, 0)
        self.getImages.finished.connect(lambda: self.add_message("Downloads stopped", 0, 0))

    def toggleWidgetsEnabled(self):
        for widget in self.inputWidgets:
            widget.setEnabled(not widget.isEnabled())

    def add_message(self, message: str, postCount: int, downloadCount: int):
        self.statusBar.showMessage(message)
        self.postCount = postCount
        self.postCountLabel.setText(str(self.postCount))
        self.downloadCount += downloadCount
        self.downloadCountLabel.setText(str(self.downloadCount))
        self.repaint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Rexodus()
    win.show()
    sys.exit(app.exec())