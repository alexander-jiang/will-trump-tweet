import glob
import os
from twitter_fetcher.fetch_recent_tweets import TwitterFetcher
from extract_features import FeatureExtractor

def main():
    # 1. Setup
    fetcher = TwitterFetcher()
    fetcher.new_session()

    # 2. Fetch tweets
    twitter_handle = "realDonaldTrump"
    output_dir = "pipeline_RDT_tweets"
    since_id = ""
    max_id = ""
    if not os.path.exists(output_dir):
        print(f"INFO Creating output dir for TwitterFetcher: {output_dir}")
        os.mkdir(output_dir)
    elif not os.path.isdir(output_dir):
        print(f"ERROR output dir for TwitterFetcher is not a directory = {output_dir}")
        return

    fetcher.get_user_tweets(
        twitter_handle, output_directory=output_dir,
        before_this_tweet_id=max_id, after_this_tweet_id=since_id)

    # 3. Extract features
    tweet_filenames = glob.glob(f"{output_dir}/tweet_ids_*.json")
    feature_extractor = FeatureExtractor()
    features_csv_filename = "pipeline_features.csv"
    feature_extractor.extract_features(tweet_filenames, features_csv_filename)


if __name__ == "__main__":
    main()
