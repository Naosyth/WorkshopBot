import warnings
def fxn():
    warnings.warn("deprecated", DeprecationWarning)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fxn()

import praw
import re
from pprint import pprint
import shelve
import lxml.html
import time

submissions_replied_to = shelve.open("links")
comments_replied_to = shelve.open("comments")

r = praw.Reddit(user_agent='Direct Workshop Linker by /u/Naosyth')
r.login('WorkshopBot', 'ILikeTurtles!', disable_warning=True)

message_start = "Direct Steam links (opens in Steam instead of an internet browser):\n\n"
message_end = "\n\nQuestions/comments? Message my maker, /u/Naosyth"

def linkToWorkshop(id, title):
	return "[" + title + "](steam://url/CommunityFilePage/" + id + ")"

while True:
	submissions = r.get_subreddit('spaceengineers').get_hot(limit=10)
	for submission in submissions:
		submission_id = submission.id
		submission_url = submission.url

		if submission_id not in submissions_replied_to:
			if "http://steamcommunity.com/sharedfiles/filedetails/?id=" in submission_url:
				workshop_id = re.search('\d+$', submission_url).group(0)
				workshop_title = lxml.html.parse("http://steamcommunity.com/sharedfiles/filedetails/?id=" + workshop_id).find(".//title").text

				if workshop_title.split()[1] == "Workshop":
					submission.add_comment(message_start + linkToWorkshop(workshop_id, workshop_title) + message_end)
					print("Proving links to submission: " + submission.permalink)
					time.sleep(600)
					submissions_replied_to[submission_id] = True

			if submission.selftext != "":
				query = re.compile('filedetails/\?id=(\d+)')
				workshop_links = re.finditer(query, submission.selftext)

				message = ""
				for link in workshop_links:
					workshop_id = link.group(1)
					workshop_title = lxml.html.parse("http://steamcommunity.com/sharedfiles/filedetails/?id=" + workshop_id).find(".//title").text
					if workshop_title.split()[1] == "Workshop":
						message += linkToWorkshop(workshop_id, workshop_title) + "\n\n"
				if message != "":
					message = message_start + message + message_end
					submission.add_comment(message)
					print("Proving links to submission: " + submission.permalink)
					time.sleep(600)
					submissions_replied_to[submission_id] = True

		comments = submission.comments
		for comment in comments:
			comment_id = comment.id

			if comment_id not in comments_replied_to:
				query = re.compile('filedetails/\?id=(\d+)')
				workshop_links = re.finditer(query, comment.body)

				message = ""
				for link in workshop_links:
					workshop_id = link.group(1)
					workshop_title = lxml.html.parse("http://steamcommunity.com/sharedfiles/filedetails/?id=" + workshop_id).find(".//title").text
					if workshop_title.split()[1] == "Workshop":
						message += linkToWorkshop(workshop_id, workshop_title) + "\n\n"
				if message != "":
					message = message_start + message + message_end
					comment.reply(message)
					print("Proving links to comment in submission: " + submission.permalink)
					time.sleep(600)
					comments_replied_to[comment_id] = True

	time.sleep(1800)
	print("tick tock")

submissions_replied_to.close()
comments_replied_to.close()
