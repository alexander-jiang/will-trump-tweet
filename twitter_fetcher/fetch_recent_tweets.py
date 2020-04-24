import json
from requests_oauthlib import OAuth1Session
from .secrets import Secrets

class TwitterFetcher():
    def __init__(self):
        self.secrets = Secrets()
        self.oauth_session = None
        self.session_ready = False

    def new_session(self):
        client_key = self.secrets.get_consumer_api_key()
        client_secret = self.secrets.get_consumer_api_secret_key()
        callback_uri = 'https://127.0.0.1/callback'

        # Endpoints found in the OAuth provider API documentation
        request_token_url = 'https://api.twitter.com/oauth/request_token'
        authorization_url = 'https://api.twitter.com/oauth/authorize'
        access_token_url = 'https://api.twitter.com/oauth/access_token'

        oauth_session = OAuth1Session(client_key, client_secret=client_secret, callback_uri=callback_uri)

        # First, fetch request token
        print("Fetching request token...")
        print(oauth_session.fetch_request_token(request_token_url))

        # Second, follow this link to authorize
        print("Authorization URL (go to this link in a browser and then copy the redirected URL here):")
        print(oauth_session.authorization_url(authorization_url))

        # Third, fetch the access token
        redirect_response = input("Paste the full redirect URL here:\n")
        print(oauth_session.parse_authorization_response(redirect_response))
        print("Access token:")
        print(oauth_session.fetch_access_token(access_token_url))

        # You can now use the oauth_session object to make OAuth requests.
        self.session_ready = True
        self.oauth_session = oauth_session

    def get_user_tweets(self,
        twitter_handle, output_directory="", before_this_tweet_id="",
        after_this_tweet_id="", tweets_per_batch=200, max_batches=20):
        """
        Calls the GET statuses/user_timeline Twitter API endpoint to fetch
        tweets in batches. Note that this endpoint can only return up to 3200
        of a user's most recent Tweets. See the endpoint docs for more details:
        https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-user_timeline

        Saves the tweets a JSON file in the specified directory. The JSON
        filename will be in the form:
        tweet_ids_{oldest_tweet_id}_to_{newest_tweet_id}.json

        twitter_handle: (string)
            screen name of the user for whom to return results
            (e.g. "realDonaldTrump" for @realDonaldTrump)
        output_directory: (string)
            a path to a directory to store the output JSON files
        before_this_tweet_id: (string)
            fetch tweets with an ID strictly less than (i.e. not inclusive)
            this value (see the "max_id" parameter in the endpoint docs above)
        after_this_tweet_id: (string)
            fetch tweets with an ID greater than or equal to (i.e. inclusive)
            this value (see the "since_id" parameter in the endpoint docs above)
        tweets_per_batch: (integer)
            up to how many tweets can be returned in each batch. Note that
            each request to the endpoint can retrieve up to 200 tweets
            (see the "count" parameter in the endpoint docs above)
        max_batches: (integer)
            the maximum number of requests to make

        Note: the results from this function will include retweets (there is a
        "include_rts" parameter on the Twitter endpoint).
        """
        if not self.session_ready:
            print("OAuth session not ready! Call the new_session() function first")
            return

        newest_tweet_id_so_far = -float('inf')
        oldest_tweet_id_so_far = float('inf')

        max_id = before_this_tweet_id
        since_id = after_this_tweet_id

        all_tweets = []
        all_tweet_ids = set([])

        print(f"Fetching tweets from @{twitter_handle}...")
        for batch_num in range(max_batches):
            print(f"==== BATCH {batch_num+1} OF {max_batches} ====")
            api_url = f"https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name={twitter_handle}&count={tweets_per_batch}&include_rts=true"
            if len(max_id) > 0:
                api_url += "&max_id=" + max_id
            if len(since_id) > 0:
                api_url += "&since_id=" + since_id

            print("API URL:", api_url)
            response = self.oauth_session.get(api_url)

            batch_tweets = response.json()
            batch_tweet_ids = [tweet['id'] for tweet in batch_tweets]
            for tweet_id in batch_tweet_ids:
                if tweet_id in all_tweet_ids:
                    print(f"ERROR: found a duplicate tweet id {tweet_id}")
                    break

            num_tweets = len(batch_tweets)
            if num_tweets > 0:
                all_tweets.extend(batch_tweets)

                newest_tweet_id = batch_tweets[0]['id']
                newest_tweet_time = batch_tweets[0]['created_at']
                oldest_tweet_id = batch_tweets[-1]['id']
                oldest_tweet_time = batch_tweets[-1]['created_at']

                newest_tweet_id_so_far = max(newest_tweet_id_so_far, newest_tweet_id)
                oldest_tweet_id_so_far = min(oldest_tweet_id_so_far, oldest_tweet_id)
                print(f"Retrieved {num_tweets} tweets in this batch")
                print(f"newest tweet id {newest_tweet_id} at time {newest_tweet_time}")
                print(f"oldest tweet id {oldest_tweet_id} at time {oldest_tweet_time}")

                max_id = str(oldest_tweet_id - 1)
            else:
                print("Exiting early, this request returned no tweets")
                break

        print(f"Retrieved {len(all_tweets)} tweets, from ID = {oldest_tweet_id_so_far} to ID = {newest_tweet_id_so_far}")
        tweets_json_filename = f"{output_directory}/tweet_ids_{oldest_tweet_id_so_far}_to_{newest_tweet_id_so_far}.json"
        with open(tweets_json_filename, "w", encoding="utf8") as f:
            json.dump(all_tweets, f)

        self.reset_session()

    def reset_session(self):
        self.session_ready = False
        self.oauth_session = None
