import sys
import keras
import tensorflow as tf
import numpy as np

from my_module.osero_model import MODEL_NAME

import my_module.load_data as load_data
from my_module import util
from my_module.util import IS_PROTO
from my_module.param import (
    OUTPUT_FILE_NAME,
    TRAIN_INPUT_DIR,
)
from my_module.custom_eval import custom_eval

print("[version info]")
print(f"\tTensorflow:{tf.__version__}")
print(f"\tKeras:{keras.__version__}")

args = util.args

print("[MODE]")
if IS_PROTO:
    print("\tPROTOTYPING MODE")
else:
    print("\tFULL MODE")

print("[MODEL]")
print(f"\t{MODEL_NAME}")

print("\n")


# 評価
def evaluate(model, x, t, is_difficult=False):

    tag = "difficult evaluate" if is_difficult else "evaluate"

    ## 評価
    print(f"[start {tag}]")
    score = model.evaluate(x, t, verbose=0)
    print(f"[end {tag}]")
    print(f"\tloss:{score[0]:3f}, acc:{score[1]:3f}\n")


# 評価(置けるか否か)
def evaluate_enable_put(model, x_eval):
    ## 評価(置けるか否か)
    y_eval = model.predict(x_eval)
    custom_acc = custom_eval(x_eval, y_eval)
    print(f"\tenable_put_acc:{custom_acc[0]:3f}, {custom_acc[1]:3f}\n")


if __name__ == "__main__":

    ## 乱数
    np.random.seed(123)
    tf.random.set_seed(123)

    ## データ取得
    print("[start load_data]")
    (_, _), (_, _), (x_eval, t_eval), (x_eval_difficult, t_eval_difficult) = (
        load_data.load_data(TRAIN_INPUT_DIR)
    )
    print("[end load_data]\n")

    ## モデルの読み込み
    model = keras.models.load_model(OUTPUT_FILE_NAME)

    # 評価
    evaluate(model, x_eval, t_eval)

    # 評価(難しいデータ)
    evaluate(model, x_eval_difficult, t_eval_difficult, True)

    ## 評価(置けるか否か)
    y_eval = model.predict(x_eval)
    custom_acc = custom_eval(x_eval, y_eval)
    print(f"\tenable_put_acc:{custom_acc[0]:3f}, {custom_acc[1]:3f}\n")

    sys.exit()
