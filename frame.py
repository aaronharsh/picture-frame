#!/usr/bin/env python

import pygame, sys
from pygame.locals import *

import images

from config import config

BLACK = (0, 0, 0)
RESOLUTION_X = config["resolution_x"]
RESOLUTION_Y = config["resolution_y"]


def show_random_image():
    image = images.random_image()

    image_size = image.get_size()

    left = round((RESOLUTION_X - image_size[0]) / 2)
    top = round((RESOLUTION_Y - image_size[1]) / 2)

    if image:
        DISPLAYSURF.fill(BLACK)
        DISPLAYSURF.blit(image, (left, top))
        pygame.display.update()

images.sync_images()

pygame.init()
DISPLAYSURF = pygame.display.set_mode((RESOLUTION_X, RESOLUTION_Y), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)

show_random_image()

mainLoop = True

while mainLoop:
    event = pygame.event.wait(config["refresh_pictures_time_seconds"] * 1000)

    print(f"event = {event}")

    if event.type in [pygame.NOEVENT, pygame.MOUSEBUTTONUP, pygame.FINGERUP]:
        images.sync_images()
        show_random_image()

    if event.type in [pygame.QUIT, pygame.KEYUP]:
        mainLoop = False

    pygame.display.update()

pygame.quit()
