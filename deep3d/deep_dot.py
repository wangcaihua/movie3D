import os
import tensorflow as tf
from tensorflow.python.framework import ops
from tensorflow.python.framework import load_library

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
deep_dot_lib = load_library.load_op_library('deep3d/tf_deep_dot.so')


def deep_dot(origin: tf.Tensor, kernel: tf.Tensor, kernel_size: int) -> tf.Tensor:
    return deep_dot_lib.deep_dot(origin=origin, kernel=kernel, kernel_size=kernel_size)


@ops.RegisterGradient('DeepDot')
def _deep_dot_grad(op, grad):
    origin, kernel = op.inputs[0], op.inputs[1]
    kernel_size = op.get_attr('kernel_size')

    [grad_origin, grad_kernel] = deep_dot_lib.grad_deep_dot(
        grad_composed=grad, origin=origin, kernel=kernel, kernel_size=kernel_size)
    return [grad_origin, grad_kernel]


@tf.custom_gradient
def deep_fuse(origin: tf.Tensor, kernel: tf.Tensor, kernel_size: int):
    composed = deep_dot_lib.deep_dot(origin=origin, kernel=kernel, kernel_size=kernel_size)

    def grad(dy):
        [grad_origin, grad_kernel] = deep_dot_lib.grad_deep_dot(
            grad_composed=dy, origin=origin, kernel=kernel, kernel_size=kernel_size)
        return [grad_origin, grad_kernel]

    return composed, grad
