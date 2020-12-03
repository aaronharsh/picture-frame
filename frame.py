#!/usr/bin/env python

import pygame, sys
from pygame.locals import *

import images

from config import config

BLACK = (0, 0, 0)
RESOLUTION_X = config["resolution_x"]
RESOLUTION_Y = config["resolution_y"]


def show_random_image_from_s3_cache(displaysurf):
    image = images.random_image_from_cache()

    image_size = image.get_size()

    left = round((RESOLUTION_X - image_size[0]) / 2)
    top = round((RESOLUTION_Y - image_size[1]) / 2)

    if image:
        displaysurf.fill(BLACK)
        displaysurf.blit(image, (left, top))
        pygame.display.update()


def main():
    images.sync_images_from_s3_to_cache()

    pygame.init()
    displaysurf = pygame.display.set_mode((RESOLUTION_X, RESOLUTION_Y), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    show_random_image_from_s3_cache(displaysurf)

    mainLoop = True

    while mainLoop:
        event = pygame.event.wait(config["refresh_pictures_time_seconds"] * 1000)

        print(f"event = {event}")

        if event.type in [pygame.NOEVENT, pygame.MOUSEBUTTONUP, pygame.FINGERUP]:
            images.sync_images_from_s3_to_cache()
            show_random_image_from_s3_cache(displaysurf)

        if event.type in [pygame.QUIT, pygame.KEYUP]:
            mainLoop = False

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
