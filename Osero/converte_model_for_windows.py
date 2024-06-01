
import os
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

def delete_all(folder_path):
    # 指定フォルダ内の全ファイルを削除
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            os.unlink(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

if __name__ == "__main__":

    ## 乱数
    np.random.seed(123)
    tf.random.set_seed(123)

    ## モデルの読み込み
    model:keras.models.Sequential = keras.models.load_model(OUTPUT_FILE_NAME)
    weights = model.get_weights()

    name = os.path.basename(OUTPUT_FILE_NAME)
    dir = os.path.dirname(OUTPUT_FILE_NAME)
    name = os.path.splitext(name)[0]
    output_dir = os.path.join(dir, name)
    os.makedirs(output_dir, exist_ok=True)
    delete_all(output_dir)#中身を空にする

    for i, w in enumerate(weights):
        save_file_name = os.path.join(output_dir, f"{i:003d}.npy")
        np.save(save_file_name, w)
        print(save_file_name)



