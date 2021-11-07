import numpy as np
from absl import logging, flags, app
import os
import cv2
from typing import Dict

import tensorflow as tf
from deep3d.utils import read_vgg16, bilinear, save
from tensorflow.keras.layers import Conv2D, MaxPooling2D, BatchNormalization, Conv2DTranspose, ReLU, Softmax
from tensorflow.keras.losses import MAE
from deep3d.data import FrameGenerator, VideoType, OriginType
from deep3d.deep_dot import deep_dot

FLAGS = flags.FLAGS
flags.DEFINE_integer('batch_size', 64, 'batch_size')
flags.DEFINE_integer('num_epoch', 1, 'num epoch')
flags.DEFINE_integer('depth_ks', 4, 'depth_ks')
flags.DEFINE_enum('vt', 'lr3d', ['simple', 'lr3d', 'ud3d'], 'video_type')
flags.DEFINE_enum('ot', 'color', ['gray', 'color'], 'video_type')
flags.DEFINE_bool('drop_remainder', True, 'drop_remainder')
flags.DEFINE_string('file_name', '/Volumes/data/baidu/Avatar_3D.mkv', 'input movie file_name')
# flags.DEFINE_string('file_name', '/Volumes/data/baidu/carrier.mp4', 'input movie file_name')
flags.DEFINE_string('model_dir', '/Users/fitz/data/code/deep3d/ckpt', 'input movie file_name')
flags.DEFINE_bool('profiler', True, 'whether start profiler')

params = read_vgg16('/Users/fitz/data/code/deep3d/vgg_16.ckpt')


class Deep3dModel(object):
  def __init__(self, file_name, depth_ks: int, num_epoch: int = 1, batch_size: int = 64,
               drop_remainder: bool = True, video_type: str = 'lr3d', origin_type='color'):
    self.num_epoch = num_epoch
    self.video_type = VideoType[video_type.upper()]
    self.origin_type = OriginType[origin_type.upper()]
    self.batch_size = batch_size
    self.drop_remainder = drop_remainder
    self._depth_ks = depth_ks

    self.frame_reader = FrameGenerator(file_name,
                                       num_epoch=self.num_epoch,
                                       video_type=self.video_type,
                                       origin_type=self.origin_type)

  @property
  def fps(self):
    return self.frame_reader.fps

  @property
  def origin_size(self):
    return self.frame_reader.origin_size

  @property
  def fourcc(self):
    return self.frame_reader.fourcc

  def input_fn(self) -> tf.data.Dataset:
    dataset = tf.data.Dataset.from_generator(generator=self.frame_reader, output_signature=self.frame_reader.signature)

    def map_fn(features):
      return {key: tf.cast(value, dtype=tf.float32) / 255.0 for key, value in features.items()}

    dataset = dataset.map(map_fn).batch(batch_size=self.batch_size, drop_remainder=self.drop_remainder)
    dataset = dataset.prefetch(buffer_size=tf.data.AUTOTUNE)

    return dataset

  def model_fn(self, features: Dict[str, tf.Tensor],
               labels: tf.Tensor,
               mode: str) -> tf.estimator.EstimatorSpec:
    data, labels = features['feature'], (labels or features.get('right', None))
    logging.info(f'the shape of left is {data.get_shape().as_list()}')
    depth_ks = self._depth_ks
    depth = depth_ks ** 2

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
      pred = {
        'origin': features['origin'],
        'origin_pred': deep_dot(origin=features['origin'], kernel=emit, kernel_size=depth_ks),
        'left': features['left'],
        'left_pred': deep_dot(origin=features['left'], kernel=emit, kernel_size=depth_ks),
        'right': features['right'],
      }
    else:
      pred = deep_dot(origin=features['left'], kernel=emit, kernel_size=depth_ks)
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
  model = Deep3dModel(FLAGS.file_name, FLAGS.depth_ks, FLAGS.num_epoch, FLAGS.batch_size,
                      FLAGS.drop_remainder, FLAGS.vt, FLAGS.ot)
  config = tf.estimator.RunConfig(save_checkpoints_steps=100, save_summary_steps=20)
  estimator = tf.estimator.Estimator(model_fn=model.model_fn,
                                     model_dir=FLAGS.model_dir, config=config)

  # estimator.train(input_fn=model.input_fn)
  if model.origin_type == OriginType.COLOR:
    # size = (2 * model.origin_size[1], model.origin_size[0])  # (width, height)
    ratio = min(model.origin_size[0] / 1080, model.origin_size[1] / 1200)
    if model.origin_size[1] / 1200 > model.origin_size[0] / 1080:
      size = (int(model.origin_size[1] * ratio) * 2, model.origin_size[0])
    else:
      size = (model.origin_size[1] * 2, int(model.origin_size[0] / ratio))
  else:
    size = (model.origin_size[1], model.origin_size[0])  # (width, height)

  with save('/Volumes/data/baidu/carrier2.mp4', model.fourcc, model.fps, size, True) as writer:
    for predictions in estimator.predict(input_fn=model.input_fn):
      if model.origin_type == OriginType.COLOR:
        origin, origin_pred = predictions['origin'], predictions['origin_pred']
        height, width = origin.shape[0], origin.shape[1]
        ratio = min(width / 1200, height / 1080)
        if width / 1200 > height / 1080:
          real_width = int(width * ratio)
          start = int((width - real_width) / 2)
          end = start + real_width
          new_origin = origin[:, start:end, :]
          new_origin_pred = origin[:, start:end, :]
        else:
          real_height = int(height / ratio)
          start = int((real_height - height) / 2)
          end = start + height
          new_origin = np.zeros(shape=(real_height, width, 3))
          new_origin_pred = np.zeros(shape=(real_height, width, 3))

          new_origin[start:end, :, :] = origin[:, :, :]
          new_origin_pred[start:end, :, :] = origin_pred[:, :, :]

        img = np.concatenate([new_origin, new_origin_pred], axis=1)
      else:
        img = np.stack([predictions['origin'],
                        np.zeros_like(predictions['origin']),
                        predictions['origin_pred']], axis=-1)
        img = np.squeeze(img, axis=2)
      img = (img * 255).astype(np.uint8)
      writer.write(img)
      cv2.waitKey(20)


if __name__ == '__main__':
  tf.compat.v1.disable_eager_execution()
  app.run(main)
