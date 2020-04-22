from requests_oauthlib import OAuth1Session
from .secrets import Secrets

secrets = Secrets()
client_key = secrets.get_consumer_api_key()
client_secret = secrets.get_consumer_api_secret_key()
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

before_this_tweet_id = "1212181341078458368" # NOTE that "max_id" is an inclusive parameter!
after_this_tweet_id = "" # NOTE that "since_id" is not inclusive!
twitter_handle = "realDonaldTrump"
tweets_per_request = 200 # max is 200 per request

num_batches = 20 # this API endpoint only exposes the past 3200 tweets
for batch_num in range(num_batches):
    print(f"==== BATCH {batch_num+1} OF {num_batches} ====")
    api_url = f"https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name={twitter_handle}&count={tweets_per_request}&include_rts=true&trim_user=1"
    if len(before_this_tweet_id) > 0:
        api_url += "&max_id=" + before_this_tweet_id
    if len(after_this_tweet_id) > 0:
        api_url += "&since_id=" + after_this_tweet_id

    print("API URL:", api_url)
    print(f"Fetching {tweets_per_request} tweets from @{twitter_handle}...")
    response = oauth_session.get(api_url)

    num_tweets = len(response.json())
    if num_tweets > 0:
        newest_tweet_id = response.json()[0]['id']
        newest_tweet_time = response.json()[0]['created_at']
        oldest_tweet_id = response.json()[-1]['id']
        oldest_tweet_time = response.json()[-1]['created_at']
        print(f"Retrieved {num_tweets} tweets")
        print(f"newest tweet id {newest_tweet_id} at time {newest_tweet_time}")
        print(f"oldest tweet id {oldest_tweet_id} at time {oldest_tweet_time}")

        tweet_filename = f"{twitter_handle}_tweets/{oldest_tweet_id}_to_{newest_tweet_id}.json"
        print(f"Saving tweets to JSON file: {tweet_filename}")
        with open(tweet_filename, "w") as f:
            f.write(response.text)

        before_this_tweet_id = str(oldest_tweet_id - 1)
    else:
        print("Exiting early, this request returned no tweets")
        break
