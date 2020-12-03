import json
import requests
import requests.auth


USER_AGENT = "pictureframebot/0.1 by aaronharsh"
ENDPOINT_ME = "https://oauth.reddit.com/api/v1/me"


def get_auth(auth_file):
    with open(auth_file) as f:
        auth_data = json.load(f)

    client_auth = requests.auth.HTTPBasicAuth(auth_data["client_id"], auth_data["secret"])
    post_data = {"grant_type": "password", "username": auth_data["username"], "password": auth_data["password"]}
    headers = {"User-Agent": USER_AGENT}
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
    return response.json()


def get_response(endpoint, auth):
    access_token = auth["access_token"]

    headers = {"Authorization": f"bearer {access_token}", "User-Agent": USER_AGENT}
    response = requests.get(endpoint, headers=headers)
    return response.json()


def get_top_image_urls(subreddit, auth):
    response = get_response(f"https://oauth.reddit.com{subreddit}/top/?t=day", auth)
    
    image_urls = []

    for child in response["data"]["children"]:
        url = child["data"].get("url")
        if url and ".jpg" in url:
            image_urls.append(url))

    return image_urls
