import json
import os
import requests
import time
from .secrets import Secrets

class TwitterPremiumSearchFetcher():
    def __init__(self):
        self.secrets = Secrets()

    def get_user_tweets(self,
        user_id, from_date, to_date, output_directory="", use_full_archive=False,
        results_per_request=100, max_requests=5, sleep_btwn_requests=2.0):
        """
        Call the Premium Search API endpoint to get the historical tweets for
        a specified user in a specified date/time range. Note that this endpoint
        has various usage limits.
        https://developer.twitter.com/en/docs/tweets/search/api-reference/premium-search#DataEndpoint

        user_id: (string)
            the Twitter user ID of the user whose tweets you wish to retrieve
            (note that this is the user ID and not the screen name as the user
            ID is often shorter in characters than the screen name, and the
            premium search query parameter has a character limit)
        from_date, to_date: (string)
            the start and end dates in which to retrieve tweets. Note that the
            dates are specified in the format YYYYMMDDhhmm
        output_directory: (string)
            a path to a directory to store the output JSON files
        use_full_archive: (boolean)
            If True, uses the Full-Archive endpoint. Otherwise, uses the 30-day
            endpoint
        results_per_request: (integer)
            The maximum number of Tweets to return per request. This must be
            between 10 and 100 (or 10 and 500 if you have a Premium API
            subscription).
        max_requests: (integer)
            The maximum number of requests to make for this endpoint. This
            function will automatically make no more requests if there are no
            more results left to return.
        sleep_btwn_requests: (float)
            The amount of time (in seconds) to sleep between each request. This
            can be used to ensure that the per-second or per-minute rate limits
            are not exceeded.
        """
        ## Don't need to change the variables below
        premium_api_type = "fullarchive" if use_full_archive else "30day"
        environment_name = "dev"
        url = f"https://api.twitter.com/1.1/tweets/search/{premium_api_type}/{environment_name}.json"
        data_json = {
            "query": f"from:{user_id}",
            "maxResults": f"{results_per_request}",
            "fromDate": f"{from_date}",
            "toDate": f"{to_date}"
        }
        data = json.dumps(data_json)
        BEARER_TOKEN = self.secrets.get_bearer_token()
        headers = {
            'content-type': 'application/json',
            'authorization': f"BEARER {BEARER_TOKEN}"
        }

        newest_tweet_id_so_far = -float('inf')
        oldest_tweet_id_so_far = float('inf')
        all_tweets = []

        has_next = False
        request_num = 1
        while request_num <= max_requests:
            if request_num > 1:
                time.sleep(sleep_btwn_requests)
            print(f"=== REQUEST {request_num} ===")
            print(url)
            print(data)
            response = requests.post(url, data=data, headers=headers)
            response_json = response.json()
            batch_tweets = response_json['results']
            num_tweets = len(batch_tweets)

            with open(f"{output_directory}/{from_date}_to_{to_date}_page{request_num}.json", "w", encoding="utf8") as f:
                json.dump(batch_tweets, f)

            # TODO refactor: this code is duplicated with the code in TwitterFetcher
            newest_tweet_id = batch_tweets[0]['id']
            newest_tweet_time = batch_tweets[0]['created_at']
            oldest_tweet_id = batch_tweets[-1]['id']
            oldest_tweet_time = batch_tweets[-1]['created_at']

            newest_tweet_id_so_far = max(newest_tweet_id_so_far, newest_tweet_id)
            oldest_tweet_id_so_far = min(oldest_tweet_id_so_far, oldest_tweet_id)
            print(f"Retrieved {num_tweets} tweets in this batch")
            print(f"newest tweet id {newest_tweet_id} at time {newest_tweet_time}")
            print(f"oldest tweet id {oldest_tweet_id} at time {oldest_tweet_time}")

            all_tweets.extend(batch_tweets)

            has_next = "next" in response_json
            if has_next:
                next_token = response_json['next']
                print(f"found a 'next' token: {next_token}")
                data_json['next'] = next_token
                data = json.dumps(data_json)
            else:
                print(f"no more 'next' token: exiting early")
                break

            request_num += 1

        print(f"Retrieved a total of {len(all_tweets)} tweets")
        with open(f"{output_directory}/merged_{from_date}_to_{to_date}.json", "w", encoding="utf8") as f:
            json.dump(all_tweets, f)


"""
# See docs:
# query operators: https://developer.twitter.com/en/docs/tweets/search/guides/premium-operators
# other request params (e.g. fromDate/toDate, maxResults): https://developer.twitter.com/en/docs/tweets/search/guides/integrating-premium


# replace the "fullarchive" in the URL with "30day" to use the 30-day search endpoint
curl --request POST \
  --url https://api.twitter.com/1.1/tweets/search/fullarchive/prod.json \
  --header 'authorization: Bearer {BEARER_TOKEN}' \
  --header 'content-type: application/json' \
  --data '{
                "query":"from:25073877",
                "maxResults": "100",
                "fromDate":"201802010000",
                "toDate":"201802282359"
                }'


# Request rate limits at both minute and second granularity. Requests are aggregated across both
# the data and counts endpoints. (but the Sandbox only has the data endpoint, not counts)
# Limits for full-archive API:
# - 10 requests per second (both Sandbox and Premium).
# - 30 requests per minute with Sandbox environment (60/min for Premium).
# - 50 requests per month with Sandbox. Premium can be from 100/mo ($99/mo) to 2500/mo ($1900/mo)
# - 100 tweets per request with Sandbox, 500/request with Premium
# - 5000 tweets per UTC month with Sandbox, from 50k/mo to 1.25M/mo with Premium

Here is the general structure of Tweet JSON payloads returned by Tweet Search:
{
  "results": [
       {Tweet},
       {Tweet},
       {Tweet}
  ],
  "next": "TOKEN",
  "requestParameters": {
      "maxResults": 10,
      "fromDate": "201709020000",
      "toDate": "201710021814"
  }
}
"""

def main():
    # Note: 25073877 is the user ID for @realDonaldTrump
    # (Used http://gettwitterid.com/?user_name=realDonaldTrump&submit=GET+USER+ID to lookup)
    # The query request parameter below is limited to 128 chars for Full-Archive API
    # in Sandbox (256 chars for 30-day Archive API in Sandbox)
    user_id = "25073877"

    # dates below are in the format YYYYMMDDhhmm
    from_date = "201701200000" # assume Jan 20, 2017 midnight UTC is the start of Trump's presidency
    to_date = "202001100205"

    output_dir = "premium_RDT_tweets"

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

if __name__ == "__main__":
    main()
