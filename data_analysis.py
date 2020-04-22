from datetime import datetime
import glob
import json
import numpy as np
import matplotlib.pyplot as plt
import pytz

eastern_tz = pytz.timezone('US/Eastern')

week_hourly_buckets = []
for i in range(24*7):
    week_hourly_buckets.append(0)
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

        weekday_idx = eastern_time.weekday() # Note Monday = 0, Sunday = 6
        hour_idx = weekday_idx * 24 + eastern_time.hour
        week_hourly_buckets[hour_idx] += 1

hourly_tick_labels = [
    "Mo", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11",
    "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23",
    "Tu", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11",
    "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23",
    "We", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11",
    "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23",
    "Th", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11",
    "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23",
    "Fr", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11",
    "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23",
    "Sa", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11",
    "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23",
    "Su", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11",
    "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"
]

x = np.arange(len(week_hourly_buckets))
plt.figure(figsize=(100, 30))

plt.bar(x, week_hourly_buckets, align='edge')
plt.xticks(x, hourly_tick_labels, rotation='vertical')
plt.title(f"@realDonaldTrump last n={total_num_tweets} tweets (Eastern time)")
plt.show()
