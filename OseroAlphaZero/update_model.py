from gdrive_mng import GoogleDriveMng
import reset_progress
import os
import shutil

LOOP_INDEX = 3
DO_BACKUP = False

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
