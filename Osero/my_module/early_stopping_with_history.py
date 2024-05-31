# カスタムコールバックの定義
import keras
import os
import numpy as np
import json
from my_module.osero_model import MODEL_NAME
from my_module.util import args, get_checkpoint_file_name, discord_write
from my_module.param import CHECK_POINT_DIR, CHECK_POINT_HISTORY_NAME


class EarlyStoppingWithHistory(keras.callbacks.Callback):
    def __init__(
        self, history, monitor="val_loss", patience=5, restore_best_weights=False
    ):
        super(EarlyStoppingWithHistory, self).__init__()
        if monitor == "loss" or monitor == "val_loss":
            self.monitor = monitor
        else:
            raise KeyError("対象外")

        self.patience = patience
        self.restore_best_weights = restore_best_weights
        self.history = history

    def on_train_begin(self, logs=None):
        # 履歴からベストエポックを取り適用
        if self.history:
            # 履歴からベスト値を持つ要素をとる
            best_item = min(self.history, key=lambda x: x[self.monitor])

            self.best_value = best_item[self.monitor]  # ベスト値
            self.stopped_epoch = best_item["epoch"]  # そのときのエポック
            # カウント
            self.wait = (
                self.history[len(self.history) - 1]["epoch"] - self.stopped_epoch
            )
            if self.restore_best_weights:
                file_path = os.path.join(
                    CHECK_POINT_DIR, get_checkpoint_file_name(self.stopped_epoch)
                )
                # ウェイト
                self.best_weights = keras.models.load_model(file_path).get_weights()

        else:
            # 履歴なければ初期値
            self.best_value = np.Inf
            self.wait = 0
            self.stopped_epoch = 0
            self.best_weights = None

    def on_epoch_end(self, epoch, logs=None):

        print(f"Epoch {epoch + 1} finished. Saving parameters.")
        self._save_history(epoch, logs)
        self._early_stopping(epoch, logs)

    def _save_history(self, epoch, logs):
        save_epoch = epoch + 1

        if args.detail_discord_ntfy:
            discord_write(f"update epoch:{save_epoch} ({MODEL_NAME})")

        result = next(
            (item for item in self.history if item["epoch"] == save_epoch), None
        )
        if result:
            print(f"override history epoch:{save_epoch}")
            result["loss"] = logs.get("loss")
            result["accuracy"] = logs.get("accuracy")
            result["val_loss"] = logs.get("val_loss")
            result["val_accuracy"] = logs.get("val_accuracy")
        else:
            self.history.append(
                {
                    "epoch": save_epoch,
                    "loss": logs.get("loss"),
                    "accuracy": logs.get("accuracy"),
                    "val_loss": logs.get("val_loss"),
                    "val_accuracy": logs.get("val_accuracy"),
                }
            )
            test = json.dumps(self.history, indent=4)
            with open(CHECK_POINT_HISTORY_NAME, "w") as file:
                file.write(test)

    def _early_stopping(self, epoch, logs):
        epoch += 1
        current_value = logs.get(self.monitor)
        if current_value is not None:
            # ベスト値更新
            if current_value < self.best_value:
                self.best_value = current_value
                self.wait = 0
                if self.restore_best_weights:
                    self.best_weights = self.model.get_weights()
            else:
                # 更新しない場合はカウント追加
                self.wait += 1
                # カウントが閾値超えたら終了
                if self.wait >= self.patience:
                    self.stopped_epoch = epoch
                    self.model.stop_training = True  # EarlyStopping設定

                    if self.restore_best_weights and self.best_weights is not None:
                        # 最高エポック時のウェイトを反映
                        self.model.set_weights(self.best_weights)

    def on_train_end(self, logs=None):
        if self.stopped_epoch > 0:
            print(f"\nEpoch {self.stopped_epoch + 1}: early stopping triggered")
