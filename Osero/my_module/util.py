import argparse
import requests
import json
import os

parser = argparse.ArgumentParser(description="Example script with arguments")
# 引数を追加
parser.add_argument("-f", "--forceproto", action="store_true", help="Force prototype")
parser.add_argument(
    "-d", "--detail_discord_ntfy", action="store_true", help="Detail discord ntfy"
)
parser.add_argument("-df", "--display_fig", action="store_true", help="Display fig")
parser.add_argument("-sf", "--save_fig", action="store_true", help="Save fig")

parser.add_argument(
    "-n",
    "--not_upload_to_gdrive",
    action="store_true",
    help="Not upload result to gdrive",
)
# 引数を解析
args = parser.parse_args()

print(f"--forceproto:{args.forceproto}")
print(f"--detail_discord_ntfy:{args.detail_discord_ntfy}")
print(f"--display_fig:{args.display_fig}")
print(f"--save_fig:{args.save_fig}")

################################ 定数

IS_PROTO = os.getenv("PROTOTYPING_DEVELOP") == "True" or args.forceproto


# google colab起動か否か
def is_colab():
    # cpu起動でもCOLAB_GPUのキーはある
    return "COLAB_GPU" in os.environ


################################ 関数


def get_checkpoint_file_name(epoch):
    return f"epoch_{epoch:02d}_checkpoint.keras"


# 保存されたチェックポイントファイルから最大のエポック番号を取得
def get_latest_checkpoint_epoch(train_history):
    length = len(train_history)
    if length == 0:
        return -1
    else:
        return train_history[length - 1].get("epoch")


# Discordに送信
def discord_write(message):
    url = "https://discord.com/api/webhooks/1094787057072734329/SWHyvUiWsMf6uDEH2TlVg-wT6nPdGoWJi9ljFsmABs6TgyzUOyzmiwsCeuRBFUvghCPX"
    content = {"content": message}
    headers = {"Content-Type": "application/json"}
    requests.post(url, json.dumps(content), headers=headers)
