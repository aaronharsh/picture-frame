import os
import re
import subprocess

from datetime import datetime


def get_script_path():
    return os.path.expanduser('~/Dropbox-Uploader/dropbox_uploader.sh')


def get_filenames(directory):
    filenames = []

    script_path = get_script_path()
    script_output_lines = subprocess.check_output([script_path, 'list', directory]).decode().split("\n")
    for line in script_output_lines:
        m = re.match(r'^\s+\[F\]\s+\d+\s+(.*)', line)
        if m:
            filenames.append(f"{directory}/{m.groups()[0]}")

    return filenames


def fetch_image(remote_path, local_path):
    script_path = get_script_path()
    subprocess.call([script_path, 'download', remote_path, local_path])


def get_todays_filenames(directory):
    filenames = []

    today_str = datetime.now().strftime('%Y%m%d')
    for filename in get_filenames(directory):
        basename = os.path.basename(filename)
        if today_str == basename[:len(today_str)]:
            filenames.append(filename)

    return filenames
