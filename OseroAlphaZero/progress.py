# ====================
# 学習サイクルの実行
# ====================

# パッケージのインポート
from dual_network import dual_network
from enum import Enum
import pickle
import os
from path_mng import get_path


class ProgressState(Enum):
    UNINIT = -1
    START = 0
    END_SELF_PLAY = 1
    END_TRAIN = 2
    END_EVALUATE = 3


PROGRESS_PATH = "progress/progress.pkl"


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

    # ファイル保存
    def _save(self):
        os.makedirs(os.path.dirname(PROGRESS_PATH), exist_ok=True)
        with open(PROGRESS_PATH, mode="wb") as f:
            pickle.dump(self, f)
