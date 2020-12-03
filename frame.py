#!/usr/bin/env python

import pygame, sys
from pygame.locals import *

import images
import reddit

from config import config

BLACK = (0, 0, 0)
RESOLUTION_X = config["resolution_x"]
RESOLUTION_Y = config["resolution_y"]


def show_image(displaysurf, image):
    image_size = image.get_size()

    left = round((RESOLUTION_X - image_size[0]) / 2)
    top = round((RESOLUTION_Y - image_size[1]) / 2)

    displaysurf.fill(BLACK)
    displaysurf.blit(image, (left, top))
    pygame.display.update()


def show_random_image_from_s3_cache(displaysurf):
    images.sync_images_from_s3_to_cache()
    image = images.random_image_from_cache()
    show_image(displaysurf, image)



def show_popular_reddit_image(displaysurf, subreddit):
    auth_file = sys.argv[1]
    auth = reddit.get_auth(auth_file)
    urls = reddit.get_top_image_urls(subreddit, auth)

    if urls:
        url = urls[0]
        print(f"fetching {url}")
        local_file = images.fetch_and_prepare_image(url)
        print(f" copied to {local_file}")
        image = pygame.image.load(local_file)
        show_image(displaysurf, image)


def choose_and_show_image(displaysurf):
    # show_random_image_from_s3_cache(displaysurf)
    show_popular_reddit_image(displaysurf, "/r/astronomy+astrophotography")


def main():
    pygame.init()
    displaysurf = pygame.display.set_mode((RESOLUTION_X, RESOLUTION_Y), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    choose_and_show_image(displaysurf)

    mainLoop = True

    while mainLoop:
        event = pygame.event.wait(config["refresh_pictures_time_seconds"] * 1000)

        print(f"event = {event}")

        if event.type in [pygame.NOEVENT, pygame.MOUSEBUTTONUP, pygame.FINGERUP]:
            choose_and_show_image(displaysurf)

        if event.type in [pygame.QUIT, pygame.KEYUP]:
            mainLoop = False

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
