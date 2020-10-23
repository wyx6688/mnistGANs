from tensorflow.keras.layers import Conv2D, Dropout, Flatten, Dense, Reshape, Conv2DTranspose, ReLU, BatchNormalization, LeakyReLU
from tensorflow import keras
import tensorflow as tf


def mnist_uni_gen_cnn(input_shape):
    return keras.Sequential([
        # [n, latent] -> [n, 7 * 7 * 128] -> [n, 7, 7, 128]
        Dense(7 * 7 * 128, input_shape=input_shape),
        BatchNormalization(),
        ReLU(),
        Reshape((7, 7, 128)),
        # -> [n, 14, 14, 64]
        Conv2DTranspose(64, (4, 4), strides=(2, 2), padding='same'),
        BatchNormalization(),
        ReLU(),
        # -> [n, 28, 28, 32]
        Conv2DTranspose(32, (4, 4), strides=(2, 2), padding='same'),
        BatchNormalization(),
        ReLU(),
        # -> [n, 28, 28, 1]
        Conv2D(1, (4, 4), padding='same', activation=keras.activations.tanh)
    ])


def mnist_uni_disc_cnn(input_shape=(28, 28, 1), use_bn=True):
    model = keras.Sequential()
    # [n, 28, 28, n] -> [n, 14, 14, 64]
    model.add(Conv2D(64, (4, 4), strides=(2, 2), padding='same', input_shape=input_shape))
    if use_bn:
        model.add(BatchNormalization())
    model.add(LeakyReLU())
    model.add(Dropout(0.3))
    # -> [n, 7, 7, 128]
    model.add(Conv2D(128, (4, 4), strides=(2, 2), padding='same'))
    if use_bn:
        model.add(BatchNormalization())
    model.add(LeakyReLU())
    model.add(Dropout(0.3))
    model.add(Flatten())
    return model


def mnist_uni_img2img(img_shape, name="generator"):
    model = keras.Sequential([
        # [n, 28, 28, n] -> [n, 14, 14, 64]
        Conv2D(64, (4, 4), strides=(2, 2), padding='same', input_shape=img_shape),
        BatchNormalization(),
        LeakyReLU(),
        # -> [n, 7, 7, 128]
        Conv2D(128, (4, 4), strides=(2, 2), padding='same'),
        BatchNormalization(),
        LeakyReLU(),

        # -> [n, 14, 14, 64]
        Conv2DTranspose(64, (4, 4), strides=(2, 2), padding='same'),
        BatchNormalization(),
        ReLU(),
        # -> [n, 28, 28, 32]
        Conv2DTranspose(32, (4, 4), strides=(2, 2), padding='same'),
        BatchNormalization(),
        ReLU(),
        # -> [n, 28, 28, 1]
        Conv2D(img_shape[-1], (4, 4), padding='same', activation=keras.activations.tanh)
    ], name=name)
    return model


def mnist_unet(img_shape):
    i = keras.Input(shape=img_shape, dtype=tf.float32)
    # [n, 28, 28, n] -> [n, 14, 14, 64]
    l1 = Conv2D(64, (4, 4), strides=(2, 2), padding='same', input_shape=img_shape)(i)
    l1 = BatchNormalization()(l1)
    l1 = LeakyReLU()(l1)
    # -> [n, 7, 7, 128]
    l2 = Conv2D(128, (4, 4), strides=(2, 2), padding='same')(l1)
    l2 = BatchNormalization()(l2)
    l2 = LeakyReLU()(l2)

    # -> [n, 14, 14, 64]
    u1 = Conv2DTranspose(64, (4, 4), strides=(2, 2), padding='same')(l2)
    u1 = BatchNormalization()(u1)
    u1 = ReLU()(u1)
    u1 = tf.concat((u1, l1), axis=3)    # -> [n, 14, 14, 64 + 64]
    # -> [n, 28, 28, 32]
    u2 = Conv2DTranspose(32, (4, 4), strides=(2, 2), padding='same')(u1)
    u2 = BatchNormalization()(u2)
    u2 = ReLU()(u2)
    u2 = tf.concat((u2, i), axis=3)     # -> [n, 28, 28, 32 + n]
    # -> [n, 28, 28, 1]
    o = Conv2D(img_shape[-1], (4, 4), padding='same', activation=keras.activations.tanh)(u2)

    unet = keras.Model(i, o, name="unet")
    return unet



