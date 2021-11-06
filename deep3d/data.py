import cv2
from enum import Enum
import numpy as np
import tensorflow as tf
from typing import Dict
from collections import namedtuple


class VideoType(Enum):
  SIMPLE = 1
  LR3D = 2
  UD3D = 3


Shape = namedtuple("Shape", 'high width')


class FrameGenerator(object):
  def __init__(self,
               video_file_name: str,
               video_type: VideoType = VideoType.LR3D,
               num_epoch: int = 1,
               resize: Shape = Shape(256, 448)):
    self._video_file_name = video_file_name
    self._vc = cv2.VideoCapture(video_file_name)
    self._video_type = video_type
    self._cur_epoch = 1
    self._num_epoch = num_epoch
    self._resize = resize

    self.previous2 = np.zeros(shape=(self.height, self.width), dtype=np.uint8)
    self.previous1 = np.zeros(shape=(self.height, self.width), dtype=np.uint8)

  @property
  def height(self):
    assert self._vc is not None and self._vc.isOpened()
    if self._video_type == VideoType.UD3D:
      return int(self._resize.high / 2)
    else:
      return int(self._resize.high)

  @property
  def width(self):
    assert self._vc is not None and self._vc.isOpened()
    if self._video_type == VideoType.LR3D:
      return int(self._resize.width / 2)
    else:
      return int(self._resize.width)

  @property
  def fps(self):
    assert self._vc is not None and self._vc.isOpened()
    return int(self._vc.get(propId=cv2.CAP_PROP_FPS)) + 1

  @property
  def signature(self) -> Dict[str, tf.TensorSpec]:
    if self._video_type == VideoType.LR3D:
      origin_width = int(self._vc.get(cv2.CAP_PROP_FRAME_WIDTH) / 2)
    else:
      origin_width = int(self._vc.get(cv2.CAP_PROP_FRAME_WIDTH))

    if self._video_type == VideoType.UD3D:
      origin_height = int(self._vc.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2)
    else:
      origin_height = int(self._vc.get(cv2.CAP_PROP_FRAME_HEIGHT))

    return {
      'origin': tf.TensorSpec(shape=(origin_height, origin_width, 3), dtype=tf.dtypes.uint8),
      'left': tf.TensorSpec(shape=(self.height, self.width, 1), dtype=tf.dtypes.uint8),
      'right': tf.TensorSpec(shape=(self.height, self.width, 1), dtype=tf.dtypes.uint8),
      'feature': tf.TensorSpec(shape=(self.height, self.width, 3), dtype=tf.dtypes.uint8),
    }

  def __enter__(self) -> 'FrameGenerator':
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self._vc.release()

  def __iter__(self):
    return self

  def __next__(self) -> Dict[str, np.ndarray]:
    if not self._vc.isOpened():
      raise StopIteration

    ret, frame = self._vc.read()
    if not ret:
      if self._cur_epoch < self._num_epoch:
        self._vc.release()
        self._vc = cv2.VideoCapture(self._video_file_name)
        ret, frame = self._vc.read()
        assert ret
        self._cur_epoch += 1
      else:
        raise StopIteration

    result = {}
    if self._video_type == VideoType.SIMPLE:
      result['origin'] = frame
    elif self._video_type == VideoType.LR3D:
      split = int(self._vc.get(cv2.CAP_PROP_FRAME_WIDTH) / 2)
      result['origin'] = frame[:, :split, :]
    else:
      split = int(self._vc.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2)
      result['origin'] = frame[:split, :, :]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, dsize=(self._resize.width, self._resize.high))
    inner_high, inner_width = gray.shape

    if self._video_type == VideoType.LR3D:
      split = int(inner_width / 2)
      left, right = gray[:, :split], gray[:, split:inner_width]
    elif self._video_type == VideoType.UD3D:
      split = int(inner_high / 2)
      left, right = gray[:split, :], gray[split:inner_high, :]
    else:
      left, right = gray, gray.copy()
    feature = np.stack([left, self.previous1, self.previous2], axis=2)
    self.previous1, self.previous2 = left.copy(), self.previous1
    left, right = np.expand_dims(left, axis=2), np.expand_dims(right, axis=2)

    result.update({
      'left': left,
      'right': right,
      'feature': feature
    })
    return result

  def __call__(self):
    # for tf.data.Dataset.from_generator
    return self
