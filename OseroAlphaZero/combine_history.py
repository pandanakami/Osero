import os
from gdrive_mng import GoogleDriveMng
import shutil
import merge_history
import extend_history
import sys

try:
    No = int(sys.argv[1])
except ValueError:
    print("Please provide a valid integer.")
    sys.exit(1)


has_raspi = True
do_download = True
do_merge = True
dir = f"../backup/{No:03}_pre_fit"

if do_download:
    # バックアップ生成
    if os.path.exists(dir):
        raise FileExistsError("既にあるよ。")
    os.makedirs(dir, exist_ok=False)

    # ローカル
    dir2 = os.path.join(dir, "local")
    os.makedirs(dir2, exist_ok=False)
    shutil.copy("game_history_tmp.pkl", os.path.join(dir2, "game_history_tmp.pkl"))
    shutil.copytree("progress", os.path.join(dir2, "progress"))

# GDriveからダウンロード
gdrive = GoogleDriveMng()


def download(remote_base, local_base):
    local_base = str.replace(local_base, "/", "\\")
    dir2 = os.path.join(dir, local_base)
    os.makedirs(dir2, exist_ok=False)
    dir3 = os.path.join(dir2, "progress")
    os.makedirs(dir3, exist_ok=False)
    gdrive.download_file(
        os.path.join(remote_base, "game_history_tmp.pkl"),
        os.path.join(dir2, "game_history_tmp.pkl"),
    )
    gdrive.download_file(
        os.path.join(remote_base, "progress/progress.pkl"),
        os.path.join(dir3, "progress.pkl"),
    )


if do_download:
    # google colab
    download("osero_rl", "colab")

    # sage maker
    for i in range(4):
        download(f"osero_rl/sage_maker/{i}", f"sage_maker/{i}")

    if has_raspi:
        # raspberry pi
        for i in range(4):
            download(f"osero_rl/raspi/{i}", f"raspi/{i}")


## マージ
def merge(input1, input2, output):
    input1 = os.path.join(dir, input1)
    input2 = os.path.join(dir, input2)
    output = os.path.join(dir, output)
    os.makedirs(output)
    merge_history.merge(input1, input2, output)


if do_merge:
    if has_raspi:
        merge("local", "colab", "tmp0")
        merge("sage_maker/0", "sage_maker/1", "tmp1")
        merge("sage_maker/2", "sage_maker/3", "tmp2")
        merge("raspi/0", "raspi/1", "tmp3")
        merge("raspi/2", "raspi/3", "tmp4")
        merge("tmp0", "tmp1", "tmp10")
        merge("tmp2", "tmp3", "tmp11")
        merge("tmp10", "tmp11", "tmp20")
        merge("tmp20", "tmp4", "combine")
    else:
        merge("local", "colab", "tmp0")
        merge("sage_maker/0", "sage_maker/1", "tmp1")
        merge("sage_maker/2", "sage_maker/3", "tmp2")
        merge("tmp0", "tmp1", "tmp10")
        merge("tmp10", "tmp2", "combine")

## 拡張
output_dir = os.path.join(dir, "extend")
input_dir = os.path.join(dir, "combine")
extend_history.extend(input_dir, output_dir)


def rm(path):
    path = os.path.join(dir, path)
    shutil.rmtree(path)


# テンポラリ削除
rm("tmp0")
rm("tmp1")
rm("tmp2")
rm("tmp10")
rm("combine")

if has_raspi:
    rm("tmp3")
    rm("tmp4")
    rm("tmp11")
    rm("tmp20")

# アップロード
gdrive.upload_file(
    os.path.join(output_dir, "game_history_tmp.pkl"), "osero_rl/game_history_tmp.pkl"
)
gdrive.upload_file(
    os.path.join(output_dir, "progress/progress.pkl"), "osero_rl/progress/progress.pkl"
)
