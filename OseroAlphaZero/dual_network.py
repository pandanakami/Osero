# ====================
# デュアルネットワークの作成
# ====================
print("load start : dual_network")

# パッケージのインポート
from keras.layers import (
    Activation,
    Add,
    BatchNormalization,
    Conv2D,
    Dense,
    GlobalAveragePooling2D,
    Input,
)
from keras.models import Model
from keras.regularizers import l2
from keras import backend as K
import os
from game import BOARD_WIDTH, BOARD_SIZE
from path_mng import get_path

# パラメータの準備
DN_FILTERS = 128  # 畳み込み層のカーネル数（本家は256）
DN_RESIDUAL_NUM = 16  # 残差ブロックの数（本家は19）
DN_INPUT_SHAPE = (BOARD_WIDTH, BOARD_WIDTH, 2)  # 入力シェイプ
DN_OUTPUT_SIZE = BOARD_SIZE + 1  # 行動数(配置先(x*x)+パス(1))


# 畳み込み層の作成
def conv(filters):
    return Conv2D(
        filters,
        3,
        padding="same",
        use_bias=False,
        kernel_initializer="he_normal",
        kernel_regularizer=l2(0.0005),
    )


# 残差ブロックの作成
def residual_block():
    def f(x):
        sc = x
        x = conv(DN_FILTERS)(x)
        x = BatchNormalization()(x)
        x = Activation("relu")(x)
        x = conv(DN_FILTERS)(x)
        x = BatchNormalization()(x)
        x = Add()([x, sc])
        x = Activation("relu")(x)
        return x

    return f


# デュアルネットワークの作成
def dual_network():
    # モデル作成済みの場合は無処理
    if os.path.exists(get_path("./model/best.h5")):
        return

    # 入力層
    input = Input(shape=DN_INPUT_SHAPE)

    # 畳み込み層
    x = conv(DN_FILTERS)(input)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    # 残差ブロック x 16
    for i in range(DN_RESIDUAL_NUM):
        x = residual_block()(x)

    # プーリング層
    x = GlobalAveragePooling2D()(x)

    # ポリシー出力
    p = Dense(
        DN_OUTPUT_SIZE, kernel_regularizer=l2(0.0005), activation="softmax", name="pi"
    )(x)

    # バリュー出力
    v = Dense(1, kernel_regularizer=l2(0.0005))(x)
    v = Activation("tanh", name="v")(v)

    # モデルの作成
    model = Model(inputs=input, outputs=[p, v])

    # モデルの保存
    os.makedirs(get_path("./model/"), exist_ok=True)  # フォルダがない時は生成
    model.save(get_path("./model/best.h5"))  # ベストプレイヤーのモデル

    # モデルの破棄
    K.clear_session()
    del model


# 動作確認
if __name__ == "__main__":
    dual_network()

print("load end : dual_network")
