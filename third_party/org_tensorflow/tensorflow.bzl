load("@rules_cc//cc:defs.bzl", "cc_binary", "cc_library", "cc_test")

def tf_cc_library(name, srcs = [], gpu_srcs = [], deps = [], linkopts = [], copts = [], **kwargs):
    cc_library(
        name = name,
        srcs = srcs,
        deps = deps + ["@org_tensorflow//:tensorflow_framework"],
        linkopts = linkopts,
        copts = copts + [
            "-D_GLIBCXX_USE_CXX11_ABI=0",
            "-Iexternal/org_tensorflow/include",
        ],
        **kwargs
    )

def tf_cc_test(name, srcs = [], deps = [], copts = [], **kwargs):
    cc_test(
        name = name,
        srcs = srcs,
        deps = deps + [
            "@org_tensorflow//:tensorflow_framework",
            "@com_google_googletest//:gtest_main",
            ],
        copts = copts + [
            "-D_GLIBCXX_USE_CXX11_ABI=0",
            "-Iexternal/org_tensorflow/include",
            "-Wdeprecated-declarations",
        ],
        **kwargs
    )

def tf_custom_op_library(name, srcs = [], gpu_srcs = [], deps = [], linkopts = [], copts = [], **kwargs):
    cc_binary(
        name = name,
        srcs = srcs,
        deps = deps + ["@org_tensorflow//:tensorflow_framework"],
        linkshared = True,
        copts = copts + [
            "-D_GLIBCXX_USE_CXX11_ABI=0",
            "-Iexternal/org_tensorflow/include",
        ],
        **kwargs
    )
