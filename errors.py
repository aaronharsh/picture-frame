import requests
import urllib.parse
import sys


def report_error(message):
    try:
        reporting_url = 'http://avoidthis.website/frame-error?message=' + urllib.parse.quote_plus(message)
        requests.get(reporting_url)
    except Exception:
        pass
