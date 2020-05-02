from datetime import datetime
import pytz

class TweetFeatures:
    """
    A selection of features from the Twitter Tweet object
    see https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object
    """

    def __init__(self, tweet_json):
        eastern_tz = pytz.timezone('US/Eastern')
        created_datetime = datetime.strptime(tweet_json['created_at'], "%a %b %d %H:%M:%S %z %Y")
        eastern_time = created_datetime.astimezone(eastern_tz)

        self.id = tweet_json['id']
        self.created_at = tweet_json['created_at']
        self.eastern_created_at = eastern_time.strftime("%a %b %d %H:%M:%S %z %Y")
        self.day_of_week = eastern_time.strftime("%A")
        self.source = tweet_json['source']
        self.is_retweet = 'retweeted_status' in tweet_json
        self.text_len = len(tweet_json['text'])

    # List of field names (used for CSV header)
    @classmethod
    def get_field_names(cls):
        return ['id', 'created_at', 'eastern_time', 'day_of_week', 'source', 'is_retweet', 'text_len']

    # This function can be used as input for csv.DictWriter.writerow()
    def as_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'eastern_time': self.eastern_created_at,
            'day_of_week': self.day_of_week,
            'source': self.source,
            'is_retweet': self.is_retweet,
            'text_len': self.text_len
        }
