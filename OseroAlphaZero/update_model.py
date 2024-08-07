from gdrive_mng import GoogleDriveMng
import reset_progress
import os
import shutil
import sys
import calc_hash
from path_mng import get_path

try:
    LOOP_INDEX = int(sys.argv[1])
except ValueError:
    print("Please provide a valid integer.")
    sys.exit(1)


def is_windows():
    return os.name == "nt"


DO_BACKUP = is_windows()

# 履歴リセット
reset_progress.reset_progress(LOOP_INDEX)

# モデルダウンロード
gdrive = GoogleDriveMng()
gdrive.download_file("osero_rl/model/latest.h5", "model/latest.h5")
gdrive.download_file("osero_rl/model/best.h5", "model/best.h5")

# ローカルの場合、モデルバックアップ
if DO_BACKUP:
    dir = f"../backup/{(LOOP_INDEX-1):03}_after_fit"
    os.makedirs(dir)
    shutil.copy("model\\latest.h5", os.path.join(dir, "latest.h5"))

calc_hash.calculate_file_hash(get_path("model/latest.h5"))
