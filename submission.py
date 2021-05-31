import datetime


class Post:
    def __init__(self, content: str, ups: int, downs: int, author: str, time: datetime, id: str):
        self.content = content
        self.ups = ups
        self.downs = downs
        self.author = author
        self.time = time
        self.id = id


class Submission(Post):
    def __init__(self, content: str, title: str, ups: int, downs: int, author: str, time: datetime, comments: list, id: str):
        super().__init__(content, ups, downs, author, time, id)
        self.title = title
        self.comments = comments


class Comment(Post):
    def __init__(self, content: str, ups: int, downs: int, author: str, time: datetime, replies: list, id: str):
        super().__init__(content, ups, downs, author, time, id)
        self.replies = replies


class reply(Post):
    def __init__(self, content: str, ups: int, downs: int, author: str, time: datetime, id: str):
        super().__init__(content, ups, downs, author, time, id)
