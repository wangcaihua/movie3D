import numpy as np
from absl import logging, flags, app
import os
import cv2
from typing import Dict

import tensorflow as tf
from deep3d.utils import read_vgg16, bilinear
from tensorflow.keras.layers import Conv2D, MaxPooling2D, BatchNormalization, Conv2DTranspose, ReLU, Softmax
from tensorflow.keras.losses import MAE
from deep3d.data import FrameGenerator, VideoType
from deep3d.deep_dot import deep_fuse, deep_dot

FLAGS = flags.FLAGS
flags.DEFINE_integer('batch_size', 64, 'batch_size')
flags.DEFINE_integer('num_epoch', 1, 'num epoch')
flags.DEFINE_integer('depth_ks', 5, 'depth_ks')
flags.DEFINE_string('file_name', '/Volumes/data/baidu/Avatar_3D.mkv', 'input movie file_name')
# flags.DEFINE_string('file_name', '/Volumes/data/baidu/carrier.mp4', 'input movie file_name')
flags.DEFINE_string('model_dir', '/Users/fitz/data/code/deep3d/ckpt', 'input movie file_name')
flags.DEFINE_bool('profiler', True, 'whether start profiler')

params = read_vgg16('/Users/fitz/data/code/deep3d/vgg_16.ckpt')


def input_fn() -> tf.data.Dataset:
  logging.info('go to input_fn')
  gen = FrameGenerator(FLAGS.file_name, num_epoch=FLAGS.num_epoch, video_type=VideoType.SIMPLE)
  dataset = tf.data.Dataset.from_generator(generator=gen, output_signature=gen.signature)

  def map_fn(features):
    return {key: tf.cast(value, dtype=tf.float32) / 255.0 for key, value in features.items()}

  dataset = dataset.map(map_fn).batch(batch_size=FLAGS.batch_size, drop_remainder=True)
  dataset = dataset.prefetch(buffer_size=tf.data.AUTOTUNE)

  return dataset


