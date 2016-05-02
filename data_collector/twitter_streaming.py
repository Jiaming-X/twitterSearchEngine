#!/usr/bin/env python

import tweepy
import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from utility import CUSTOMER_KEY, CUSTOMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET


consumer_key = CUSTOMER_KEY
consumer_secret = CUSTOMER_SECRET

access_token = ACCESS_TOKEN
access_token_secret = ACCESS_SECRET

class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        #print(data)
        print '\n'
        parsed = json.loads(data)
        print json.dumps(parsed, indent=4, sort_keys=True)
        return True

    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, l)
    stream.filter(track=['bull market'])
    #stream.filter(track=['python'])

# write to file
#with open('FILE_DIR_YOUR_WANT_TO_WRITE', 'a') as thefile:
#    for item in searched_tweets:
#        text = unicodedata.normalize('NFKD', item.text).encode('ascii', 'ignore')
#        thefile.write("followers:{0}, statuses:{1}, favorites:{2}, retweeted:{3}, text:{4}\n".format(
#            item.user.followers_count, item.user.statuses_count, item.favorite_count, item.retweet_count, text))

#sys.exit()
