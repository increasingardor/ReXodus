import typing
from bs4 import BeautifulSoup
import requests
import config
import os
import praw.models
from yarl import URL

class BaseImage:
    '''
    Base image class from which other inherit, handles final downloads from
    all
    '''
    def __init__(self, session: requests.Session, url: str):
        self.session = session
        self.url = url
        self.ctrl = { "stop": False }
        self.filetype = url.split(".")[len(url.split(".")) - 1]
        self.message = ""

    def download(self, location: str, filename: str=None) -> bool:
        location = location.replace("/", "\\")
        url = URL(self.url)
        folder, fullpath = self.parse_url(url, location, filename)
        if not os.path.isfile(fullpath):
            os.makedirs(folder, exist_ok=True)
            if hasattr(self, "headers"):
                resp = self.session.get(self.url, headers=self.headers)
            else:
                resp = self.session.get(self.url)
            with open(f"{fullpath}", "wb") as file:
                for chunk in resp.iter_content(1024):
                    if self.ctrl["stop"]:
                        break
                    file.write(chunk)
            if self.ctrl["stop"]:
                return self.endDownload(fullpath)
            self.message = f"Saved {fullpath}\n"
            return True
        return False

    def endDownload(self, fullpath: str=None):
        if fullpath:
            os.remove(fullpath)
        return False

    def parse_url(self, url: str, location: str, filename: str=None):
        url = URL(url)
        folder_name = url.host
        folder = os.path.join(location, folder_name)
        if not filename:
            filename = url.parts[len(url.parts) - 1]
        fullpath = os.path.join(folder, filename)
        return (folder, fullpath)

class ImgurImage(BaseImage):
    def __init__(self, session: requests.Session, url: str):
        ext = url.split(".")[len(url.split(".")) - 1]
        if ext.lower() == "gifv":
            url = url.replace("gifv", "mp4").replace("gifV", "mp4")
        super().__init__(session, url)

    def download(self, location: str) -> bool:
        if self.url.find("remove") > -1:
            return False
        return super().download(location)

class ImgurAlbum(BaseImage):
    def __init__(self, session: requests.Session, url: str):
        self.api = config.IMGUR_ALBUM_API
        super().__init__(session, url)

    def download(self, location: str) -> typing.Union[bool, list]:
        url = URL(self.url)
        id = url.parts[len(url.parts) - 1]
        headers = { "Authorization": config.IMGUR_CLIENT_ID }
        resp = self.session.get(f"{self.api}{id}", headers=headers)
        data = resp.json()
        results = [True * len(data["data"]["images"])]
        for image in data["data"]["images"]:
            if self.ctrl["stop"]:
                return self.endDownload()
            self.url = image["link"]
            super().download(location)
        return results

class RedditImage(BaseImage):
    def __init__(self, session: requests.Session, url: str, post: praw.models.Submission):
        self.post = post
        super().__init__(session, url)

    def download(self, location: str) -> bool:
        if self.post.secure_media:
            self.url = self.post.secure_media["reddit_video"]["fallback_url"].split("?")[0]
        elif self.post.media:
            self.url = self.post.media["reddit_video"]["fallback_url"].split("?")[0]
        if self.url.find("DASH_") > -1:
            parts = URL(self.url).parts
            name_parts = parts[len(parts) - 1].split(".")
            ext = name_parts[len(name_parts) - 1]
            filename = f"{parts[len(parts) - 2]}.{ext}"
        else:
            filename = None
        return super().download(location, filename)

class RedditAlbum(BaseImage):
    def __init__(self, session: requests.Session, url: str, post: praw.models.Submission):
        self.post = post
        self.base_url = config.REDDIT_ALBUM_URL
        super().__init__(session, url)

    def download(self, location: str) -> typing.Union[bool, list]:
        if self.post.media_metadata:
            results = [True * len(self.post.media_metadata.items())]
            for image in self.post.media_metadata.items():
                if self.ctrl["stop"]:
                    return self.endDownload()
                id = image[0]
                ext = self.parse_filetype(image[1]["m"])
                self.url = f"{self.base_url}/{id}.{ext}"
                super().download(location)
            return results
        return False

    def parse_filetype(self, mime: str) -> str:
        return mime.split("/")[len(mime.split("/")) - 1]

class Erome(BaseImage):
    def download(self, location: str) -> typing.Union[bool, list]:
        self.headers = {"User-Agent": "Mozilla/5.0"}
        resp = self.session.get(self.url, headers=self.headers)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "html.parser")
        else:
            return False
        files = []
        [files.append(video_source["src"]) for video_source in soup.find_all("source")]
        [files.append(image["data-src"]) for image in soup.find_all("img", {"class": "img-back"})]
        results = [True * len(files)]
        for file in files:
            if self.ctrl["stop"]:
                return self.endDownload()
            folder, fullpath = self.parse_url(file, location)
            self.headers["Referrer"] = self.url
            self.headers["Origin"] = f"https://{URL(file).host}"
            super().download(location)
        return results

class RedGifs(BaseImage):
    def __init__(self, session: requests.Session, url: str, headers: dict):
        parts = url.split("/")
        self.id = parts[len(parts) - 1].split(".")[0]
        self.headers = headers
        self.api = "https://api.redgifs.com/v2/gifs"
        super().__init__(session, url)

    def download(self, location: str) -> bool:
        if self.ctrl["stop"]:
            return self.endDownload()
        gif_resp = self.session.get(f"{self.api}/{self.id}", headers=self.headers)
        gif_data = gif_resp.json()
        self.url = gif_data["gif"]["urls"]["hd"]
        return super().download(location)

class GfyImage(BaseImage):
    def __init__(self, session: requests.Session, url: str, headers: dict):
        parts = url.split("/")
        self.id = parts[len(parts) - 1].split(".")[0]
        self.headers = headers
        self.api = "https://api.gfycat.com/v1/gfycats"
        super().__init__(session, url)

    def download(self, location: str) -> bool:
        if self.ctrl["stop"]:
            return self.endDownload()
        gfy_resp = self.session.get(f"{self.api}/{self.id}", headers=self.headers)
        gif_data = gfy_resp.json()
        self.url = gif_data["gfyItem"]["mp4Url"]
        return super().download(location)