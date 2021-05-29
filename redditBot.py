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
        self.subreddit.new(limit=5)
    
    def subredditCommand(self, command : str):
        return getattr(self.subreddit, command)
    
