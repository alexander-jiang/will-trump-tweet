from datetime import datetime

class TweetFeatures:
    """
    A selection of features from the Twitter Tweet object
    see https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object
    """

    def __init__(self, tweet_json):
        self.id = tweet_json['id']
        self.created_at = tweet_json['created_at']
        self.created_datetime = datetime.strptime(tweet_json['created_at'], "%a %b %d %H:%M:%S %z %Y")
        self.source = tweet_json['source']
        self.is_retweet = 'retweeted_status' in tweet_json
        self.text_len = len(tweet_json['text'])
        self.text = tweet_json['text']
        self.favorite = tweet_json['favorite_count']
        self.retweets = tweet_json['retweet_count']

    # List of field names (used for CSV header)
    @classmethod
    def get_field_names(cls):
        return ['id', 'created_at', 'source', 'is_retweet', 'text_len', 'text', 'favorite', 'retweets']

    # This function can be used as input for csv.DictWriter.writerow()
    def as_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'source': self.source,
            'is_retweet': self.is_retweet,
            'text_len': self.text_len,
            'text' : self.text,
            'favorite' : self.favorite,
            'retweets' : self.retweets
        }
