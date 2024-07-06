from progress import Progress, ProgressState
import pickle
import os

INPUT_1_DIR = "input1"
INPUT_2_DIR = "input2"
OUTPUT_DIR = "combine"


PROGRESS_1_PATH = os.path.join(os.path.join(INPUT_1_DIR, "progress"), "progress.pkl")
PROGRESS_2_PATH = os.path.join(os.path.join(INPUT_2_DIR, "progress"), "progress.pkl")
PROGRESS_OUTPUT_PATH = os.path.join(
    os.path.join(OUTPUT_DIR, "progress"), "progress.pkl"
)

HISTORY_1_PATH = os.path.join(INPUT_1_DIR, "game_history_tmp.pkl")
HISTORY_2_PATH = os.path.join(INPUT_2_DIR, "game_history_tmp.pkl")
HISTORY_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "game_history_tmp.pkl")

progress1 = Progress.load(PROGRESS_1_PATH)
progress2 = Progress.load(PROGRESS_2_PATH)

with open(HISTORY_1_PATH, "rb") as f:
    history1 = pickle.load(f)

with open(HISTORY_2_PATH, "rb") as f:
    history2 = pickle.load(f)

# 同条件であれば結合
if (
    progress1.loop_index == progress2.loop_index
    and progress1._state == ProgressState.START
    and progress2._state == ProgressState.START
):
    progress1.play_count += progress2.play_count
    history: list = history1
    history.extend(history2)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    progress1._save(PROGRESS_OUTPUT_PATH)
    with open(HISTORY_OUTPUT_PATH, "wb") as f:
        pickle.dump(history, f)

    print("Conbine!!!!")
else:
    print("Not !!!!!")
