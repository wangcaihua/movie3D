load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")
load("//third_party/org_tensorflow:tensorflow.bzl", "tf_cc_library", "tf_custom_op_library", "tf_cc_test")


tf_custom_op_library(
    name = "deep_dot.so",
    srcs = [
        "kernels/deepdot_kernel.cc",
        "ops/deep_dot_ops.cc"
    ],
)

py_library(
    name='data',
    srcs = ['data.py'],
)

py_library(
    name='utils',
    srcs = ['utils.py'],
)

py_library(
    name='deep_dot',
    srcs = ['deep_dot.py'],
)

py_library(
    name='model',
    srcs = ['model.py'],
    deps = [
        ":data",
        ":utils",
        ":deep_dot"
    ]
)

