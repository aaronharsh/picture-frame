#!/usr/bin/env python

import argparse
import logging
from datetime import datetime, timedelta
import random
import sys

import pygame
from pygame.locals import *

import dropbox
import images
import reddit

from config import config

BLACK = (0, 0, 0)
RESOLUTION_X = config["resolution_x"]
RESOLUTION_Y = config["resolution_y"]

OFFSET_X = config["offset_x"]
OFFSET_Y = config["offset_y"]

DROPBOX_DIRECTORY = config.get("dropbox_directory")


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def show_image(displaysurf, image):
    image_size = image.get_size()

    left = round((RESOLUTION_X - image_size[0]) / 2) + OFFSET_X
    top = round((RESOLUTION_Y - image_size[1]) / 2) + OFFSET_Y

    displaysurf.fill(BLACK)
    displaysurf.blit(image, (left, top))
    pygame.display.update()


def show_random_image_from_s3_cache(displaysurf):
    images.sync_images_from_s3_to_cache()
    image = images.random_image_from_cache()
    show_image(displaysurf, image)


def show_local_image(displaysurf, local_file):
    image = pygame.image.load(local_file)
    show_image(displaysurf, image)


def show_popular_reddit_image(displaysurf, subreddit, auth_file, only_horizontal=False):
    auth = reddit.get_auth(auth_file)
    urls = reddit.get_top_image_urls(subreddit, auth, time_period='day', only_horizontal=only_horizontal)

    if urls:
        url = urls[0]
        logging.info(f"fetching {url}")
        local_file = images.fetch_and_prepare_image(url)
        logging.info(f" copied to {local_file}")
        show_local_image(displaysurf, local_file)


def subreddit_for_day_of_week():
    now = datetime.now()
    if now.weekday() == 0:
        return "/r/AbandonedPorn"
    elif now.weekday() == 1:
        return "/r/Portland+cedarrapids+OregonCoast+Iowa"
    elif now.weekday() == 2:
        return "/r/AccidentalWesAnderson"
    elif now.weekday() == 3:
        return "/r/CampingandHiking+WildCampingAndHiking+camping+socalhiking"
    elif now.weekday() == 4:
        return "/r/EverythingFoxes+fennecfoxes+foxes"
    elif now.weekday() == 5:
        return "/r/NatureIsFuckingLit"
    elif now.weekday() == 6:
        return "/r/Eyebleach"


def show_dropbox_image(displaysurf, dropbox_filename):
    local_image = images.fetch_and_prepare_dropbox_image(dropbox_filename, rotate=False)
    show_local_image(displaysurf, local_image)


def get_random_dropbox_filename():
    if DROPBOX_DIRECTORY:
        dropbox_filenames = dropbox.get_todays_filenames(DROPBOX_DIRECTORY)
        if dropbox_filenames:
            return random.choice(dropbox_filenames)
    return None


def choose_and_show_image(displaysurf, auth_file):
    # show_random_image_from_s3_cache(displaysurf)

    dropbox_filename = get_random_dropbox_filename()
    if dropbox_filename:
        show_dropbox_image(displaysurf, dropbox_filename)
    else:
        show_popular_reddit_image(displaysurf, subreddit_for_day_of_week(), auth_file, only_horizontal=True)


def main():
    parser = argparse.ArgumentParser(description="Show rotating list of pictures")
    parser.add_argument("--auth-file", type=str, required=True)
    args = parser.parse_args()
    auth_file = args.auth_file

    start = datetime.now()
    end_after = datetime(start.year, start.month, start.day) + timedelta(days=1, hours=3)

    exit_code = 0

    pygame.init()
    displaysurf = pygame.display.set_mode((RESOLUTION_X, RESOLUTION_Y), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    choose_and_show_image(displaysurf, auth_file)

    last_click_times = []

    while True:
        event = pygame.event.wait(config["refresh_pictures_time_seconds"] * 1000)

        logging.info(f"event = {event}")

        if event.type in [pygame.NOEVENT, pygame.QUIT, pygame.KEYUP]:
            choose_and_show_image(displaysurf, auth_file)

        if event.type in [pygame.MOUSEBUTTONUP, pygame.FINGERUP]:
            last_click_times.append(datetime.now())
            last_click_times = last_click_times[-5:]
            if len(last_click_times) >= 5 and last_click_times[0] + timedelta(seconds=10) >= last_click_times[-1]:
                exit_code = 2
                break

        if datetime.now() > end_after:
            break

        pygame.display.update()

    pygame.quit()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
