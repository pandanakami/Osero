import os

import keras as K
import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import numpy as np
from sklearn.model_selection import train_test_split
import re
import datetime

from my_module.osero_model import INPUT_CHANNEL, OUTPUT_SIZE, MODEL_NAME
from my_module.osero_model import is_channel_first, get_model
import my_module.load_data as load_data
from my_module import plot
from my_module.gdrive_uploader import GoogleDriveFacade
import json
import requests
import argparse

print(tf.__version__)
print(K.__version__)

BATCH_SIZE = 100
EPOCH = 1000


parser = argparse.ArgumentParser(description="Example script with arguments")
# 引数を追加
parser.add_argument("-f", "--forceproto", action="store_true", help="Force prototype")
parser.add_argument(
    "-d", "--detail_discord_ntfy", action="store_true", help="Detail discord ntfy"
)

# 引数を解析
args = parser.parse_args()

print(f"--forceproto:{args.forceproto}")
print(f"--detail_discord_ntfy:{args.detail_discord_ntfy}")


IS_PROTO = os.getenv("PROTOTYPING_DEVELOP") == "True"

if args.forceproto:
    IS_PROTO = True

if IS_PROTO:
    print("[PROTOTYPING MODE]")


def is_colab():
    return "COLAB_GPU" in os.environ


SAVE_NAME = f"{MODEL_NAME}{'_proto' if IS_PROTO else '_'}"

if is_colab():
    # Google Driveの保存ディレクトリを指定
    BASE_DIR = "/content/drive/MyDrive/osero/"

    if IS_PROTO:
        TRAIN_INPUT_DIR = os.path.join(BASE_DIR, "input_proto")
    else:
        TRAIN_INPUT_DIR = os.path.join(BASE_DIR, "input")

    CHECK_POINT_DIR = os.path.join(BASE_DIR, f"checkpoints_{SAVE_NAME}")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")

else:
    BASE_DIR = "./"
    if IS_PROTO:
        TRAIN_INPUT_DIR = "../CreateTrainData/output/proto"
    else:
        TRAIN_INPUT_DIR = "../CreateTrainData/output"

    CHECK_POINT_DIR = f"./checkpoints_{SAVE_NAME}"
    OUTPUT_DIR = "./output"

