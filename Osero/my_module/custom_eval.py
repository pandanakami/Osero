import numpy as np
from my_module.model.model_cmn import OSERO_WIDTH, OSERO_HEIGHT


def _convertY(data):
    data = data.copy()
    result = []
    for row in data:
        # 行の中で一番大きい値とそのインデックスを取得
        first_max_idx = np.argmax(row)
        first_max_value = row[first_max_idx]

        # 一番大きい値を除いた配列を作成して二番目に大きい値を取得
        row_excluding_first_max = np.delete(row, first_max_idx)
        second_max_idx = np.argmax(row_excluding_first_max)

        # 二番目に大きい値のインデックスを元の配列のインデックスに修正
        if second_max_idx >= first_max_idx:
            second_max_idx += 1

        second_max_value = row[second_max_idx]

        # 辞書形式で結果を格納
        result.append(
            {
                "first_max_index": first_max_idx,
                "first_max_value": first_max_value,
                "second_max_index": second_max_idx,
                "second_max_value": second_max_value,
            }
        )
    return result


def _convertX(data):
    return np.argmax(data, axis=3)


EMPTY = 0
SELF_STONE = 1
OTHER_STONE = 2


def IS_PASS(x, y):
    return y == 8 and x == 0


# ひっくり返るかチェック
def enable_replace(x, y, field_data, i, j):
    # 無視
    if i == 0 and j == 0:
        return False

    x += i
    y += j
    # 探索場所が範囲外の場合　無視
    if not (0 <= x and x < OSERO_WIDTH and 0 <= y and y < OSERO_HEIGHT):
        return False

    # 置いた隣が相手　無視
    if field_data[y][x] != OTHER_STONE:
        return False

    # 以降一つでも相手がある
    while True:
        x += i
        y += j
        # 探索場所が範囲外の場合　終了
        if not (0 <= x and x < OSERO_WIDTH and 0 <= y and y < OSERO_HEIGHT):
            return False
        # 探索場所が相手　継続
        if field_data[y][x] == OTHER_STONE:
            continue
        # 探索場所が自分　入れ替えれる　終了
        elif field_data[y][x] == SELF_STONE:
            return True
        # 探索場所が空白　終了
        else:
            return False


def _enable_put(map_data, x, y):
    # パスはTrue
    if IS_PASS(x, y):
        return True

    # 置こうとする場所が埋まっている
    if map_data[y][x] != EMPTY:
        return False

    # 各方向どれか一つでも置ける
    for j in [-1, 0, 1]:
        for i in [-1, 0, 1]:
            if enable_replace(x, y, map_data, i, j):
                return True

    return False


# 置けるか否かで正当性検証
def custom_eval(x_eval, y_eval):
    x_eval = _convertX(x_eval)
    y_eval = _convertY(y_eval)

    # 一番高確率のやつが正常における数
    f_count = 0
    # 二番目まで高確率のやつが正常における数
    f_s_count = 0

    for i, yData in enumerate(y_eval):

        pos = yData["first_max_index"]
        x = pos % 8
        y = pos // 8

        # マップ
        map_data = x_eval[i]

        check_f = _enable_put(map_data, x, y)
        if check_f:
            f_count += 1
            f_s_count += 1

        # 2番目の確率が0.1以上なら置けるか調べてみる
        elif yData["second_max_value"] > 0.1:
            pos = yData["second_max_index"]
            x = pos % 8
            y = pos // 8
            check_s = _enable_put(map_data, x, y)
            if check_s:
                f_s_count += 1

    data_num = len(y_eval)
    f_probability = float(f_count) / data_num
    f_s_probability = float(f_s_count) / data_num
    return [f_probability, f_s_probability]
