import glob
import os
from twitter_fetcher.fetch_recent_tweets import TwitterFetcher
from twitter_fetcher.fetch_premium_api import TwitterPremiumSearchFetcher
from merge_tweet_files import MergeTweetFiles
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

    # TODO haven't tested steps 3a/3b & 4 in a full end-to-end run of the pipeline
    # # 3a. Fetch tweets from premium full-archive API
    # premium_output_dir = "premium_RDT_tweets"
    # fetch_from_premium_api(premium_output_dir)

    # # 3b. Merge tweets:
    # tweet_filenames = []
    # tweet_filenames.extend(glob.glob(f"{output_dir}/tweet_ids_*.json"))
    # tweet_filenames.extend(glob.glob(f"{premium_output_dir}/merged_*.json"))
    # merged_output_filename = "master_full_tweets.json"
    # merge_tweet_files(tweet_filenames, merged_output_filename)

    # 4 (alt). If you merged tweets,
    # master_json_filename = [merged_output_filename,]
    # feature_extractor = FeatureExtractor()
    # master_features_csv_filename = "master_features.csv"
    # feature_extractor.extract_features(master_json_filename, master_features_csv_filename)

    # 4. Extract features
    tweet_filenames = glob.glob(f"{output_dir}/tweet_ids_*.json")
    feature_extractor = FeatureExtractor()
    features_csv_filename = "pipeline_features.csv"
    feature_extractor.extract_features(tweet_filenames, features_csv_filename)


def fetch_from_premium_api(output_dir):
    user_id = "25073877"
    # dates below are in the format YYYYMMDDhhmm
    from_date = "201701200000" # assume Jan 20, 2017 midnight UTC is the start of Trump's presidency
    to_date = "202001100205"

    if not os.path.exists(output_dir):
        print(f"INFO Creating output dir for TwitterPremiumSearchFetcher: {output_dir}")
        os.mkdir(output_dir)
    elif not os.path.isdir(output_dir):
        print(f"ERROR output dir for TwitterPremiumSearchFetcher is not a directory = {output_dir}")
        return

    # use the 30-day endpoint while testing as it has higher rate limit than the full-archive API
    use_full_archive = True

    # The max results per request is 100 for Sandbox (500 if you have Premium subscription)
    results_per_request = 100
    max_requests = 50

    # sleep for 2 seconds between each request to avoid exceeding the
    # 30 requests per minute rate limit
    sleep_time = 2.0

    premium_fetcher = TwitterPremiumSearchFetcher()
    premium_fetcher.get_user_tweets(
        user_id, from_date, to_date, output_directory=output_dir,
        use_full_archive=use_full_archive, results_per_request=results_per_request,
        max_requests=max_requests, sleep_btwn_requests=sleep_time)

def merge_tweet_files(tweet_filenames, merge_output_filename):
    merger = MergeTweetFiles()
    merger.merge_tweet_files(tweet_filenames, merge_output_filename)

if __name__ == "__main__":
    main()
