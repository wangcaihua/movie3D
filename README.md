
## install
### 1.1 install bazel
```bash
export BAZEL_VERSION=3.7.2
curl -fLO "https://github.com/bazelbuild/bazel/releases/download/${BAZEL_VERSION}/bazel-${BAZEL_VERSION}-installer-darwin-x86_64.sh"
chmod +x "bazel-${BAZEL_VERSION}-installer-darwin-x86_64.sh"
./bazel-${BAZEL_VERSION}-installer-darwin-x86_64.sh --user
export PATH="$PATH:$HOME/bin"
```

### 1.2 install py pkgs
```bash
pip freeze > requirements.txt
pip install -r requirements.txt
```
