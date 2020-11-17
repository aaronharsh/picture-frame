import io
import json
import os
import pygame
import random
import requests
import sys
import tempfile

from config import config

cache_directory = config["cache_directory"]


def get_remote_manifest(base_url):
    response = requests.get(base_url + "/manifest.txt")
    if response.status_code == 200:
        return response.text
    else:
        return None


def get_remote_image_urls():
    base_url = config["image_base_url"]

    manifest = get_remote_manifest(base_url)
    if manifest == None:
        return None

    image_urls = []

    for image_basename in manifest.split("\n"):
        if image_basename == "":
            continue

        image_urls.append(base_url + "/" + image_basename)

    return image_urls


def fetch_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        # Preserve the suffix on the file, to avoid confusing pygame
        _, suffix = os.path.splitext(image_url)
        _, local_path = tempfile.mkstemp(suffix=suffix)
        with open(local_path, "wb") as f:
            f.write(response.content)
        return local_path
    else:
       print(f"failed to download {image_url}: {response.status_code}")


def resize_image(original_path, resized_path):
    original_image = pygame.image.load(original_path)
    original_size = original_image.get_size()
    screen_size = (config["resolution_x"], config["resolution_y"])

    x_ratio = screen_size[0] / original_size[0]
    y_ratio = screen_size[1] / original_size[1]

    ratio = min([x_ratio, y_ratio])

    new_size = (round(original_size[0] * ratio), round(original_size[1] * ratio))
    resized = pygame.transform.smoothscale(original_image, new_size)

    pygame.image.save(resized, resized_path)


def fetch_and_resize_image(image_url):
    image_basename = os.path.basename(image_url)

    local_path = cache_directory + "/" + image_basename

    if os.path.exists(local_path):
        print(f"{local_path} already exists - not downloading {image_url}")
    else:
        unresized_path = fetch_image(image_url)
        resize_image(unresized_path, local_path)
        os.unlink(unresized_path)


def sync_images():
    try:
        if not os.path.exists(cache_directory):
            try:
                os.mkdir(cache_directory)
            except Exception as e:
                print(f"couldn't create {cache_directory}: e")
                return

        remote_image_urls = get_remote_image_urls()
        if not remote_image_urls:
            print(f"no remote image urls.  not syncing")
            return

        for image_url in remote_image_urls:
            fetch_and_resize_image(image_url)

        remote_image_basenames = [os.path.basename(u) for u in remote_image_urls]

        for local_basename in os.listdir(cache_directory):
            if not local_basename in remote_image_basenames:
                print(f"removing file {local_basename}")
                os.remove(cache_directory + '/' + local_basename)
    except Exception as e:
        print(f"error syncing images: {e}")


def random_image():
    files = os.listdir(cache_directory)
    if not files:
        return None

    file = random.choice(files)
    return pygame.image.load(cache_directory + "/" + file)
