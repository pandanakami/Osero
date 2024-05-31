import os
import sys
import keras
import tensorflow as tf

from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import numpy as np
from sklearn.model_selection import train_test_split

import datetime

from my_module.osero_model import MODEL_NAME
from my_module.osero_model import get_model
import my_module.load_data as load_data
from my_module import plot
from my_module.gdrive_uploader import GoogleDriveFacade
from my_module.early_stopping_with_history import EarlyStoppingWithHistory
from my_module import util
from my_module.util import is_colab, IS_PROTO
from my_module.param import (
    CHECK_POINT_DIR,
    CHECK_POINT_HISTORY_NAME,
    OUTPUT_DIR,
    OUTPUT_FIG_FILE_PATH,
    OUTPUT_LATEST_FIG_POS,
    OUTPUT_FILE_NAME,
    TRAIN_INPUT_DIR,
)
import json

print("[version info]")
print(f"\tTensorflow:{tf.__version__}")
print(f"\tKeras:{keras.__version__}")

BATCH_SIZE = 100
EPOCH = 1000

args = util.args

print("[MODE]")
if IS_PROTO:
    print("\tPROTOTYPING MODE")
else:
    print("\tFULL MODE")

os.makedirs(CHECK_POINT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 履歴
train_history = []

if __name__ == "__main__":

    # google認証準備
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

    # 最大のエポック番号を取得
    latest_epoch = util.get_latest_checkpoint_epoch(train_history)
    if latest_epoch != -1:
        # ロード
        model = keras.models.load_model(
            os.path.join(CHECK_POINT_DIR, util.get_checkpoint_file_name(latest_epoch))
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
    print(f"model:{MODEL_NAME}")

    ## 学習プロセスを設定する
    model.compile(
        loss=keras.losses.SparseCategoricalCrossentropy(),
        optimizer=tf.keras.optimizers.Adam(),
        # 評価関数を指定
        metrics=[keras.metrics.Accuracy().name],
    )

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
            checkpoint_callback,
            EarlyStoppingWithHistory(
                train_history, monitor="val_loss", patience=5, restore_best_weights=True
            ),
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
    util.discord_write(
        f"{MODEL_NAME}: train finish. loss:{score[0]:3f}, acc:{score[1]:3f}"
    )

    ##図示
    plot.plot(
        train_history,
        OUTPUT_FIG_FILE_PATH,
        args.display_fig,
        args.save_fig,
    )

    if not is_colab():
        if not args.not_upload_to_gdrive:
            save_folder_id = "1r3nNbTkJk77eMMSVq-zXRz_gBaVbtd1x"
            # モデルアップロード
            gdrive_mng.upload(
                local_file_path=OUTPUT_FILE_NAME,
                save_folder_id=save_folder_id,
                is_convert=True,
            )

            if args.save_fig:
                # 図アップロード
                gdrive_mng.upload(
                    local_file_path=OUTPUT_FIG_FILE_PATH,
                    save_folder_id=save_folder_id,
                    is_convert=True,
                )

    if is_colab():
        with open(OUTPUT_LATEST_FIG_POS, "w") as f:
            f.write(OUTPUT_FIG_FILE_PATH)

    print("[end training]")
    sys.exit()
