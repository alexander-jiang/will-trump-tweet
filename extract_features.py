import csv
from datetime import datetime
import json
import pytz

from twitter_fetcher.tweet_features import TweetFeatures

class FeatureExtractor():
    def __init__(self):
        pass

    def extract_features(self,
        tweet_filenames, csv_out_filename):
        """
        Extracts features from the Tweet JSON using the TweetFeatures class.

        tweet_filenames: (list of strings)
            list of filepaths of Tweet JSON files to extract features from
        csv_out_filename: (string)
            a path to the CSV output file to store extracted features
        """
        eastern_tz = pytz.timezone('US/Eastern')

        csvfile = open(csv_out_filename, "w", newline='', encoding="utf8")
        csv_writer = csv.DictWriter(csvfile, fieldnames=TweetFeatures.get_field_names(), quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writeheader()

        total_num_tweets = 0
        tweet_ids = set([])

        for filename in tweet_filenames:
            print(f"reading tweets from {filename}")
            with open(filename, "r", encoding="utf8") as f:
                tweets_json = json.load(f)

            total_num_tweets += len(tweets_json)
            for tweet in tweets_json:
                tweet_datetime = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S %z %Y")
                eastern_time = tweet_datetime.astimezone(eastern_tz)
                # print(f"tweet id {tweet['id']} at {eastern_time}")

                tweet_features = TweetFeatures(tweet)
                if tweet_features.id in tweet_ids:
                    print(f"ERROR found duplicate tweet ID! {tweet_features.id}")
                    break
                tweet_ids.add(tweet_features.id)

                csv_writer.writerow(tweet_features.as_dict())

        csvfile.close()
        print(f"extracted features for {total_num_tweets} tweets to {csv_out_filename}")

def main():
    tweet_filenames = []
    tweet_filenames.append("master_full_tweets.json")

    output_filename = "master_features.csv"

    feature_extractor = FeatureExtractor()
    feature_extractor.extract_features(tweet_filenames, output_filename)

if __name__ == "__main__":
    main()
