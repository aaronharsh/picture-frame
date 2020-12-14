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


def is_horizontal(reddit_data):
    images = reddit_data.get("preview", {}).get("images")
    if not images:
        return False

    source = images[0]["source"]
    print(f"images = {images}; source = {source}")
    width = source["width"]
    height = source["height"]

    print(f"checking if image is horizontal.  width = {width}, height = {height}")
    return width >= height


def get_top_image_urls(subreddit, auth, time_period='day', only_horizontal=False):
    response = get_response(f"https://oauth.reddit.com{subreddit}/top/?t={time_period}", auth)

    image_urls = []

    for child in response["data"]["children"]:
        data = child["data"]
        url = data.get("url")
        if url and ".jpg" in url:
            if is_horizontal(data) or not only_horizontal:
                image_urls.append(url)

    return image_urls
