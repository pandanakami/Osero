# ====================
# 学習サイクルの実行
# ====================

# パッケージのインポート
from dual_network import dual_network
from enum import Enum
import pickle
import os
from path_mng import get_path
import json


class ProgressState(Enum):
    UNINIT = -1
    START = 0
    END_SELF_PLAY = 1
    END_TRAIN = 2
    END_EVALUATE = 3
    END_CHECK = 4


PROGRESS_PATH = get_path("progress/progress.pkl")
PROGRESS_JSON_PATH = get_path("progress/progress.json")


class VsOldModelResult:
    def __init__(self, old=0, new=0):
        self.old_model_win = old
        self.new_model_win = new


class Progress:
    # 進捗ファイル読み込み
    def load():
        if os.path.exists(PROGRESS_PATH):
            with open(PROGRESS_PATH, mode="rb") as f:
                return pickle.load(f)
        else:
            return Progress()

    # コンストラクタ
    def __init__(self):
        self.loop_index = 0
        self._state: ProgressState = ProgressState.UNINIT
        self.play_count = 0
        self.eval_result = []
        self.vs_old_result = []
        self.vs_old_pred_only_result = []

    # 初期化
    def init(self):
        if self._state != ProgressState.UNINIT:
            # 初期化済
            return

        # デュアルネットワークの作成
        dual_network()
        self._state = ProgressState.START
        self.loop_index = 0
        self._save()

    # ループ更新
    def update_loop(self):
        self.loop_index += 1
        self._state = ProgressState.START
        self._save()

    # 状態更新
    def set_state(self, state: ProgressState):
        if state == ProgressState.UNINIT:
            raise RuntimeError("だめ")
        self._state = state
        self._save()

    def get_state(self):
        return self._state

    def update_play_count(self, num=1):
        self.play_count += num
        self._save()

    def add_eval_result(self, result: float):
        if len(self.eval_result) <= self.loop_index:
            self.eval_result.append(result)
        else:
            self.eval_result[self.loop_index] = result
        self._save()

    def add_vs_old_result(self, result: VsOldModelResult):
        if len(self.vs_old_result) <= self.loop_index:
            self.vs_old_result.append(result)
        else:
            self.vs_old_result[self.loop_index] = result
        self._save()

    def add_vs_old_pred_only_result(self, result: VsOldModelResult):
        if len(self.vs_old_pred_only_result) <= self.loop_index:
            self.vs_old_pred_only_result.append(result)
        else:
            self.vs_old_pred_only_result[self.loop_index] = result
        self._save()

    # ファイル保存
    def _save(self):
        os.makedirs(os.path.dirname(PROGRESS_PATH), exist_ok=True)
        with open(PROGRESS_PATH, mode="wb") as f:
            pickle.dump(self, f)

    def print(self):
        print(f"loop index:{self.loop_index}")
        print(f"state:{self._state}")

        print("eval")
        for i, o in enumerate(self.eval_result):
            print(f"{i}:: eval rate:{o}")

        print("vs old")
        for i, _o in enumerate(self.vs_old_result):
            o: VsOldModelResult = _o
            print(f"{i}:: old_win:{o.old_model_win}, new_win:{o.new_model_win}")

        print("vs old(pred only)")
        for i, _o in enumerate(self.vs_old_pred_only_result):
            o: VsOldModelResult = _o
            print(f"{i}:: old_win:{o.old_model_win}, new_win:{o.new_model_win}")


if __name__ == "__main__":
    progress = Progress.load()
    progress.print()
