from secrets import token_urlsafe
from base64 import b64encode
from .http_resolver import RequestHandler, AuthServer
import requests


BASE_URL = "https://www.reddit.com"
AUTHORISE_URL = BASE_URL + "/api/v1/authorize"
ACCESS_TOKEN_URL = BASE_URL + "/api/v1/access_token"


class RedditApp:
    def __init__(self, client_id, client_secret, scopes, port=8765, refresh_token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.port = port
        self.scopes = scopes
        self.refresh_token = refresh_token

    def authorisation_url(self, state):
        return (f"{AUTHORISE_URL}"
                f"?client_id={self.client_id}"
                f"&response_type=code"
                f"&state={state}"
                f"&redirect_uri=http%3A%2F%2Flocalhost%3A{self.port}"
                f"&duration=permanent"
                f"&scope={'%20'.join(self.scopes)}")

    def start_auth_server(self, state):
        with AuthServer(("127.0.0.1", self.port), RequestHandler) as server:
            return server.auth(state)

    def retrieve_tokens(self, code):
        headers = {
            "User-agent": f"bot {self.client_id}",
            "Authorization": b"Basic " + b64encode(f"{self.client_id}:{self.client_secret}".encode('utf-8'))
        }
        with requests.post(ACCESS_TOKEN_URL, {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": f"http://localhost:{self.port}"
        }, headers=headers) as r:
            json = r.json()
            if "error" in json:
                print(json)
                exit(1)
            access_token = json["access_token"]
            self.refresh_token = json["refresh_token"]
            return access_token

    def auth(self):
        if self.refresh_token is not None:
            return self.get_new_access_token()
        state = token_urlsafe(16)
        print(self.authorisation_url(state))
        code = self.start_auth_server(state)
        return self.retrieve_tokens(code)

    def get_new_access_token(self):
        headers = {
            "User-agent": f"bot {self.client_id}",
            "Authorization": b"Basic " + b64encode(f"{self.client_id}:{self.client_secret}".encode('utf-8'))
        }
        with requests.post(ACCESS_TOKEN_URL, {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }, headers=headers) as r:
            json = r.json()
            if "error" in json:
                print(json)
                exit(1)
            access_token = json["access_token"]
            return access_token
