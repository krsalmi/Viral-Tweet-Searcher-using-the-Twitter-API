# Viral-Tweet-Searcher-using-the-Twitter-API
## What and Why?
I created this program while I was studying APIs and how they work. I decided to take a closer look at the Twitter API 
because the interface always requires some sort of authentication, a process I was also interested to learn more about.  
  
The program I wrote searches for viral tweets (in this case meaning tweets that have been retweeted
at least 20 times) on a particular subject, which is obtained from the command line. If no command line argument is given, the program will search for
viral tweets regarding the 'Tom Girardi' scandal, which is heavily covered on the hit TV show, the
Real Housewives of Beverly Hills.

## How...
### &nbsp;&nbsp;does it work?
If command line arguments are given, the first one after the name of the program will be saved as the phrase to be searched for. If no
arguments are given, 'search_for' will be "Tom Girardi". After creating the url needed for the search (which will allow the search for a random sample of 
current tweets) and defining a dictionary of parameters (which includes,
for example, a result count of 100), the actual connecting to the Twitter API happens in __connect_to_endpoint()__ with a "GET" request.
If all goes well, the response is returned in json format. In the case that the status code of the response wasn't "Ay OK" 200, an exception is raised.
Connecting this way will actually take place twice, if the response includes a 'next_token' hinting that more than the initial 100 results exist. If no 
resulting  tweets have been discovered, the program will print out a statement and exit.  
  
After, the tweets are loop through, and the ones that have been retweeted more than 20 times will be looked at more closely. Each one of these is checked 
to see if that tweet is the original tweet, which has been retweeted multiple times, or just a retweet. If the tweet is an original, it is directly saved
into our new 'retweeted' list. If, however, the tweet under analysis is a retweet, the id of the referenced tweet is sent to 
__get_original_tweet_from_id()__ to connect to the endpoint again and receive information on that specific tweet. Before saving the tweet 
into the 'retweeted' list, the list is looped through to check for possible duplicates.

Next, the list of saved retweeted tweets is looped through again and a new connection to the Twitter endpoint is established in order to get the username 
and name of the author of each tweet. Finally, the results will be formatted and printed in the following format: @username, name, date and time of tweet, the 
tweet itself and the number of times it was retweeted.

### &nbsp;&nbsp;to use this program?
First of all, to use this program, you need a Twitter API developer bearer token.
To use your token, run the following line in your terminal:
`export "BEARER_TOKEN"="ABCD......7kdfhlk3N"` (your bearer token in its entirety)
  
To execute the program in default "Tom Girardi" mode, run `python3 viral_tweet_searcher.py`
To search for something of your own, run `python3 viral_tweet_searcher "I love Taco Bell"` (or whatever you feel like searching for).
