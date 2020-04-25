import glob
import json
from twitter_fetcher.tweet_features import TweetFeatures

class MergeTweetFiles():
    def __init__(self):
        pass

    def merge_tweet_files(self,
        tweet_filenames, merged_out_filename):
        """
        Merges tweets from different JSON files into a single JSON file.

        tweet_filenames: (list of strings)
            list of filepaths of Tweet JSON files to extract features from
        merged_out_filename: (string)
            a path to the JSON output file to store all tweets
        """
        tweet_ids = set([])
        merged_tweets = {}

        for filename in tweet_filenames:
            print(f"reading tweets from {filename}")
            with open(filename, "r", encoding="utf8") as f:
                tweets_json = json.load(f)

            for tweet in tweets_json:
                tweet_features = TweetFeatures(tweet)
                if tweet_features.id in merged_tweets:
                    print(f"found duplicate tweet ID! {tweet_features.id}")
                    print(f"this tweet JSON = {tweet}")
                    print(f"the existing tweet JSON = {merged_tweets[tweet_features.id]}")
                    choice = input("Press (1) for this tweet, (2) for the existing tweet: ")
                    if choice == "2":
                        continue
                    elif choice == "1":
                        merged_tweets[tweet_features.id] = tweet
                        continue
                    else:
                        print(f"invalid choice, replacing the tweet")
                        merged_tweets[tweet_features.id] = tweet
                        continue
                merged_tweets[tweet_features.id] = tweet

        tweets_list = [merged_tweets[id] for id in merged_tweets]
        with open(merged_out_filename, "w", encoding="utf8") as f:
            json.dump(tweets_list, f)

def main():
    tweet_filenames = []
    tweet_filenames.extend(glob.glob("pipeline_RDT_tweets/tweet_ids_*.json"))
    tweet_filenames.extend(glob.glob("premium_RDT_tweets/merged_*.json"))

    output_filename = "master_full_tweets.json"

    merger = MergeTweetFiles()
    merger.merge_tweet_files(tweet_filenames, output_filename)

if __name__ == "__main__":
    main()
