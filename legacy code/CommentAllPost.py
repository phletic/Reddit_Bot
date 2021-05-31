import json
import redditBot
from profanity import profanity

with open("authentication.json") as read_file:
    data_dict = json.loads(read_file.read())

        
limitThrottle = 2
Bot = redditBot.reddit_bot(data_dict,False, "ASR_SG")

def message(title, text):
    r = 'Hello there! Thank you for taking some time off to post on ASR_SG. Every submission will contribute to the growth of this new subreddit.\n'
    isVulgar = profanity.contains_profanity(title+text)
    bad = False
    if isVulgar == True:
        if bad == False: 
            r += "However, there is some thing that you need to note:"
        bad = True
        r += "Ensure that your submission uses polite language. We detect the use of profanities in your post. Next time, do censor such hurtful language.\n"
    r+= "Thank you and have a great day!"
    return r
submissions = Bot.subredditCommand("new")(limit=limitThrottle)

for i in submissions:
    text = message(i.title, i.selftext)
    i.reply(text)