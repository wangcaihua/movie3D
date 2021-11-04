import atexit
import os
from typing import List
import numpy as np
import tensorflow as tf


def register_at_exit(func):
  atexit.register(func)
  return func


def read_vgg16(ckpt_path: str):
  # VGG16: http://download.tensorflow.org/models/vgg_16_2016_08_28.tar.gz
  reader = tf.compat.v1.train.NewCheckpointReader(ckpt_path)
  
  params = {}
  for block_id in range(1, 4):
    for layer_id in range(1, 3):
      for var_name in ['weights', 'biases']:
        key = f'vgg_16/conv{block_id}/conv{block_id}_{layer_id}/{var_name}'
        name = f'conv{block_id}_{layer_id}/{var_name}'
        if block_id == 1 and layer_id == 1 and var_name == 'weights':
          params[name] = np.mean(reader.get_tensor(key), axis=2, keepdims=True)
        else:
          params[name] = reader.get_tensor(key)
  
  return params


def bilinear(shape):
  assert shape[0] == shape[1]
  init = np.empty(shape, dtype='float32')
  weight = np.empty(shape=(shape[0], shape[1]), dtype='float32')
  
  s = int(shape[0] / 2)
  c = (2 * s - 1 - s % 2) / (2 * s)
  coeff = 1 / abs(s - c)
  for i in range(shape[0]):
    for j in range(shape[1]):
      weight[i, j] = (1 - coeff * i) * (1 - coeff * j)
  
  for p in range(shape[2]):
    for q in range(shape[2]):
      init[:, :, p, q] = weight[:, :]
  return init
