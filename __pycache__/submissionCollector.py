import json
import submission
import redditBot
import pickle
import threading
import queue


# get authentication window
with open("authentication.json") as read_file:
    data_dict = json.loads(read_file.read())

# create bot
Bot = redditBot.reddit_bot(data_dict, False, "ASR_SG")


# run thread
def runThread(_thread):
    for i in _thread:
        i.run()
    for i in _thread:
        if i.is_alive():
            i.join()

# scrape submissions


def retrieveSubmissions():
    return [i.id for i in Bot.getHotSubreddits()()]


def getAllID():
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


def UpdateDataBase(submissions, remove=None):
    global toAppend
    toAppend = []
    # get current list of submissions
    readFile = getAllID()
    # check for repeats
    threads = [threading.Thread(target=checkDuplicate, args=(
        i, readFile,)) for i in submissions]
    runThread(threads)
    # update database
    obj = readFile + toAppend
    print(obj)
    print(remove)
    if remove is not None:
        obj.remove(remove)
    with open("submissions.redd", "wb") as submissionFile:
        pickle.dump(obj, submissionFile)
    del toAppend


def checkDuplicate(i, readFile):
    if i in readFile:
        return
    else:
        toAppend.append(i)


output = queue.Queue()


def tokenizeSubmissions(submissionIDs):
    submissionDict = {str(id): 0 for id in submissionIDs}
    threads = [threading.Thread(target=lambda q, arg1: q.put(
        retreiveInfomation(arg1)), args=(output, id)) for id in submissionDict]
    runThread(threads)
    while not output.empty():
        result, id = output.get()
        if result == 0:
            print("change")
            UpdateDataBase(submissionIDs, remove=id)
            return tokenizeSubmissions(submissionIDs=getAllID())
        submissionDict[id] = result
    return submissionDict


def retreiveInfomation(id: str):
    submissionStream = Bot.getPostById(id)
    commentStream = submissionStream.comments.replace_more(limit=None)
    comments = []
    for i in commentStream:
        comments.append(submission.Comment(i.body, i.ups, i.downs, i.author.id, i.created_utc,
                                           [submission.reply(
                                            j.body, j.ups, j.downs, j.author.id, j.created_utc, j.id) for j in i.replies.replace_more(limit=None)],
                                            i.id))
    try:
        submissionbject = submission.Submission(submissionStream.selftext, submissionStream.title, submissionStream.ups,
                                                submissionStream.downs, submissionStream.author.id, submissionStream.created_utc,
                                                comments, submissionStream.id)
    except AttributeError:
        return 0, id
    return submissionbject, id


def printSubmissions(object):
    r = ''
    for i in object.values():
        r += f"""
id:{i.author} at {i.time} wrote this post:
{i.content}\n\n\n
        """
        for j in i.comments:
            r += f"""
id:{j.author} at {j.time} wrote this comment:
{j.content}\n\n
            """
            for z in j.replies:
                r += f"""
id{z.author} at {z.time} wrote this comment:
{z.content}\n
                """
        r += "\n\n\n\n---------------------------------------------------------------------------------\n\n\n\n"
    return r


UpdateDataBase(retrieveSubmissions())
object = tokenizeSubmissions(getAllID())
print(object)
print(printSubmissions(object))
