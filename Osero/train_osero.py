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


print(tf.__version__)
print(K.__version__)

BATCH_SIZE = 100
EPOCH = 1000

IS_PROTO = os.getenv("PROTOTYPING_DEVELOP") == "True"
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


def get_checkpoint_file_name(epoch):
    return f"epoch_{epoch:02d}_checkpoint.keras"


# 保存されたチェックポイントファイルから最大のエポック番号を取得
def get_latest_checkpoint_epoch(checkpoint_dir):
    pattern = re.compile(r"epoch_(\d+)_checkpoint\.keras")
    max_epoch = -1
    for filename in os.listdir(checkpoint_dir):
        match = pattern.match(filename)
        if match:
            epoch = int(match.group(1))
            if epoch > max_epoch:
                max_epoch = epoch
    return max_epoch


# カスタムコールバックの定義
class EpochLogger(keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        print(f"Epoch {epoch+1} finished. Saving parameters.")


if __name__ == "__main__":

    ## 乱数
    np.random.seed(123)
    tf.random.set_seed(123)

    ## データ取得
    print("[start load_data]")
    (x_train, t_train), (x_val, t_val), (x_eval, t_eval) = load_data.load_data(
        TRAIN_INPUT_DIR
    )
    print("[end load_data]")

    ## モデルの定義
    print("[start construct Model]")
    # 最大のエポック番号を取得
    latest_epoch = get_latest_checkpoint_epoch(CHECK_POINT_DIR)
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
    print("[end construct Model]")

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

    history = model.fit(
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
            EpochLogger(),
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
    print(f"end:{end}")

    plot.plot(history, OUTPUT_FIG_FILE_NAME)

    if is_colab():
        with open("figure_path.txt", "w") as f:
            f.write(OUTPUT_FIG_FILE_NAME)
