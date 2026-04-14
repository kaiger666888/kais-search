#!/bin/bash
# kais-search 依赖安装
# 以图搜图需要 PicImageSearch

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔧 安装 kais-search 依赖..."

# 创建 venv（仅以图搜图需要）
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "📦 创建 Python venv..."
    python3 -m venv "$SCRIPT_DIR/.venv"
fi

echo "📦 安装 PicImageSearch..."
"$SCRIPT_DIR/.venv/bin/pip" install -q PicImageSearch

echo "✅ 依赖安装完成"
