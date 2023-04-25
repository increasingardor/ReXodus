from PyQt5.QtCore import QThread, pyqtSignal
from connector import Connector


class GetImages(QThread):
    finished = pyqtSignal()
    downloads = pyqtSignal(str, int, int)

    def __init__(self, username: str, location: str, ctrl: dict, sources: list):
          super(GetImages, self).__init__()
          self.connector = Connector(username, location)
          self.connector.sources = sources
          self.stop = False
          self.ctrl = ctrl
          self.connector.ctrl = ctrl

    def __del__(self):
          self.wait()

    def run(self):
        self.ctrl["stop"] = False
        posts = 0
        for post in self.connector.posts:
            if self.ctrl["stop"]:
                break
            posts += 1
            file = self.connector.parse(self.connector.session, post)
            if file is not None:
                try:
                    success = file.download(self.connector.location)
                    if success:
                        if isinstance(success, list):
                            downloads = len(success)
                        else:
                            downloads = 1
                        self.downloads.emit(file.message, posts, downloads)
                except Exception as e:
                    print(e)
        self.finished.emit()