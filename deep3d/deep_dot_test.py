import logging
import numpy as np
import tensorflow as tf

from deep3d.deep_dot import deep_dot, deep_dot_lib

logger = tf.get_logger()
logger.setLevel(logging.INFO)


class DeepDotTest(tf.test.TestCase):

    def test_deep_dot(self):
        origin = tf.constant(value=[1, 2, 3, 4, 5,
                                    3, 4, 5, 6, 7,
                                    0, 1, 2, 3, 4,
                                    3, 2, 6, 1, 0,
                                    3, 8, 2, 3, 0],
                             shape=(1, 5, 5, 1), dtype=tf.dtypes.float32)
        kernel = tf.constant(value=[0, 0, 0, 1,  # 1 -> 1
                                    0, 0, 1, 0,  # 2 -> 1
                                    0, 1, 0, 0,  # 3 -> 0
                                    1, 0, 0, 0,  # 4 -> 0
                                    1, 1, 0, 0,  # 5 -> 0
                                    1, 0, 1, 0,  # 3 -> 0
                                    1, 0, 0, 1,  # 4 -> 5
                                    0, 1, 1, 0,  # 5 -> 7
                                    0, 1, 0, 1,  # 6 -> 10
                                    0, 0, 1, 1,  # 7 -> 13
                                    0, 0, 0, 1.5,  # 0 -> 0
                                    0, 0, 1.5, 0,  # 1 -> 0
                                    0, 1.5, 0, 0,  # 2 -> 7.5
                                    1.5, 0, 0, 0,  # 3 -> 7.5
                                    1.5, 1.5, 0, 0,  # 4 -> 19.5
                                    1.5, 0, 1.5, 0,  # 3 -> 0
                                    1.5, 0, 0, 1.5,  # 2 -> 3
                                    0, 1.5, 1.5, 0,  # 6 -> 6
                                    0, 1.5, 0, 1.5,  # 1 -> 6
                                    0, 0, 1.5, 1.5,  # 0 -> 1.5
                                    1, 2, 0, 0,  # 3 -> 6
                                    2, 0, 1, 0,  # 8 -> 9
                                    1, 0, 0, 2,  # 2 -> 6
                                    0, 1, 2, 0,  # 3 -> 5
                                    0, 2, 0, 1,  # 0  -> 0
                                    ],
                             shape=(1, 5, 5, 4), dtype=tf.dtypes.float32)
        composed = deep_dot(origin, kernel, kernel_size=2)
        result = np.reshape(np.array([1., 1., 0., 0., 0.,
                                      0., 5., 7., 10., 13.,
                                      0., 0., 7.5, 7.5, 19.5,
                                      0., 3., 6., 6., 1.5,
                                      6., 9., 6., 5., 0.]), newshape=(1, 5, 5, 1))
        self.assertNDArrayNear(composed.numpy(), result, err=1e-6)

    def test_deep_dot_grad(self):
        grad = tf.constant(value=1,
                           shape=(1, 5, 5, 1), dtype=tf.dtypes.float32)
        origin = tf.constant(value=[1,  # 1, 1, 0, 1 -> 3
                                    2,  # 0, 0, 0, 0 -> 0
                                    3,
                                    4,
                                    5,
                                    3,
                                    4,
                                    5,
                                    6,
                                    7,
                                    0,
                                    1,
                                    2,
                                    3,
                                    4,
                                    3,
                                    2,
                                    6,
                                    1,
                                    0,
                                    3,
                                    8,
                                    2,
                                    3,
                                    0],
                             shape=(1, 5, 5, 1), dtype=tf.dtypes.float32)
        kernel = tf.constant(value=[0, 0, 0, 1,  # 1 -> 1
                                    0, 0, 1, 0,  # 2 -> 1
                                    0, 1, 0, 0,  # 3 -> 0
                                    1, 0, 0, 0,  # 4 -> 0
                                    1, 1, 0, 0,  # 5 -> 0
                                    1, 0, 1, 0,  # 3 -> 0
                                    1, 0, 0, 1,  # 4 -> 5
                                    0, 1, 1, 0,  # 5 -> 7
                                    0, 1, 0, 1,  # 6 -> 10
                                    0, 0, 1, 1,  # 7 -> 13
                                    0, 0, 0, 1.5,  # 0 -> 0
                                    0, 0, 1.5, 0,  # 1 -> 0
                                    0, 1.5, 0, 0,  # 2 -> 7.5
                                    1.5, 0, 0, 0,  # 3 -> 7.5
                                    1.5, 1.5, 0, 0,  # 4 -> 19.5
                                    1.5, 0, 1.5, 0,  # 3 -> 0
                                    1.5, 0, 0, 1.5,  # 2 -> 3
                                    0, 1.5, 1.5, 0,  # 6 -> 6
                                    0, 1.5, 0, 1.5,  # 1 -> 6
                                    0, 0, 1.5, 1.5,  # 0 -> 1.5
                                    1, 2, 0, 0,  # 3 -> 6
                                    2, 0, 1, 0,  # 8 -> 9
                                    1, 0, 0, 2,  # 2 -> 6
                                    0, 1, 2, 0,  # 3 -> 5
                                    0, 2, 0, 1,  # 0  -> 0
                                    ],
                             shape=(1, 5, 5, 4), dtype=tf.dtypes.float32)
        grad_origin, grad_kernel = deep_dot_lib.grad_deep_dot(
            grad_composed=grad, origin=origin, kernel=kernel, kernel_size=2)
        print(grad_origin)


if __name__ == '__main__':
    # tf.compat.v1.disable_eager_execution()
    tf.test.main()
