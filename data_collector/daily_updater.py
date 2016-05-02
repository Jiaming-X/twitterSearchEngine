#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This small program is to count the number of tweets of each company
update the number and score in tcount collection for each company
'''

from senti_classifier import senti_classifier
from nltk.corpus import stopwords
from pymongo import MongoClient
import pandas as pd
import datetime
import time
import json
import os
import re

# Mongo config
client = MongoClient()
client = MongoClient('mongodb://localhost:27017/')

# Sample the tweets 1/sample
SAMPLE = 100
TIMESLOT = 10
CURRDATE = str(datetime.datetime.now().date())

# Update date and score infomation in MongoDB
def Count_Update(company, score):
    query_collection = getattr(client.twitterData, company)
    update_collection = client.twitterData.tcount
    end = CURRDATE + " 24"
    start = CURRDATE
    count = query_collection.find({'time': {'$gte': start, '$lt': end}}).count()
    record = {"company":company,"count":count,"date":CURRDATE,"score":score}
    result = update_collection.insert_one(record)
    return


# Read csv and modify date for later process
def read(a):
    tweet = pd.read_csv(a)
    date = tweet['time']
    text = tweet['text']
    day = pd.to_datetime(date,format = '%Y-%m-%d %H:%M:%S.%f')
    day = day.map(lambda x: x.strftime('%Y-%m-%d'))
    text = map(lambda x: [x], text)
    tweet = pd.DataFrame(text, index = day, columns = ['text'])
    return tweet


# Caculate score by using senti_classifier
def sentiment_score(dataset, sample):
    count = pos_sum = neg_sum = 0
    for sentence in dataset:
        if count%sample==0:
            pos_score, neg_score = senti_classifier.polarity_scores([sentence])
            #print "pos_score: " + str(pos_score) + "  neg_score" + str(neg_score)
            pos_sum += pos_score
            neg_sum += neg_score
        count += 1
    sum_val = pos_sum + neg_sum
    pos_score,neg_score = pos_sum/max(0.0000001,sum_val),neg_sum/max(0.0000001,sum_val)
    return pos_score - neg_score

# Create a loop to get the clean text
def corpus(sub):
    num_text=sub['text'].size
    cleantext=[]
    for i in xrange(0,num_text):
        cleantext.append(words(sub['text'][i]))
    return cleantext

# Pre-process the text
def words(text):
    text=re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', \
    '',text,flags=re.MULTILINE)
    letters=re.sub('[^a-zA-Z]', ' ', text)
    words=letters.lower().split()
    stop=set(stopwords.words('english'))
    meanfulwords=[w for w in words if not w in stop]
    return(' '.join(meanfulwords))

# Mian function
def query_and_process(company):
    # Query data
    query = "mongoexport -h 127.0.0.1:27017 -d twitterData -c " + company + " --type=csv --fields time,text -q '{ \"time\": { $gt: \"" + CURRDATE + "\", $lt: \"" + CURRDATE + " 24:00\" } }' --out " + company + ".csv"
    print query
    os.system(query)
    time.sleep(TIMESLOT)
    # Read data
    tweet = read(company + ".csv")
    sub = tweet.loc[CURRDATE]
    # Pre-process Data
    sub=corpus(sub)
    # Get score
    score = sentiment_score(sub,SAMPLE)
    print str(score)
    # Update DB
    Count_Update(company,score)
    os.system("rm -f " + company + ".csv")
    return


# Save daily tweets as csv
CURRDATE = '2016-05-01' #hardcode update date
print "\n-----------PROCESSING-----------    "+CURRDATE

names = ["amazon"]
map(query_and_process, names)
print "finished"

''' if want to caculate mutiple days. Use following:
hard_code_time = '2016-03-29'
timearry = [hard_code_time[:-2]+str(int(hard_code_time[-2:])+i) for i in range(13) ]
for t in timearry:
    CURRDATE = t
    print CURRDATE
    map(query_and_process, names)
    print "finished"
'''