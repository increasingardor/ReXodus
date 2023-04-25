from typing import Any, Callable
from PyQt5.QtCore import QThread, pyqtSignal
from connector import Connector


class GetImages(QThread):
    finished = pyqtSignal()
    downloads = pyqtSignal(str, int, int)

    # def __init__(self, username: str, location: str, ctrl: dict, sources: list):
    def __init__(self, ctrl: dict, connector: Connector, location: str):

          super(GetImages, self).__init__()
          self.connector = connector
          self.ctrl = ctrl
          self.connector.ctrl = ctrl
          self.location = location
          self.connector.connect()

    def __del__(self):
          self.wait()

    def run(self):
        self.ctrl["stop"] = False
        postCount = 0
        for post in self.connector.posts:
            if self.ctrl["stop"]:
                break
            postCount += 1
            self.downloads.emit(f"Processing {post.url}", postCount, 0)
            file = self.connector.parse(post)
            if file is not None:
                file.ctrl = self.ctrl
                try:
                    success = file.download(self.location)
                    if success:
                        if isinstance(success, list):
                            downloads = len(success)
                        else:
                            downloads = 1
                        self.downloads.emit(file.message, postCount, downloads)
                except Exception as e:
                    print(e)
        self.finished.emit()

    def onComplete(self, *methods: Callable[[Any], Any]):
        for method in methods:
            self.finished.connect(method)