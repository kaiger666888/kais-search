#!/bin/bash
# kais-search 依赖安装
# 以图搜图需要 playwright Python 包

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔧 安装 kais-search 依赖..."

# 安装 playwright Python 包
pip3 install -q playwright 2>/dev/null

# 确保 playwright 浏览器已安装
npx playwright install chromium 2>/dev/null

echo "✅ 依赖安装完成"
