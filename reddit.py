import config
import praw

def get_reddit():
    return praw.Reddit(
                client_id=config.REDDIT_CLIENT_ID,
                client_secret=config.REDDIT_SECRET,
                user_agent=config.USER_AGENT,
                check_for_updates=True,
                comment_kind="t1",
                message_kind="t4",
                redditor_kind="t2",
                submission_kind="t3",
                subreddit_kind="t5",
                trophy_kind="t6",
                oauth_url="https://oauth.reddit.com",
                ratelimit_seconds=5,
                reddit_url="https://www.reddit.com",
                short_url="https://redd.it",
                timeout=16
            )