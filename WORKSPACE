workspace(name = "deep3d")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")

http_archive(
    name = "bazel_skylib",
    sha256 = "2ef429f5d7ce7111263289644d233707dba35e39696377ebab8b0bc701f7818e",
    type = "tar.gz",
    url = "https://github.com/bazelbuild/bazel-skylib/releases/download/{version}/bazel-skylib.{version}.tar.gz".format(
        version = "0.8.0",
    ),
)

http_archive(
    name = "rules_python",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.5.0/rules_python-0.5.0.tar.gz",
    sha256 = "cd6730ed53a002c56ce4e2f396ba3b3be262fd7cb68339f0377a45e8227fe332",
)

# load("@rules_python//python:pip.bzl", "pip_install")
# Create a central external repo, @my_deps, that contains Bazel targets for all the
# third-party packages specified in the requirements.txt file.
# pip_install(
#    name = "py_deps",
#    requirements = "third_party/py_deps/requirements.txt",
# )

# python -c "import tensorflow as tf; print(tf.sysconfig.get_include())"
# python -c "import tensorflow as tf; print(tf.sysconfig.get_lib())"
new_local_repository(
    name = "org_tensorflow",
    build_file = "third_party/org_tensorflow/BUILD",
    path = "/Volumes/opt/opt/anaconda3/envs/vrenv/lib/python3.8/site-packages/tensorflow",
)

# Google Log
git_repository(
    name = "com_github_glog_glog",
    commit = "3106945d8d3322e5cbd5658d482c9ffed2d892c0",
    remote = "https://github.com/google/glog.git",
)

# Google Flags
http_archive(
    name = "com_github_gflags_gflags",
    sha256 = "6e16c8bc91b1310a44f3965e616383dbda48f83e8c1eaa2370a215057b00cabe",
    strip_prefix = "gflags-77592648e3f3be87d6c7123eb81cbad75f9aef5a",
    urls = [
        "https://mirror.bazel.build/github.com/gflags/gflags/archive/77592648e3f3be87d6c7123eb81cbad75f9aef5a.tar.gz",
        "https://github.com/gflags/gflags/archive/77592648e3f3be87d6c7123eb81cbad75f9aef5a.tar.gz",
    ],
)

# Google Test
http_archive(
    name = "com_google_googletest",
    sha256 = "94c634d499558a76fa649edb13721dce6e98fb1e7018dfaeba3cd7a083945e91",  # 对下载的内容进行校验
    strip_prefix = "googletest-release-1.10.0",  # 解压后的文件夹名称，用来指定抽取的文件目录
    urls = ["https://github.com/google/googletest/archive/release-1.10.0.zip"],
)

