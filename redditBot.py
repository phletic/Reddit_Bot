import praw
from praw.reddit import Submission
from prawcore.exceptions import Redirect
import json

class reddit_bot:
    def __init__(self,authentication_details : dict,read_only : bool, subreddit:str):
        reddit = praw.Reddit(**authentication_details)
        reddit.read_only = read_only
        self.reddit = reddit
        self.subreddit = self.reddit.subreddit(subreddit)
    
    def subredditCommand(self, command : str):
        return getattr(self.subreddit, command)

    def getNewSubreddits(self):
        return self.subreddit.new
    
    def getHotSubreddits(self):
        return self.subreddit.hot

    def getPostById(self, iDStr):
        return self.reddit.submission(id=iDStr)

    def getSubscribers(self):
        return self.subreddit.subscribers
    
