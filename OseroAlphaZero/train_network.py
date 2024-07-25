# ====================
# パラメータ更新部
# ====================

# パッケージのインポート
from dual_network import DN_INPUT_SHAPE
from keras.callbacks import (
    LearningRateScheduler,
    LambdaCallback,
    ModelCheckpoint,
    TensorBoard,
    EarlyStopping,
)
from keras.models import load_model, Model
from keras import backend as K
from keras.metrics import Accuracy
from pathlib import Path
import numpy as np
import pickle
from path_mng import get_path
from sklearn.model_selection import train_test_split
import tensorflow as tf
import os


# パラメータの準備
RN_EPOCHS = 100  # 学習回数


def checkpoint_dir(cycle: int):
    return "checkpoint/" + str(cycle)


# 学習データの読み込み
def load_data():
    history_path = sorted(Path(get_path("./game_history")).glob("*.history"))[-1]
    print(f"load history:{history_path}")
    with history_path.open(mode="rb") as f:
        return pickle.load(f)


def callbacks(cycle: int):

    ret = []

    # チェックポイント
    cb = ModelCheckpoint(
        filepath=get_path(checkpoint_dir(cycle) + "/{epoch:03d}_model_checkpoint.h5"),
        save_weights_only=True,
        save_best_only=False,
        verbose=0,
        monitor="val_loss",
        period=20,
        mode="auto",
    )
    ret.append(cb)

    # TensorBoard
    cb = TensorBoard(log_dir=get_path(f"tb_log/{cycle}"), histogram_freq=1)
    ret.append(cb)

    # EarlyStopping
    # cb = EarlyStopping(monitor="val_loss", patience=5)
    # ret.append(cb)

    # 学習率
    def step_decay(epoch):
        x = 0.001
        if epoch >= 50:
            x = 0.0005
        if epoch >= 80:
            x = 0.00025
        return x

    cb = LearningRateScheduler(step_decay)
    ret.append(cb)

    # CB
    cb = LambdaCallback(
        on_epoch_begin=lambda epoch, logs: print(
            "\rTrain {}/{}".format(epoch + 1, RN_EPOCHS), end=""
        )
    )
    ret.append(cb)

    return ret


# 再開時はモデルロード
def _load_model_if_resume(model: Model, cycle: int) -> int:

    # モデルロード
    initial_epoch = 0
    dir_path = get_path(checkpoint_dir(cycle))
    if os.path.exists(dir_path):
        # 再開
        files = files = os.listdir(dir_path)
        if len(files) > 0:
            # 一番最後の要素(ファイル名)を取得
            files = sorted(files)
            file = files[-1]
            # 先頭3文字(epoch)数値化。これを開始エポックにする
            initial_epoch = int(file[:3])
            model.load_weights(os.path.join(dir_path, file))

    return initial_epoch


# デュアルネットワークの学習
def train_network(cycle: int):
    CORE_NUM = os.cpu_count()
    # オペレーション内の並列実行
    tf.config.threading.set_intra_op_parallelism_threads(CORE_NUM)
    # オペレーション間の並列実行
    tf.config.threading.set_inter_op_parallelism_threads(CORE_NUM)

    # 学習データの読み込み
    history = load_data()
    xs, y_policies, y_values = zip(*history)

    # 学習のための入力データのシェイプの変換
    a, b, c = DN_INPUT_SHAPE
    xs = np.array(xs)
    # 自状態、相手状態でone-hot化
    xs = xs.reshape(len(xs), c, a, b).transpose(0, 2, 3, 1)
    y_policies = np.array(y_policies)
    y_values = np.array(y_values)

    # ベストプレイヤーのモデルの読み込み
    model: Model = load_model(get_path("./model/best.h5"))

    initial_epoch = _load_model_if_resume(model, cycle)

    # モデルのコンパイル
    model.compile(
        loss=["categorical_crossentropy", "mse"],
        optimizer="adam",
        metrics=[Accuracy().name],
    )

    x_train, x_val, y1_train, y1_val, y2_train, y2_val = train_test_split(
        xs, y_policies, y_values, test_size=0.1, random_state=4
    )
    # 学習の実行
    model.fit(
        x_train,
        [y1_train, y2_train],
        batch_size=128,
        epochs=RN_EPOCHS,
        verbose=1,
        callbacks=[callbacks(cycle)],
        initial_epoch=initial_epoch,
        validation_data=(x_val, [y1_val, y2_val]),
        use_multiprocessing=True,  # マルチプロセッシングを有効化
        workers=CORE_NUM,  # ワーカープロセスの数を設定
    )
    print("")

    # 最新プレイヤーのモデルの保存
    model.save(get_path("./model/latest.h5"))

    # モデルの破棄
    K.clear_session()
    del model


# 動作確認
if __name__ == "__main__":
    train_network(999)
