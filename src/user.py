import json
import os

USER_MAPPINGS_FILE = "data/user_mappings.json"


def load_user_mappings():
    if os.path.exists(USER_MAPPINGS_FILE):
        with open(USER_MAPPINGS_FILE, "r") as file:
            return json.load(file)
    return {}


def save_user_mappings(mappings):
    with open(USER_MAPPINGS_FILE, "w") as file:
        json.dump(mappings, file)