def model_fn(features: Dict[str, tf.Tensor],
             labels: tf.Tensor,
             mode: str) -> tf.estimator.EstimatorSpec:
  logging.info('go to model_fn')
  data, labels = features['feature'], (labels or features.get('right', None))
  logging.info(f'the shape of left is {data.get_shape().as_list()}')
  depth = FLAGS.depth_ks * FLAGS.depth_ks

  # group 1
  data = Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding="same", name='conv1_1',
                kernel_initializer=tf.constant_initializer(params['conv1_1/weights']),
                bias_initializer=tf.constant_initializer(params['conv1_1/biases']))(data)
  data = Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding="same", name='conv1_2',
                kernel_initializer=tf.constant_initializer(params['conv1_2/weights']),
                bias_initializer=tf.constant_initializer(params['conv1_2/biases']))(data)
  data = MaxPooling2D(pool_size=(2, 2), strides=(2, 2))(data)
  emit1 = BatchNormalization()(data)
  emit1 = Conv2D(filters=depth, kernel_size=(3, 3), padding="same", activation='relu')(emit1)
  logging.info(f'the shape of emit1 is {emit1.get_shape().as_list()}]')
  emit1 = Conv2DTranspose(filters=depth, kernel_size=(1, 1), strides=(1, 1), use_bias=False)(emit1)
  logging.info(f'the shape of emit1 after Conv2DTranspose is {emit1.get_shape().as_list()}')

  # group 2
  data = Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding="same", name='conv2_1',
                kernel_initializer=tf.constant_initializer(params['conv2_1/weights']),
                bias_initializer=tf.constant_initializer(params['conv2_1/biases']))(data)
  data = Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding="same", name='conv2_2',
                kernel_initializer=tf.constant_initializer(params['conv2_2/weights']),
                bias_initializer=tf.constant_initializer(params['conv2_2/biases']))(data)
  data = MaxPooling2D(pool_size=(2, 2), strides=(2, 2))(data)
  emit2 = BatchNormalization()(data)
  emit2 = Conv2D(filters=depth, kernel_size=(3, 3), padding="same", activation='relu')(emit2)
  logging.info(f'the shape of emit2 is {emit2.get_shape().as_list()}]')
  emit2 = Conv2DTranspose(filters=depth, kernel_size=(4, 4), strides=(2, 2), padding="same", use_bias=False,
                          kernel_initializer=tf.constant_initializer(bilinear(shape=[4, 4, depth, depth])))(emit2)
  logging.info(f'the shape of emit2 after Conv2DTranspose is {emit2.get_shape().as_list()}')

  # group 3
  data = Conv2D(filters=256, kernel_size=(3, 3), activation='relu', padding="same", name='conv3_1',
                kernel_initializer=tf.constant_initializer(params['conv3_1/weights']),
                bias_initializer=tf.constant_initializer(params['conv3_1/biases']))(data)
  data = Conv2D(filters=256, kernel_size=(3, 3), activation='relu', padding="same", name='conv3_2',
                kernel_initializer=tf.constant_initializer(params['conv3_2/weights']),
                bias_initializer=tf.constant_initializer(params['conv3_2/biases']))(data)
  data = MaxPooling2D(pool_size=(2, 2), strides=(2, 2))(data)
  emit3 = BatchNormalization()(data)
  emit3 = Conv2D(filters=depth, kernel_size=(3, 3), padding="same", activation='relu')(emit3)
  logging.info(f'the shape of emit3 is {emit3.get_shape().as_list()}')
  emit3 = Conv2DTranspose(filters=depth, kernel_size=(8, 8), strides=(4, 4), padding="same", use_bias=False,
                          kernel_initializer=tf.constant_initializer(bilinear(shape=[8, 8, depth, depth])))(emit3)
  logging.info(f'the shape of emit3 after Conv2DTranspose is {emit3.get_shape().as_list()}')

  emit = ReLU()(emit1 * emit2 * emit3)
  emit = Conv2DTranspose(filters=depth, kernel_size=(4, 4), strides=(2, 2), padding="same", use_bias=False,
                         kernel_initializer=tf.constant_initializer(bilinear(shape=[4, 4, depth, depth])))(emit)
  logging.info(f'the shape of emit after Conv2DTranspose is {emit.get_shape().as_list()}')
  emit = Conv2D(filters=depth, kernel_size=(3, 3), padding="same")(ReLU()(emit))
  emit = Softmax(axis=-1)(emit)
  logging.info(f'the shape of emit is {emit.get_shape().as_list()}')

  if mode == tf.estimator.ModeKeys.PREDICT:
    pred = deep_dot(origin=features['origin'], kernel=emit, kernel_size=FLAGS.depth_ks)
  else:
    pred = deep_dot(origin=features['left'], kernel=emit, kernel_size=FLAGS.depth_ks)
  logging.info(f'the shape of pred is {pred.get_shape().as_list()}')

  if mode == tf.estimator.ModeKeys.TRAIN:
    loss = tf.reduce_mean(MAE(pred, labels))
    opt = tf.compat.v1.train.MomentumOptimizer(learning_rate=0.001, momentum=0.9)
    train_op = opt.minimize(loss=loss, global_step=tf.compat.v1.train.get_or_create_global_step())
    return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op, predictions=pred)
  elif mode == tf.estimator.ModeKeys.EVAL:
    loss = tf.reduce_mean(MAE(pred, labels))
    return tf.estimator.EstimatorSpec(mode=mode, loss=loss, predictions=pred)
  else:
    return tf.estimator.EstimatorSpec(mode=mode, predictions=pred)


def main(_):
  tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.INFO)
  if FLAGS.profiler:
    tf.profiler.experimental.server.start(6009)
  config = tf.estimator.RunConfig(save_checkpoints_steps=100, save_summary_steps=20)
  estimator = tf.estimator.Estimator(model_fn=model_fn, model_dir=FLAGS.model_dir, config=config)
  estimator.train(input_fn=input_fn)


if __name__ == '__main__':
  # tf.compat.v1.disable_eager_execution()
  app.run(main)
