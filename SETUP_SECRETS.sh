#!/bin/bash
#
# 配置 GitHub Secrets 脚本
# 这个脚本帮助你快速设置 Cloudflare 凭证到 GitHub Secrets

set -e

echo "======================================================================="
echo "🔐 GitHub Secrets 配置助手"
echo "======================================================================="
echo ""

# 检查 gh 是否安装
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) 未安装"
    echo "安装方法: brew install gh"
    exit 1
fi

# 检查是否登录
if ! gh auth status &> /dev/null; then
    echo "❌ 未登录 GitHub CLI"
    echo "请运行: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI 已准备就绪"
echo ""

# 获取 Cloudflare Account ID
echo "步骤 1: 获取 Cloudflare Account ID"
echo "---------------------------------------"
echo "运行以下命令获取 Account ID:"
echo "  wrangler whoami"
echo ""
echo "或访问: https://dash.cloudflare.com/"
echo ""
read -p "请输入你的 Cloudflare Account ID: " ACCOUNT_ID

if [ -z "$ACCOUNT_ID" ]; then
    echo "❌ Account ID 不能为空"
    exit 1
fi

echo ""
echo "步骤 2: 获取 Cloudflare API Token"
echo "---------------------------------------"
echo "访问: https://dash.cloudflare.com/profile/api-tokens"
echo "点击 'Create Token' -> 选择 'Edit Cloudflare Workers' 模板"
echo ""
read -sp "请粘贴你的 Cloudflare API Token: " API_TOKEN
echo ""

if [ -z "$API_TOKEN" ]; then
    echo "❌ API Token 不能为空"
    exit 1
fi

echo ""
echo "步骤 3: 配置 GitHub Secrets"
echo "---------------------------------------"

# 设置 GitHub Secrets
echo "正在设置 CLOUDFLARE_ACCOUNT_ID..."
echo "$ACCOUNT_ID" | gh secret set CLOUDFLARE_ACCOUNT_ID

echo "正在设置 CLOUDFLARE_API_TOKEN..."
echo "$API_TOKEN" | gh secret set CLOUDFLARE_API_TOKEN

echo ""
echo "======================================================================="
echo "✅ GitHub Secrets 配置完成！"
echo "======================================================================="
echo ""
echo "已配置的 Secrets:"
gh secret list
echo ""
echo "下一步:"
echo "1. 创建 R2 Bucket: wrangler r2 bucket create handwriting-characters"
echo "2. 创建 KV Namespace: wrangler kv:namespace create \"CHAR_MAPPING\""
echo "3. 更新 wrangler.toml 中的 KV ID"
echo "4. 推送代码触发自动部署: git push"
echo ""
