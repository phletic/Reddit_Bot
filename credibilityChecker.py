from submissionCollector import getEntries
from bs4 import BeautifulSoup
import requests
import re
import pickle
import threading
import json
import redditBot
message = """
Hello, we have detected a link that may harm our subreddit. Our friendly moderators will review this post as soon as possible! If its fine, it'll still be up and running, else, we will take it down! Thank you redditors~ ASR_BOT
"""
httpDeduction = 50
unwantedURLDeduction = 100
urlRegex = r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"


def writeVisited(id):
    file = readVisited()
    open('submissions.redd', 'w').close()
    with open("Visited.credibleWeb", "wb") as submissionFile:
        pickle.dump([id]+file, submissionFile)


def readVisited():
    objects = []
    # open file
    with open("Visited.credibleWeb", "rb") as submissionFile:
        # attempt to read
        try:
            objects = pickle.load(submissionFile)
        # return empty list if database is empty
        except EOFError:
            objects = []
    return objects


def runThread(_thread):
    for i in _thread:
        i.run()
    for i in _thread:
        if i.is_alive():
            i.join()


def checkCredible(Bot):
    visitedIdList = readVisited()
    print(visitedIdList)
    allPosts =  getEntries()
    getUnwatnedURL()
    threads = [threading.Thread(
        target=searchSubmission, args=(i, Bot,visitedIdList)) for i in allPosts]
    runThread(threads)
    print(readVisited())


def searchSubmission(text, Bot,visitedIdList):
    if text not in visitedIdList:
        q = []
        id = text.id
        content = text.content
        urls = [match.group() for match in re.finditer(urlRegex, content)]
        threads = [threading.Thread(target=lambda q, args: q.append(
            isSafe(args)), args=(q, i,)) for i in urls]
        runThread(threads)
        print("new")
        if False in q:
            print(text.title, " = unsafe")
            Bot.getPostById(id).reply(message)
        writeVisited(id)
    threads = [threading.Thread(
        target=searchComments, args=(i, Bot,visitedIdList)) for i in text.comments]
    runThread(threads)    

def searchComments(text,Bot,visitedIdList):
    if text not in visitedIdList:
        q = []
        id = text.id
        content = text.content
        urls = [match.group() for match in re.finditer(urlRegex, content)]
        threads = [threading.Thread(target=lambda q, args: q.append(
            isSafe(args)), args=(q, i,)) for i in urls]
        runThread(threads)
        print("new")
        if False in q:
            print(text.title, " = unsafe")
            Bot.getPostById(id).reply(message)
        writeVisited(id)
    threads = [threading.Thread(
        target=searchReplies, args=(i, Bot,visitedIdList)) for i in text.replies]
    runThread(threads) 

def searchReplies(text,Bot,visitedIdList):
    if text not in visitedIdList:
        q = []
        id = text.id
        content = text.content
        urls = [match.group() for match in re.finditer(urlRegex, content)]
        threads = [threading.Thread(target=lambda q, args: q.append(
            isSafe(args)), args=(q, i,)) for i in urls]
        runThread(threads)
        print("new")
        if False in q:
            print(text.title, " = unsafe")
            Bot.getPostById(id).reply(message)
        writeVisited(id)

def isSafe(input):
    url = f"https://www.mywot.com/scorecard/{input}"
    total = 0
    # check if is safe
    response = requests.get(url=url).content
    soup = BeautifulSoup(response, "html5lib")
    scores = soup.find_all("div", {
                           "class": "hBCQsP"})
    for i in scores:
        total += int(i.getText())
    parsed = parseWeb(input)
    if parsed[0] == "http":
        total -= httpDeduction
    if parsed in unwantedURLList:
        total -= unwantedURLDeduction
    return True if total > 170 else False


def parseWeb(url):
    # output [http/https] [web name] [com/net/whatever]
    properContruct = []
    parsed = url.split(".")
    parsed[0] = parsed[0].split("//")
    parsed[1] = parsed[1].split("/")
    properContruct.append(parsed[0][0])
    if isinstance(parsed[0], list):
        if parsed[0][1] == "www":
            properContruct.append(''.join(parsed[1]))
            properContruct.append(''.join(parsed[2]))
        else:
            properContruct.append(''.join(parsed[0][1]))
            properContruct.append(''.join(parsed[1]))
    else:
        properContruct.append(parsed[0][1])
        properContruct.append(''.join(parsed[1]))
    return properContruct


def getUnwatnedURL():
    webnames = []
    with open("blacklist.txt", "r") as file:
        webnames = [line.strip()[:-1] for line in file]
    for e, i in enumerate(webnames):
        webnames[e] = parseWeb(i)
    global unwantedURLList
    unwantedURLList = webnames
    return


if __name__ == "__main__":
    # get authentication details
    with open("authentication.json") as read_file:
        data_dict = json.loads(read_file.read())

    # create bot
    Bot = redditBot.reddit_bot(data_dict, False, "ASR_SG")
    checkCredible(Bot)
