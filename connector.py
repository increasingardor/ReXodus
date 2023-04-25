import requests
import praw
import config
from yarl import URL
from images import *


class Connector:
    '''
    Handles connections to Reddit and various image hosts
    '''
    def __init__(self, username: str, location: str):
        self.session = requests.Session()
        self.location = location

        # Reddit variables
        self.__reddit = praw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_SECRET,
            user_agent=config.USER_AGENT,
        )
        self.redditor = self.__reddit.redditor(username)
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

    def parse(self, session: requests.Session, post: praw.models.Submission) -> BaseImage:
        TYPES = "jpg, png, gif, mp4"

        if (post.url.find("reddit") > -1 or post.url.find("redd.it") > -1) and not post.is_self and self.sources["Reddit"]:
            if post.url.find("gallery") > -1:
                image = RedditAlbum(session, post.url, post)
                image.ctrl = self.ctrl
                return image
            image = RedditImage(session, post.url, post)
            image.ctrl = self.ctrl
            return image
        elif post.url.find("imgur") > -1 and self.sources["Imgur"]:
            parts = URL(post.url).parts
            if "a" in parts or "album" in parts:
                image = ImgurAlbum(session, post.url)
            else:
                image = ImgurImage(session, post.url)
            image.ctrl = self.ctrl
            return image
        elif post.url.find("erome.com") > -1 and self.sources["Erome"]:
            image = Erome(session, post.url)
            image.ctrl = self.ctrl
            return image
        elif post.url.find("redgifs") > -1 and self.sources["Redgifs"]:
            image = RedGifs(session, post.url, self.redgifs_headers)
            image.ctrl = self.ctrl
            return image
        elif post.url.find("gfycat") > -1  and self.sources["GfyCat"]:
            image = GfyImage(session, post.url, self.gfy_headers)
            image.ctrl = self.ctrl
            return image
        elif post.url.split(".")[len(post.url.split(".")) - 1] in TYPES and self.sources["Others"]:
            image = BaseImage(session, post.url)
            image.ctrl = self.ctrl
            return image
        return None