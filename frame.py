#!/usr/bin/env python

import argparse
import logging
from datetime import datetime, timedelta
import sys

import pygame
from pygame.locals import *

import images
import reddit

from config import config

BLACK = (0, 0, 0)
RESOLUTION_X = config["resolution_x"]
RESOLUTION_Y = config["resolution_y"]

OFFSET_X = config["offset_x"]
OFFSET_Y = config["offset_y"]

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



def show_popular_reddit_image(displaysurf, subreddit, auth_file):
    auth = reddit.get_auth(auth_file)
    urls = reddit.get_top_image_urls(subreddit, auth, time_period='day')

    if urls:
        url = urls[0]
        logging.info(f"fetching {url}")
        local_file = images.fetch_and_prepare_image(url)
        logging.info(f" copied to {local_file}")
        image = pygame.image.load(local_file)
        show_image(displaysurf, image)


def choose_and_show_image(displaysurf, auth_file):
    # show_random_image_from_s3_cache(displaysurf)
    show_popular_reddit_image(displaysurf, "/r/astronomy+astrophotography", auth_file)


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
