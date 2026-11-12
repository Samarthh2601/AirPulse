import os
import json
import time

CACHE_DIR = "cache"

os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache(key, expiry=600):

    file_path = os.path.join(CACHE_DIR, f"{key}.json")

    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, "r") as file:
            cached_data = json.load(file)

        timestamp = cached_data["timestamp"]
        data = cached_data["data"]

        # Check whether cache has expired
        if time.time() - timestamp > expiry:
            return None

        return data

    except (json.JSONDecodeError, KeyError, OSError):
        return None


def set_cache(key, data):
    file_path = os.path.join(CACHE_DIR, f"{key}.json")

    cached_data = {
        "timestamp": time.time(),
        "data": data
    }

    with open(file_path, "w") as file:
        json.dump(cached_data, file)