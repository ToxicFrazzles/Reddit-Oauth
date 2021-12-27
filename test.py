from reddit_oauth import RedditApp
import json
import requests
from pathlib import Path


def create_example_credentials(credential_file):
    with credential_file.open("w") as f:
        json.dump({
            "client_id": "CLIENT ID GOES HERE!",
            "client_secret": "CLIENT SECRET GOES HERE!",
            "refresh_token": None
        }, f, indent=4)
    exit(1)


def load_credentials():
    credential_file = Path(__file__).parent / "test_credentials.json"
    if not credential_file.is_file():
        create_example_credentials(credential_file)
    f = credential_file.open()
    try:
        credentials = json.load(f)
    except json.JSONDecodeError:
        f.close()
        create_example_credentials(credential_file)
    f.close()
    if credentials["client_id"].startswith("CLIENT"):
        print("Please populate the credentials file with valid credentials")
        exit(1)
    return credentials


def save_credentials(credentials):
    credential_file = Path(__file__).parent / "test_credentials.json"
    with credential_file.open("w") as f:
        json.dump(credentials, f, indent=4)


def get_reddit_username(token):
    headers = {
        "User-agent": "test_bot",
        "Authorization": f"bearer {token}"
    }
    with requests.get("https://oauth.reddit.com/api/v1/me", headers=headers) as r:
        return r.json()["name"]


def main():
    creds = load_credentials()
    app = RedditApp(creds["client_id"], creds["client_secret"], ["identity", "read", "save", "mysubreddits", "history"], refresh_token=creds["refresh_token"])
    access_token = app.auth()
    creds['refresh_token'] = app.refresh_token
    save_credentials(creds)
    print(get_reddit_username(access_token))


if __name__ == "__main__":
    main()
