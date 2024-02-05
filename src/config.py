import os
import sys
import json

CONFIG = json.load(
    open(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), "config.json"))
)


def get_verbose():
    # Read `config.json` file and get the value of `verbose` key
    return CONFIG["verbose"]


def get_telegram_api_id():
    # Read `config.json` file and get the value of `telegram_api_id` key
    return CONFIG["telegram_api_id"]


def get_telegram_api_hash():
    # Read `config.json` file and get the value of `telegram_api_hash` key
    return CONFIG["telegram_api_hash"]
