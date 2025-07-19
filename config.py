import json


def load_config(path="./config.json"):
    with open(path) as f:
        return json.load(f)


def get_telegram_token(config):
    telegram = config["telegram"]
    # Token format: "bot_id:bot_secret:chat_id"
    # We need "bot_id:bot_secret" (everything except the last part)
    parts = telegram.split(":")
    return ":".join(parts[:-1])


def get_chat_id(config):
    telegram = config["telegram"]
    # Chat ID is the last part after the final colon
    return telegram.split(":")[-1]
