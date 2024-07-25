import json
import requests
import os


# Discordに送信
def discord_write(message):
    url = "https://discord.com/api/webhooks/1094787057072734329/SWHyvUiWsMf6uDEH2TlVg-wT6nPdGoWJi9ljFsmABs6TgyzUOyzmiwsCeuRBFUvghCPX"
    content = {"content": message}
    headers = {"Content-Type": "application/json"}
    requests.post(url, json.dumps(content), headers=headers)


def is_windows():
    return os.name == "nt"


def get_core():
    if is_windows():
        core = "0"
    else:
        core = f"{os.sched_getaffinity(0)}"
    return core


# google colab起動か否か
def is_colab():
    # cpu起動でもCOLAB_GPUのキーはある
    return "COLAB_GPU" in os.environ
