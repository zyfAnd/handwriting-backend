# 安装指南

## Python 3.13 兼容性问题

如果你使用 Python 3.13，可能会遇到依赖包编译错误。这是因为某些包（如 mitmproxy）还没有完全支持 Python 3.13。

## 推荐解决方案

### 方案 1: 使用 Python 3.12（推荐）

```bash
# 安装 Python 3.12
brew install python@3.12

# 创建虚拟环境
cd data-collection
python3.12 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 方案 2: 使用 Homebrew 安装 mitmproxy

这样可以避免编译问题：

```bash
# 使用 Homebrew 安装 mitmproxy（跳过 Python 编译）
brew install mitmproxy

# 安装最小依赖（不包含 mitmproxy）
cd data-collection
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-minimal.txt
```

### 方案 3: 使用 pyenv 管理 Python 版本

```bash
# 安装 pyenv
brew install pyenv

# 安装 Python 3.12
pyenv install 3.12.7

# 设置项目使用 3.12
cd /Volumes/thinkplus-1T/my-github/handwriting-backend/data-collection
pyenv local 3.12.7

# 创建虚拟环境
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 快速检查

安装完成后，验证：

```bash
# 检查 mitmproxy
which mitmproxy
mitmproxy --version

# 检查 Flask
python -c "import flask; print(flask.__version__)"

# 检查 SocketIO
python -c "import flask_socketio; print('Flask-SocketIO OK')"
```

## 常见错误

### 错误 1: cffi 编译失败

```
error: call to undeclared function '_PyErr_WriteUnraisableMsg'
```

**解决**: 使用 Python 3.12 或通过 Homebrew 安装 mitmproxy

### 错误 2: zstandard 构建失败

```
ERROR: Failed to build 'zstandard' when installing build dependencies
```

**解决**: 使用 requirements-minimal.txt + Homebrew mitmproxy

### 错误 3: 缺少 C 编译器

**解决**: 安装 Xcode Command Line Tools

```bash
xcode-select --install
```

## 启动服务

安装完成后：

```bash
cd data-collection
./start_collector.sh
```

或手动启动：

```bash
source venv/bin/activate
python web_collector.py
```
