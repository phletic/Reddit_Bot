from praw.reddit import Submission
import submission
import redditBot
import pickle
import threading
import queue
import json


def runThread(_thread):
    for i in _thread:
        i.run()
    for i in _thread:
        if i.is_alive():
            i.join()


def checkDuplicate(i, readFile):
    if i.id in readFile:
        return 0
    else:
        return i

def getEntries():
    objects = []
    # open file
    with open("submissions.redd", "rb") as submissionFile:
        # attempt to read
        try:
            objects = pickle.load(submissionFile)
        # return empty list if database is empty
        except EOFError:
            objects = []
    return objects


def writeFile(submissions):
    open('submissions.redd', 'w').close()
    with open("submissions.redd", "wb") as submissionFile:
        pickle.dump(submissions, submissionFile)


def createSubmissionObjects(Bot: redditBot.reddit_bot):
    output = []
    fileList = getEntries()
    IDfilelist = [i.id for i in fileList]
    Submissions = [submission.Submission(i.selftext, i.title, i.ups, i.downs, i.author, i.created_utc,
                                         [], i.id, i.link_flair_template_id) for i in Bot.getHotSubreddits()()]
    threads = [threading.Thread(target=lambda q, file, fileList: q.append(
        checkDuplicate(file, fileList)), args=(output, i, IDfilelist)) for i in Submissions]
    runThread(threads)
    output = list(filter(lambda l: l != 0, output))
    Submissions = fileList + output
    output = []
    threads = [threading.Thread(target=lambda output, i, Bot: output.append(
        GetComments(i, Bot)), args=(output, i, Bot, )) for i in Submissions]
    runThread(threads)
    for i,e in enumerate(output):
        Submissions[i].comments = e
    writeFile(Submissions)


def GetComments(post, Bot: redditBot.reddit_bot):
    output = []
    postComments = post.comments
    posts = Bot.getPostById(post.id).comments
    IDfilelist = [i.id for i in postComments]
    Comments = [submission.Comment(i.body, i.ups, i.downs, i.author, i.created_utc,
                                   [], i.id)  for i in posts]
    threads = [threading.Thread(target=lambda q, file, fileList: q.append(
        checkDuplicate(file, fileList)), args=(output, i, IDfilelist)) for i in Comments]
    runThread(threads)
    output = list(filter(lambda l: l != 0, output))
    Comments = postComments + output
    output = []
    threads = [threading.Thread(target=lambda output, i, Bot, parent: output.append(
        GetReplies(i, Bot, parent)), args=(output, i, Bot, posts[e])) for e,i in enumerate(Comments)]
    runThread(threads)
    for i,e in enumerate(output):
        Comments[i].replies = e
    return Comments

def GetReplies(comment, Bot: redditBot.reddit_bot, parent):
    parent.refresh()
    output = []
    postReplies = comment.replies
    IDfilelist = [i.id for i in postReplies]
    Replies = [submission.Reply(i.body, i.ups, i.downs, i.author, i.created_utc,
                                   i.id) for i in parent.replies]
    threads = [threading.Thread(target=lambda q, file, fileList: q.append(
        checkDuplicate(file, fileList)), args=(output, i, IDfilelist)) for i in Replies]
    runThread(threads)
    output = list(filter(lambda l: l != 0, output))
    Replies = postReplies + output
    return Replies


def printSubmissions(object):
    r = ''
    for i in object:
        r += f"""
id:{i.author} at {i.time} wrote this post titled {i.title}, text flair id {i.textFlairId}:
{i.content}\n\n\n
        """
        for j in i.comments:
            r += f"""
id:{j.author} at {j.time} wrote this comment:
{j.content}\n\n
            """
            for z in j.replies:
                r += f"""
id{z.author} at {z.time} wrote this reply:
{z.content}\n
                """
        r += "\n\n\n\n---------------------------------------------------------------------------------\n\n\n\n"
    return r


def updateEntires(Bot):
    createSubmissionObjects(Bot)
    #print(printSubmissions(getEntries()))


if __name__ == "__main__":
    # get authentication details
    with open("authentication.json") as read_file:
        data_dict = json.loads(read_file.read())

    # create bot
    Bot = redditBot.reddit_bot(data_dict, False, "ASR_SG")
    createSubmissionObjects(Bot)
    print(printSubmissions(getEntries()))
