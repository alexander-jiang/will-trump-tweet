import json
import os

class Secrets():
    def __init__(self):
        secrets_path = os.path.join(os.path.dirname(__file__), "../secrets/twitter_api_secrets.json")
        print(secrets_path)
        with open(secrets_path, "r") as f:
            secrets = json.load(f)
            self.CONSUMER_API_KEY = secrets["CONSUMER_API_KEY"]
            self.CONSUMER_API_SECRET_KEY = secrets["CONSUMER_API_SECRET_KEY"]
            self.ACCESS_TOKEN = secrets["ACCESS_TOKEN"]
            self.ACCESS_TOKEN_SECRET = secrets["ACCESS_TOKEN_SECRET"]

    def get_consumer_api_key(self):
        return self.CONSUMER_API_KEY

    def get_consumer_api_secret_key(self):
        return self.CONSUMER_API_SECRET_KEY

    def get_access_token(self):
        return self.ACCESS_TOKEN

    def get_access_token_secret(self):
        return self.ACCESS_TOKEN_SECRET
