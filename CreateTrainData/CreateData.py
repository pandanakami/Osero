from aifc import Error
import os
import pandas as pd
import numpy as np
import csv
import shutil
from SplitTrainEval import split_train_eval

BLACK = 2
WHITE = 1

SELF_STONE = 1
OTHER_STONE = 2


INIT_DATA = np.array(
    [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, WHITE, BLACK, 0, 0, 0],
        [0, 0, 0, BLACK, WHITE, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    dtype=np.uint8,
)

WIDTH = INIT_DATA.shape[1]
HEIGHT = INIT_DATA.shape[0]

DEBUG_OUTPUT = False


class TrainData:
    def __init__(self, field_data: np.ndarray, t_x: int, t_y: int, user: int):
        self.field_data = field_data.copy()
        self.t_x = t_x
        self.t_y = t_y
        self.user = user  # デバッグ用

    DEBUG_USER_DATA = ["・", "〇", "●", "☆", "★"]

    def debug_user(self):
        return self.DEBUG_USER_DATA[self.user]

    # デバッグ出力する
    def save_debug(self, writer):
        # 教師データを★として置く
        tmp = self.field_data.copy()
        if self.t_y < HEIGHT:
            tmp[self.t_y][self.t_x] = self.user + 2

        writer.writerow(
            [self.debug_user(), ""]
            + [self.DEBUG_USER_DATA[val] for val in tmp[0].tolist()]
            + ["", "→", "(", str(self.t_x), str(self.t_y), ")"]
        )

        for i in range(1, HEIGHT):
            writer.writerow(
                ["", ""] + [self.DEBUG_USER_DATA[val] for val in tmp[i].tolist()]
            )
        writer.writerow([])

    def train_x(self):
        other_user = BLACK if self.user == WHITE else WHITE
        output_array = np.zeros_like(self.field_data, dtype=np.uint8)
        output_array[self.field_data == self.user] = SELF_STONE
        output_array[self.field_data == other_user] = OTHER_STONE
        return output_array

    def train_t(self):
        return self.t_y * WIDTH + self.t_x


# ひっくり返るかチェック
def enable_replace(x, y, user, field_data, i, j):
    # 無視
    if i == 0 and j == 0:
        return False
    other_user = BLACK if user == WHITE else WHITE
    x += i
    y += j
    # 探索場所が範囲外の場合　無視
    if not (0 <= x and x < WIDTH and 0 <= y and y < HEIGHT):
        return False
    # 置いた隣が相手でない　無視
    if field_data[y][x] != other_user:
        return False
    # 以降一つでも相手がある
    while True:
        x += i
        y += j
        # 探索場所が範囲外の場合　終了
        if not (0 <= x and x < WIDTH and 0 <= y and y < HEIGHT):
            return False
        # 探索場所が相手　継続
        if field_data[y][x] == other_user:
            continue
        # 探索場所が自分　入れ替えれる　終了
        elif field_data[y][x] == user:
            return True
        # 探索場所が空白　終了
        else:
            return False


# ひっくり返す(事前にenable_replace()チェック済みであること)
def replace(x, y, user, field_data, i, j):
    # 無視
    if i == 0 and j == 0:
        return
    other_user = BLACK if user == WHITE else WHITE

    # 以降一つでも相手がある
    while True:
        x += i
        y += j

        # 探索場所が相手　入れ替え
        if field_data[y][x] == other_user:
            field_data[y][x] = user
            continue
        # 探索場所が自分　終了
        elif field_data[y][x] == user:
            return
        # 探索場所が空白　終了
        else:
            raise Error("?????")


# パスかチェック
def is_pass(x, y, user, field_data):

    # 各方向どれか一つでも置ける
    for j in [-1, 0, 1]:
        for i in [-1, 0, 1]:
            if enable_replace(x, y, user, field_data, i, j):
                return False

    return True


# フィールド更新
def update_field(x, y, user, field_data):

    field_data[y][x] = user

    for j in [-1, 0, 1]:
        for i in [-1, 0, 1]:
            if enable_replace(x, y, user, field_data, i, j):
                replace(x, y, user, field_data, i, j)


def getFiles(dir, extension):
    # 拡張子を小文字に変換しておく
    extension = extension.lower()
    # 指定した拡張子のファイルのリストを作成
    files = [
        os.path.join(dir, file)
        for file in os.listdir(dir)
        if file.lower().endswith(extension)
    ]
    return files


# 1譜面解析
def analyze_score(score_data, train_data_list: list):

    user = BLACK
    field_data = INIT_DATA.copy()

    # 整形(置いたx,y情報のリストに。)
    score_data = [score_data[i : i + 2] for i in range(0, len(score_data), 2)]

    # 1譜面解析
    for hands in score_data:

        # 手解析
        def analyze_hands(hands: str):
            x = ord(hands[0]) - ord("a")  # a~h
            y = ord(hands[1]) - ord("1")  # 1~8
            return x, y

        x, y = analyze_hands(hands)

        # パス
        if is_pass(x, y, user, field_data):
            result_x = 0
            result_y = HEIGHT

            # パスを保存
            train_data_list.append(TrainData(field_data, result_x, result_y, user))

            # ユーザー入れ替え
            user = BLACK if user == WHITE else WHITE

            # memo 入れ替えたら置けるはず。エラーチェックはしない

        result_x = x
        result_y = y

        # 保存
        train_data_list.append(TrainData(field_data, result_x, result_y, user))

        # フィールド更新
        update_field(x, y, user, field_data)

        # ユーザー入れ替え
        user = BLACK if user == WHITE else WHITE


# 保存
def save(train_data_list: list):
    list_train_x = [instance.train_x() for instance in train_data_list]
    list_train_x = np.stack(list_train_x)

    list_train_t = [instance.train_t() for instance in train_data_list]
    list_train_t = np.array(list_train_t, dtype=np.uint8)

    np.save("output/osero_train_full_x.npy", list_train_x)
    np.save("output/osero_train_full_t.npy", list_train_t)

    split_train_eval()

    if DEBUG_OUTPUT:
        np.savetxt(
            "osero_train_x.csv",
            list_train_x.reshape(-1, WIDTH * HEIGHT),
            delimiter=",",
            fmt="%d",
        )
        np.savetxt("osero_train_t.csv", list_train_t, delimiter=",", fmt="%d")


# 保存　デバッグ
def save_debug(train_data_list: list):
    # デバッグ保存
    with open("test.csv", "w", newline="", encoding="sjis") as csv_file:
        csv_writer = csv.writer(csv_file)
        for train_data in train_data_list:
            _train_data: TrainData = train_data
            _train_data.save_debug(csv_writer)


def main():

    # 出力フォルダリセット
    if os.path.exists("output"):
        shutil.rmtree("output")
    os.makedirs("output")

    # 入力ファイルたち
    files = getFiles("../WtbReader/output/", "csv")

    # 解析した訓練データ
    train_data_list = []

    file_num = len(files)
    for i, file in enumerate(files):
        # CSV読み込み(年度データ)
        df = pd.read_csv(file)
        year_data = df["transcript"]
        score_num = len(year_data)

        for j, score_data in enumerate(year_data):
            print(
                f"file:({i}/{file_num}) {'../WtbReader/output/0.csv'}, ({j}/{score_num})"
            )

            # 1試合の譜面データ
            analyze_score(score_data, train_data_list)

            if False:
                if i == 0 and j == 100:
                    save_debug(train_data_list)
                    save(train_data_list)
                    return

    save(train_data_list)

    if DEBUG_OUTPUT:
        save_debug(train_data_list)


if __name__ == "__main__":
    main()
