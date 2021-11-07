load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")
load("//third_party/org_tensorflow:tensorflow.bzl", "tf_cc_library", "tf_custom_op_library", "tf_cc_test")


tf_custom_op_library(
    name = "tf_deep_dot.so",
    srcs = [
        "kernels/deepdot_kernel.cc",
        "ops/deep_dot_ops.cc"
    ],
)

py_library(
    name = "deep_dot",
    srcs = ["deep_dot.py"],
    data = [":tf_deep_dot.so"]
)

py_test(
    name="deep_dot_test",
    srcs = ["deep_dot_test.py"],
    deps = [
        ":deep_dot"
    ]
)

py_library(
    name='data',
    srcs = ['data.py'],
)

py_library(
    name='utils',
    srcs = ['utils.py'],
)

py_binary(
    name='model',
    srcs = ['model.py'],
    deps = [
        ":data",
        ":utils",
        ":deep_dot"
    ]
)

py_binary(
    name='compose',
    srcs = ['compose.py'],
)

