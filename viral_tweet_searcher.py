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
# export "BEARER_TOKEN"="ABCDE......7kdfhlk3N" (your bearer token in its entirety)

# The program takes a while to execute, because connecting to the twitter API happens
# multiple times and volume of tweets is large.

class bcolors:
	PURPLE = '\033[95m'
	OKBLUE = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	ENDC = '\033[0m'
	TITLE = '\033[1;37;45m'


def create_searcher_url(search_for):
	if not search_for:
		search_for = "Tom Girardi"
	url_beginning = "https://api.twitter.com/2/tweets/search/recent?query="
	return url_beginning + search_for

# Defines the parameters which will be included in the API response. If this function
# receives an argument which is not null, it will return the 'basic_parameters' dictionary
# and 'optionals' dictionary merged into one. Otherwise, it will return the dict of
# 'basic_parameters'
def get_params(optionals=None):
	basic_parameters = {"tweet.fields":"text,public_metrics,author_id,id,created_at,referenced_tweets"}
	return basic_parameters | optionals if optionals else basic_parameters


def handle_bearer_oauth():
	bearer_token = os.environ.get("BEARER_TOKEN")
	headers = dict()
	headers["Authorization"] = f"Bearer {bearer_token}"
	return headers

# Connects to the twitter API to collect the information we request for and
# if all goes well, returns the response in json format. This function is modeled
# after the official example code bit on 'Twitter-API-v2-sample-code' github.
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

# We loop through our tweets and determining if the tweet is the original tweet that has
# been retweeted over 20 times, in which case the tweet will not include a
# 'referenced_tweets' field because it is an original tweet. If however the tweet being 
# analysed is a retweet, the id of the referenced tweet is sent to 
# 'get_original_tweet_from_id()' to connect to the endpoint again and receive information
# on that specific tweet. Before saving the tweet into the 'retweeted' list, the
# list is looped through to check for possible duplicates.
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

# Collects username using the 'author_id' and connecting to the endpoint once again
def get_author_username(tweets):
	for tweet in tweets:
		url = "https://api.twitter.com/2/users/{}".format(tweet["author_id"])
		ret = connect_to_endpoint(url, None)
		tweet["author_info"] = ret["data"]
	return tweets

# Prints the title of the search, and each tweet in the following format:
# @username, name, date and time of tweet, the tweet itself and the number of times it
# was retweeted.
def format_and_print_viral_tweets(tweets, title=None):
	if not title:
		title = "the Tom Girardi scandal"
	print(bcolors.TITLE + "\nCurrent viral tweets mentioning " + title + ":" + bcolors.ENDC + '\n')
	if not tweets:
		print("No", bcolors.OKGREEN + "viral", bcolors.ENDC + "tweets were found including \"" + bcolors.OKCYAN + title + bcolors.ENDC + "\"\n")
	for tweet in tweets:
		date = dateutil.parser.isoparse(tweet["created_at"]) # ISO 8601 extended format to datetime.datetime object
		date = date.replace(tzinfo=timezone.utc).astimezone(tz=None) #change timezone from UTC to local
		print(bcolors.OKCYAN + '@' + tweet["author_info"]["username"] + bcolors.ENDC, "(" + bcolors.OKBLUE + 
		tweet["author_info"]["name"] + bcolors.ENDC + ")", "writes at", bcolors.PURPLE + str(date) + bcolors.ENDC + ":\n", tweet["text"], 
		bcolors.OKGREEN + "\nRetweeted" + bcolors.ENDC, tweet["public_metrics"]["retweet_count"], bcolors.OKGREEN + "times\n" + bcolors.ENDC)

# From the main function we will try to connect to the API endpoint two times, if we
# get the information (by receiving a 'next_token' from the first connection response)
# that there are more than 100 results corresponding to our request. So, at most we will
# receive 200 tweets to analyse.
def main():
	search_for = sys.argv[1] if len(sys.argv) > 1 else None
	url = create_searcher_url(search_for)
	params = get_params({"max_results":100,'next_token': {}})
	json_response = connect_to_endpoint(url, params)
	if json_response["meta"]["result_count"] == 0:
		print("\nNo tweets were found including the phrase \"" + bcolors.OKCYAN + search_for + bcolors.ENDC + "\"\n")
		exit(0)
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
