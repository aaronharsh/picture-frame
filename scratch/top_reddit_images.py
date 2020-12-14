import json
import re
import requests
import requests.auth
import time


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

    with open("/tmp/reddit.json", "w") as f:
        json.dump(response.json(), f)
    return response.json()


after = None

def get_top_image_postings(auth, limit, time_period='week'):
    url = f"https://oauth.reddit.com/top/?t={time_period}&limit={limit}"
    url = f"https://oauth.reddit.com/top/?t={time_period}"

    global after
    if after:
        url += f"&after={after}"
    response = get_response(url, auth)
    
    results = []

    after = response["data"]["after"]

    for child in response["data"]["children"]:
        data = child["data"]
        permalink = data["permalink"]
        url = data.get("url")

        parts = permalink.split('/')
        subreddit = parts[2]
        post_id = parts[4]

        if url and ".jpg" in url:
            results.append({
                "permalink": permalink,
                "url": url,
                "subreddit": subreddit,
                "post_id": post_id,
            })

    return results


auth = get_auth("reddit_auth.json")

print("<table>\n")

for count in range(300):
    for result in get_top_image_postings(auth, 100):
        print(f'<tr><td>{result["subreddit"]}</td><td>{result["permalink"]}</td><td><img src="{result["url"]}" width="300"/></td></tr>')

print("</table>\n")