os.makedirs(CHECK_POINT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


OUTPUT_FILE_NAME = os.path.join(OUTPUT_DIR, f"{SAVE_NAME}.keras")
OUTPUT_FIG_FILE_NAME = os.path.join(OUTPUT_DIR, f"{SAVE_NAME}_fig.png")
OUTPUT_LATEST_FIG_POS = os.path.join(BASE_DIR, "latest_fig_pos.txt")
CHECK_POINT_HISTORY_NAME = os.path.join(CHECK_POINT_DIR, "history.json")


def get_checkpoint_file_name(epoch):
    return f"epoch_{epoch:02d}_checkpoint.keras"


# 保存されたチェックポイントファイルから最大のエポック番号を取得
def get_latest_checkpoint_epoch(train_history):
    length = len(train_history)
    if length == 0:
        return -1
    else:
        return train_history[length - 1].get("epoch")


train_history = []


def discord_write(message):
    url = "https://discord.com/api/webhooks/1094787057072734329/SWHyvUiWsMf6uDEH2TlVg-wT6nPdGoWJi9ljFsmABs6TgyzUOyzmiwsCeuRBFUvghCPX"
    content = {"content": message}
    headers = {"Content-Type": "application/json"}
    requests.post(url, json.dumps(content), headers=headers)


# カスタムコールバックの定義
class HistorySaver(keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        save_epoch = epoch + 1
        print(f"Epoch {save_epoch} finished. Saving parameters.")

        if args.detail_discord_ntfy:
            discord_write(f"update epoch:{save_epoch} ({MODEL_NAME})")

        result = next(
            (item for item in train_history if item["epoch"] == save_epoch), None
        )
        if result:
            print(f"override history epoch:{save_epoch}")
            result["loss"] = logs.get("loss")
            result["accuracy"] = logs.get("accuracy")
            result["val_loss"] = logs.get("val_loss")
            result["val_accuracy"] = logs.get("val_accuracy")
        else:
            train_history.append(
                {
                    "epoch": save_epoch,
                    "loss": logs.get("loss"),
                    "accuracy": logs.get("accuracy"),
                    "val_loss": logs.get("val_loss"),
                    "val_accuracy": logs.get("val_accuracy"),
                }
            )
            test = json.dumps(train_history, indent=4)
            with open(CHECK_POINT_HISTORY_NAME, "w") as file:
                file.write(test)


if __name__ == "__main__":

    if not is_colab():
        gdrive_mng = GoogleDriveFacade()

    ## 乱数
    np.random.seed(123)
    tf.random.set_seed(123)

    ## データ取得
    print("[start load_data]")
    (x_train, t_train), (x_val, t_val), (x_eval, t_eval) = load_data.load_data(
        TRAIN_INPUT_DIR
    )
    print("[end load_data]")

    ## 途中履歴取得
    if os.path.exists(CHECK_POINT_HISTORY_NAME):
        with open(CHECK_POINT_HISTORY_NAME, "r") as file:
            train_history = json.load(file)

    ## モデルの定義
    print("[start construct Model]")
    # 最大のエポック番号を取得
    latest_epoch = get_latest_checkpoint_epoch(train_history)
    if latest_epoch != -1:
        # ロード
        model = keras.models.load_model(
            os.path.join(CHECK_POINT_DIR, get_checkpoint_file_name(latest_epoch))
        )
        initial_epoch = latest_epoch
        print(
            f"Loaded model from epoch {latest_epoch}. Resuming training from epoch {initial_epoch}."
        )
    else:
        # 最初から
        model = get_model(True)
        initial_epoch = 0
        print("No checkpoint found. Starting training from scratch.")
    print(f"[end construct Model] model:{MODEL_NAME}")

    ## 学習プロセスを設定する
    print("[start compile]")
    model.compile(
        loss=K.losses.SparseCategoricalCrossentropy(),
        optimizer=tf.keras.optimizers.Adam(),
        # 評価関数を指定
        metrics=[keras.metrics.Accuracy().name],
    )
    print("[end compile]")

    ## 学習
    print("[start training]")
    start = datetime.datetime.now()

    # ModelCheckpointコールバックの設定
    checkpoint_callback = keras.callbacks.ModelCheckpoint(
        filepath=os.path.join(CHECK_POINT_DIR, "epoch_{epoch:02d}_checkpoint.keras"),
        save_weights_only=False,
        save_freq="epoch",  # エポックごとに保存
    )

    model.fit(
        x_train,
        t_train,
        batch_size=BATCH_SIZE,
        epochs=EPOCH,
        validation_data=(x_val, t_val),
        verbose=2,
        initial_epoch=initial_epoch,
        callbacks=[
            keras.callbacks.EarlyStopping(monitor="val_loss", patience=5),
            checkpoint_callback,
            HistorySaver(),
        ],
    )
    print("[end training]")

    ## 評価
    print("[start evaluate]")
    score = model.evaluate(x_eval, t_eval, verbose=0)
    print(f"[end evaluate] loss:{score[0]:3f}, acc:{score[1]:3f}")

    ##保存
    model.save(OUTPUT_FILE_NAME)

    end = datetime.datetime.now()
    print(f"start:{start}")
    print(f"end:{end} model_name:{MODEL_NAME}")

    ##web hook
    discord_write(f"{MODEL_NAME}: train finish. loss:{score[0]:3f}, acc:{score[1]:3f}")

    plot.plot(train_history, OUTPUT_FIG_FILE_NAME)

    if not is_colab():
        # モデルアップロード
        gdrive_mng.upload(
            local_file_path=OUTPUT_FILE_NAME,
            save_folder_id="1r3nNbTkJk77eMMSVq-zXRz_gBaVbtd1x",
            is_convert=True,
        )
        # 図アップロード
        gdrive_mng.upload(
            local_file_path=OUTPUT_FIG_FILE_NAME,
            save_folder_id="1r3nNbTkJk77eMMSVq-zXRz_gBaVbtd1x",
            is_convert=True,
        )

    if is_colab():
        with open(OUTPUT_LATEST_FIG_POS, "w") as f:
            f.write(OUTPUT_FIG_FILE_NAME)
