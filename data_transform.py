import csv
from datetime import datetime
import glob
import json
import numpy as np
import matplotlib.pyplot as plt
import pytz

from twitter_fetcher.tweet_features import TweetFeatures

eastern_tz = pytz.timezone('US/Eastern')

csv_out_filename = "realDonaldTrump_tweets/features.csv"
csvfile = open(csv_out_filename, "w", newline='', encoding="utf8")
csv_writer = csv.DictWriter(csvfile, fieldnames=TweetFeatures.get_field_names(), quoting=csv.QUOTE_NONNUMERIC)
csv_writer.writeheader()

total_num_tweets = 0
filenames = glob.glob("realDonaldTrump_tweets/*.json")
for filename in filenames:
    with open(filename, "r", encoding="utf8") as f:
        tweets_json = json.load(f)

    total_num_tweets += len(tweets_json)

    for tweet in tweets_json:
        tweet_datetime = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S %z %Y")
        eastern_time = tweet_datetime.astimezone(eastern_tz)
        print(f"tweet id {tweet['id']} at {eastern_time}")

        tweet_features = TweetFeatures(tweet)
        csv_writer.writerow(tweet_features.as_dict())

csvfile.close()
