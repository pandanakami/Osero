from tensorflow import keras
from keras.layers import Conv2D, Dense, BatchNormalization

INPUT_CHANNEL = 3
OSERO_HEIGHT = 8
OSERO_WIDTH = 8
INPUT_SIZE = OSERO_HEIGHT * OSERO_WIDTH
OUTPUT_SIZE = OSERO_HEIGHT * OSERO_WIDTH + 1


def is_channel_first():
    keras.backend.image_data_format() == "channels_first"


def input_shape():

    if is_channel_first():
        # チャンネルファースト
        return (INPUT_CHANNEL, OSERO_HEIGHT, OSERO_HEIGHT)
    else:
        # チャンネルラスト
        return (OSERO_HEIGHT, OSERO_HEIGHT, INPUT_CHANNEL)


def conv(kernel_size, out_size, activation, is_padding=True, is_start=False):
    padding = "same" if is_padding else "valid"
    if is_start:
        return Conv2D(
            out_size,
            kernel_size=(kernel_size, kernel_size),
            activation=activation,
            input_shape=input_shape(),
            padding=padding,
            kernel_initializer=keras.initializers.he_normal,
        )
    else:
        return Conv2D(
            out_size,
            kernel_size=(kernel_size, kernel_size),
            activation=activation,
            padding=padding,
            kernel_initializer=keras.initializers.he_normal,
        )


def conv_bn(
    model, kernel_size, out_size, activation_layer_obj, is_padding=True, is_start=False
):
    padding = "same" if is_padding else "valid"
    if is_start:
        model.add(
            Conv2D(
                out_size,
                kernel_size=(kernel_size, kernel_size),
                input_shape=input_shape(),
                padding=padding,
                kernel_initializer=keras.initializers.he_normal,
            )
        )
    else:
        model.add(
            Conv2D(
                out_size,
                kernel_size=(kernel_size, kernel_size),
                padding=padding,
                kernel_initializer=keras.initializers.he_normal,
            )
        )
    model.add(BatchNormalization())
    model.add(activation_layer_obj)


# モデルついかしておく、accuracyも併記、earlystoppingカスタム


def dense(out_size, activation):
    return Dense(
        out_size,
        activation=activation,
        kernel_initializer=keras.initializers.he_normal,
    )


def dense_bn(model, out_size, activation_layer_obj):
    model.add(
        Dense(
            out_size,
            kernel_initializer=keras.initializers.he_normal,
        )
    )
    model.add(BatchNormalization())
    model.add(activation_layer_obj)


def model_debug_disp(model):
    print("[debug_model_info]")
    # レイヤー情報
    for i, layer in enumerate(model.layers):
        weights = layer.get_weights()
        s = f"[{i}] {layer.__class__}"
        if len(weights) == 0:
            s += ", "
        else:
            k = ""
            for j, o in enumerate(weights):
                k += str(o.shape) + ", "
            s += f", weights_shape:{k}"
        print(f"\t{s}output_shape:{layer.output_shape}")
