import sys
import requests
import os
import json
from datetime import datetime, timezone
import dateutil.parser

#This is a program to search for viral tweets (meaning tweets that have been retweeted
# at least 20 times) on a particular subject, which is the first command line argument
# after this program's name. If no argument is given, the program will search for
# viral tweets regarding the 'Tom Girardi' scandal, which is heavily covered on
# Real Housewives of Beverly Hills.

# To use this program, you need a Twitter API developer bearer token.
# To use your token, run the following line in your terminal:
# export "BEARER_TOKEN"="AAAAA......7kdfhlk3N" (your bearer token in its entirety)

class bcolors:
	PURPLE = '\033[95m'
	OKBLUE = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	TITLE = '\033[1;37;45m'


def create_searcher_url(search_for):
	if not search_for:
		search_for = "Tom Girardi"
	url_beginning = "https://api.twitter.com/2/tweets/search/recent?query="
	return url_beginning + search_for


def get_params(optionals=None):
	basic_parameters = {"tweet.fields":"text,public_metrics,author_id,id,created_at,referenced_tweets"}
	return basic_parameters | optionals if optionals else basic_parameters


def handle_bearer_oauth():
	bearer_token = os.environ.get("BEARER_TOKEN")
	headers = dict()
	headers["Authorization"] = f"Bearer {bearer_token}"
	return headers


def connect_to_endpoint(url, params):
	headers = handle_bearer_oauth()
	response = requests.request("GET", url, headers=headers, params=params)
	if response.status_code != 200:
		raise Exception(
			"Request returned an error: {} {}".format(
				response.status_code, response.text
			)
		)
	return response.json()

def get_original_tweet_from_id(id):
	url = "https://api.twitter.com/2/tweets/{}".format(id)
	params = get_params()
	return connect_to_endpoint(url, params)

def save_original_retweeted_tweets(tweets):
	retweeted = list()
	already_exists = 0
	for tweet in tweets:
		if tweet["public_metrics"]["retweet_count"] >= 20:
			if "referenced_tweets" in tweet:
				orig_tweet = get_original_tweet_from_id(tweet["referenced_tweets"][0]["id"])["data"]
			else:
				orig_tweet = tweet
			for retweet in retweeted:
				if retweet["id"] == orig_tweet["id"]:
					already_exists = 1
			if not already_exists:
				retweeted.append(orig_tweet)
			else:
				already_exists = 0
	return retweeted

def get_author_username(tweets):
	for tweet in tweets:
		url = "https://api.twitter.com/2/users/{}".format(tweet["author_id"])
		ret = connect_to_endpoint(url, None)
		tweet["author_info"] = ret["data"]
	return tweets

def format_and_print_viral_tweets(tweets, title=None):
	if not title:
		title = "the Tom Girardi scandal"
	print(bcolors.TITLE + "\nCurrent viral tweets mentioning " + title + ":" + bcolors.ENDC + '\n')
	for tweet in tweets:
		date = dateutil.parser.isoparse(tweet["created_at"]) # ISO 8601 extended format to datetime.datetime object
		date = date.replace(tzinfo=timezone.utc).astimezone(tz=None) #change timezone from UTC to local
		print(bcolors.OKCYAN + '@' + tweet["author_info"]["username"] + bcolors.ENDC, "(" + bcolors.OKBLUE + 
		tweet["author_info"]["name"] + bcolors.ENDC + ")", "writes at", bcolors.PURPLE + str(date) + bcolors.ENDC + ":\n", tweet["text"], 
		bcolors.OKGREEN + "\nRetweeted" + bcolors.ENDC, tweet["public_metrics"]["retweet_count"], bcolors.OKGREEN + "times\n" + bcolors.ENDC)


def main():
	search_for = sys.argv[1] if len(sys.argv) > 1 else None
	url = create_searcher_url(search_for)
	params = get_params({"max_results":100,'next_token': {}})
	json_response = connect_to_endpoint(url, params)
	collected_tweets = json_response["data"]
	if "next_token" in json_response["meta"]:
		params["next_token"] = json_response["meta"]["next_token"]
		page2 = connect_to_endpoint(url, params)
		collected_tweets += page2["data"]
	retweeted = save_original_retweeted_tweets(collected_tweets)
	retweeted_with_usernames = get_author_username(retweeted)
	format_and_print_viral_tweets(retweeted_with_usernames, search_for)

if __name__ == "__main__":
	main()
