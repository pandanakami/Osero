import os
from my_module.osero_model import MODEL_NAME
from my_module.util import IS_PROTO, is_colab

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

OUTPUT_FILE_NAME = os.path.join(OUTPUT_DIR, f"{SAVE_NAME}.keras")
OUTPUT_FIG_FILE_NAME = f"{SAVE_NAME}_fig.png"
OUTPUT_FIG_FILE_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FIG_FILE_NAME)
OUTPUT_LATEST_FIG_POS = os.path.join(BASE_DIR, "latest_fig_pos.txt")
CHECK_POINT_HISTORY_NAME = os.path.join(CHECK_POINT_DIR, "history.json")
