import sys
import os
import keras
import tensorflow as tf
import numpy as np
import eval_osero

from my_module.osero_model import MODEL_NAME, load_model

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


    for i in range(0,22):
        if i==9:
            continue
        model_name = f"Simple_{i:02d}"
        name = f"output/{model_name}_proto.keras"
        ## モデルの読み込み
        model = load_model(name)

        # 評価(難しいデータ)
        print("[Model]")
        print(f"\t{model_name}")
        eval_osero.evaluate(model, x_eval_difficult, t_eval_difficult, True)

    sys.exit()
