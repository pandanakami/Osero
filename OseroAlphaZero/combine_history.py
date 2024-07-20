import os
from gdrive_mng import GoogleDriveMng

os.environ["NOT_USE_MODEL"] = "True"
from progress import Progress, ProgressState
import shutil
import merge_history
import extend_history
import sys
import pickle

# 設定
#############################################################
# 実行処理設定
DO_DOWNLOAD = True
DO_MERGE = True
DO_EXTEND = True
DO_UPLOAD = True

# ダウンロード一覧(DO_DOWNLOAD=Falseの場合は無効)
HAS_LOCAL = True
HAS_COLAB = True
HAS_RASPI = True
HAS_SAGE_MAKER = True

# 共通処理
#############################################################
try:
    No = int(sys.argv[1])
except ValueError:
    print("Please provide a valid integer.")
    sys.exit(1)

dir = f"../backup/{No:03}_pre_fit"
output_dir = os.path.join(dir, "extend")

inputs = []

if (not DO_MERGE) and DO_EXTEND:
    print("対象外の設定, merge, extend")
    sys.exit(1)

if DO_DOWNLOAD or DO_UPLOAD:
    # GDriveからダウンロード
    gdrive = GoogleDriveMng()

#############################################################3

## ダウンロード
if DO_DOWNLOAD:

    def print_info(path):
        progress = Progress.load(os.path.join(path, "progress/progress.pkl"))
        with open(os.path.join(path, "game_history_tmp.pkl"), "rb") as f:
            history = pickle.load(f)
        print(
            f"{path}, loop_index:{progress.loop_index}, count:{progress.play_count}, history_num:{len(history)}"
        )

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
        inputs.append(local_base)
        print_info(dir2)

    # バックアップ生成
    if os.path.exists(dir):
        raise FileExistsError("既にあるよ。")
    os.makedirs(dir, exist_ok=False)

    # ローカル
    if HAS_LOCAL:
        dir2 = os.path.join(dir, "local")
        os.makedirs(dir2, exist_ok=False)
        shutil.copy("game_history_tmp.pkl", os.path.join(dir2, "game_history_tmp.pkl"))
        shutil.copytree("progress", os.path.join(dir2, "progress"))
        inputs.append("local")
        print_info(dir2)

    # google colab
    if HAS_COLAB:
        download("osero_rl", "colab")

    # sage maker
    if HAS_SAGE_MAKER:
        for i in range(4):
            download(f"osero_rl/sage_maker/{i}", f"sage_maker/{i}")

    if HAS_RASPI:
        # raspberry pi
        for i in range(4):
            download(f"osero_rl/raspi/{i}", f"raspi/{i}")
else:
    dirs = os.listdir(dir)
    dirs = [d for d in dirs if d != "extend"]

    for d in dirs:
        if d == "extend":
            continue
        elif d == "raspi" or d == "sage_maker":
            for i in range(4):
                inputs.append(os.path.join(d, f"{i}"))
        else:
            inputs.append(d)


## マージ
if DO_MERGE:

    def merge(input1, input2, output):
        input1 = os.path.join(dir, input1)
        input2 = os.path.join(dir, input2)
        output = os.path.join(dir, output)
        os.makedirs(output)
        merge_history.merge(input1, input2, output)

    in_list = inputs

    all_tmp_list = []
    out_list = [in_list[0]]

    while len(in_list) > 1:
        out_list = []
        # 奇数(3以上)
        if len(in_list) % 2 != 0:
            out_list.append(in_list.pop())
        for i in range(0, len(in_list), 2):
            if len(in_list) == 2 and len(out_list) == 0:
                out_dir = "combine"
                pass
            else:
                out_dir = f"tmp{len(all_tmp_list)}"

            all_tmp_list.append(out_dir)
            out_list.append(out_dir)
            merge(in_list[i], in_list[i + 1], out_dir)

        in_list = out_list

    def rm(path):
        path = os.path.join(dir, path)
        shutil.rmtree(path)

    ## 拡張
    input_dir = os.path.join(dir, out_list[0])
    if DO_EXTEND:
        extend_history.extend(input_dir, output_dir)
    else:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        shutil.copytree(input_dir, output_dir)

    # テンポラリ削除
    for path in all_tmp_list:
        rm(path)

## アップロード
if DO_UPLOAD:
    # アップロード
    gdrive.upload_file(
        os.path.join(output_dir, "game_history_tmp.pkl"),
        "osero_rl/game_history_tmp.pkl",
    )
    gdrive.upload_file(
        os.path.join(output_dir, "progress/progress.pkl"),
        "osero_rl/progress/progress.pkl",
    )
