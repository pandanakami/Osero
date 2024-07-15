import os
import shutil

os.environ["NOT_USE_MODEL"] = "True"
from progress import Progress, ProgressState


def reset_progress(loop_index):
    progress = Progress.load()

    progress.loop_index = loop_index
    progress.reset_play_count()
    progress.set_state(ProgressState.START)

    if os.path.exists("game_history_tmp.pkl"):
        shutil.rmtree("game_history_tmp.pkl")
