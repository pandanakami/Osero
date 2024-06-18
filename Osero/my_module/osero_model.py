from my_module.model import model_cmn
import my_module.util as util
import importlib
import keras
import numpy as np
import os

#####################################################
# モデル切り替え
if util.args.module:
    # 起動引数で指定されている場合
    module_path = "my_module.model."
    m = importlib.import_module(module_path + util.args.module)
else:
    from my_module.model import Simple_22 as m


#####################################################

MODEL_NAME = m.MODEL_NAME.split(".")[-1]

INPUT_CHANNEL = model_cmn.INPUT_CHANNEL
OSERO_HEIGHT = model_cmn.OSERO_HEIGHT
OSERO_WIDTH = model_cmn.OSERO_WIDTH
INPUT_SIZE = OSERO_HEIGHT * OSERO_WIDTH
OUTPUT_SIZE = OSERO_HEIGHT * OSERO_WIDTH + 1


def is_channel_first():
    return model_cmn.is_channel_first()


def input_shape():
    return model_cmn.input_shape()


def get_model(DEBUG=False):
    return m.get_model(DEBUG)


def load_model(file_name) -> keras.models.Sequential:

    ## モデルの読み込み
    if util.is_windows():
        """
        windowsだと他環境で作ったモデルのロードができない。
        ts, kerasバージョン合わせても同じ。
        推測だけど、tensorflow-intelがよろしくないのでは。
        なので、初期モデル作って、ウェイトをロードするようにする
        """
        model = get_model(True)
        weights = _load_weights_for_windows(file_name)
        model.set_weights(weights)
        ## 学習プロセスを設定する
        model.compile(
            loss=keras.losses.SparseCategoricalCrossentropy(),
            optimizer=keras.optimizers.Adam(),
            # 評価関数を指定
            metrics=[keras.metrics.Accuracy().name],
        )

    else:
        model = keras.models.load_model(file_name)
    return model


def _load_weights_for_windows(file_name):
    name = os.path.basename(file_name)
    dir = os.path.dirname(file_name)
    name = os.path.splitext(name)[0]
    input_dir = os.path.join(dir, name)

    ret = []
    # 指定フォルダ内の全ファイルを削除
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        ret.append(np.load(file_path))
    return ret
