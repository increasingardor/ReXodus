import requests
import praw
import config
import reddit
from yarl import URL
from images import *


class Connector:
    '''
    Handles connections to Reddit and various image hosts
    '''
    def __init__(self, username: str, sources: list):
        self.username = username
        self.session = requests.Session()
        self.sources = sources

    def connect(self):
        # Reddit variables
        self.__reddit = reddit.get_reddit()
        self.redditor = self.__reddit.redditor(self.username)
        self.posts = self.redditor.submissions.hot(limit=None)

        # Redgifs variables
        self.redgifs_headers = { "User-Agent": config.USER_AGENT }
        redgifs_resp = self.session.get(config.REDGIFS_AUTH, headers=self.redgifs_headers)
        data = redgifs_resp.json()
        self.redgifs_headers["Authorization"] = f"Bearer {data['token']}"

        # Gfycat variables
        gfy_payload = {
            "grant_type": "client_credentials",
            "client_id": config.GFYCAT_CLIENT_ID,
            "client_secret": config.GFYCAT_SECRET
        }
        gfy_resp = self.session.get(config.GFYCAT_AUTH_API, json=gfy_payload)
        data = gfy_resp.json()
        gfy_token = data['access_token']
        self.gfy_headers = { "Authorization": f"Bearer {gfy_token}" }

    def parse(self, post: praw.models.Submission) -> BaseImage:
        TYPES = "jpg, png, gif, mp4"

        if (post.url.find("reddit") > -1 or post.url.find("redd.it") > -1) and not post.is_self and self.sources["Reddit"]:
            if post.url.find("gallery") > -1:
                image = RedditAlbum(self.session, post.url, post)
                image.ctrl = self.ctrl
                return image
            image = RedditImage(self.session, post.url, post)
            image.ctrl = self.ctrl
            return image
        elif post.url.find("imgur") > -1 and self.sources["Imgur"]:
            parts = URL(post.url).parts
            if "a" in parts or "album" in parts:
                image = ImgurAlbum(self.session, post.url)
            else:
                image = ImgurImage(self.session, post.url)
            image.ctrl = self.ctrl
            return image
        elif post.url.find("erome.com") > -1 and self.sources["Erome"]:
            image = Erome(self.session, post.url)
            image.ctrl = self.ctrl
            return image
        elif post.url.find("redgifs") > -1 and self.sources["Redgifs"]:
            image = RedGifs(self.session, post.url, self.redgifs_headers)
            image.ctrl = self.ctrl
            return image
        elif post.url.find("gfycat") > -1 and self.sources["GfyCat"]:
            image = GfyImage(self.session, post.url, self.gfy_headers)
            image.ctrl = self.ctrl
            return image
        elif post.url.split(".")[len(post.url.split(".")) - 1] in TYPES and self.sources["Others"]:
            image = BaseImage(self.session, post.url)
            image.ctrl = self.ctrl
            return image
        return None