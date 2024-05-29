import os

import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import numpy as np
from sklearn.model_selection import train_test_split
import re
import datetime

from osero_model import INPUT_CHANNEL, OUTPUT_SIZE
from osero_model import is_channel_first, get_model
import load_data


print(tf.__version__)
print(keras.__version__)

BATCH_SIZE = 100
EPOCH = 1000


def is_colab():
    return "COLAB_GPU" in os.environ


if is_colab():
    from google.colab import drive

    # Google Driveをマウント
    drive.mount("/content/drive")
    # Google Driveの保存ディレクトリを指定
    CHECK_POINT_DIR = "/content/drive/MyDrive/osero/checkpoints"
    TRAIN_INPUT_DIR = "content/drive/MyDrive/osero/input"
else:
    CHECK_POINT_DIR = "./checkpoints"
    TRAIN_INPUT_DIR = "../CreateTrainData/output/"

os.makedirs(CHECK_POINT_DIR, exist_ok=True)


def get_checkpoint_file_name(epoch):
    return f"epoch_{epoch:02d}_checkpoint.h5"


# 保存されたチェックポイントファイルから最大のエポック番号を取得
def get_latest_checkpoint_epoch(checkpoint_dir):
    pattern = re.compile(r"epoch_(\d+)_checkpoint\.h5")
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
        initial_epoch = latest_epoch + 1
        print(
            f"Loaded model from epoch {latest_epoch}. Resuming training from epoch {initial_epoch}."
        )
    else:
        # 最初から
        model = get_model()
        initial_epoch = 0
        print("No checkpoint found. Starting training from scratch.")
    print("[end construct Model]")

    ## 学習プロセスを設定する
    print("[start compile]")
    model.compile(
        loss=keras.losses.categorical_crossentropy,
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
        filepath=os.path.join(CHECK_POINT_DIR, "epoch_{epoch:02d}_checkpoint.h5"),
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
            EpochLogger(),
        ],
    )
    print("[end training]")

    ## 評価
    print("[start evaluate]")
    score = model.evaluate(x_eval, t_eval, verbose=0)
    print(f"[end evaluate] loss:{score[0]:3f}, acc:{score[1]:3f}")

    end = datetime.datetime.now()
    print(f"start:{start}")
    print(f"end:{end}")
