#!/bin/bash
#
# CloudBrush 汉字图片搜索系统 - 一键部署脚本
# 自动化部署 Worker、上传数据到R2、配置KV
#

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 辅助函数
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装，请先安装"
        exit 1
    fi
}

# ============================================================================
# 步骤 0: 检查依赖
# ============================================================================

log_info "检查依赖..."

check_command "wrangler"
check_command "python3"
check_command "jq"

log_success "所有依赖已安装"

# ============================================================================
# 步骤 1: Cloudflare 登录
# ============================================================================

log_info "检查 Cloudflare 登录状态..."

if ! wrangler whoami &> /dev/null; then
    log_warning "未登录 Cloudflare，开始登录..."
    wrangler login
else
    log_success "已登录 Cloudflare"
    wrangler whoami
fi

# ============================================================================
# 步骤 2: 创建 R2 Bucket
# ============================================================================

BUCKET_NAME="chinese-characters"

log_info "创建 R2 Bucket: $BUCKET_NAME"

# 检查 Bucket 是否已存在
if wrangler r2 bucket list | grep -q "$BUCKET_NAME"; then
    log_warning "Bucket $BUCKET_NAME 已存在，跳过创建"
else
    wrangler r2 bucket create $BUCKET_NAME
    log_success "Bucket 创建成功"
fi

# ============================================================================
# 步骤 3: 上传图片到 R2
# ============================================================================

log_info "上传图片到 R2..."

if [ ! -d "collected_characters" ]; then
    log_error "未找到 collected_characters 目录"
    log_info "请先运行抓包脚本采集图片"
    exit 1
fi

# 统计文件数量
FILE_COUNT=$(find collected_characters -name "*.png" | wc -l)
log_info "找到 $FILE_COUNT 个图片文件"

if [ $FILE_COUNT -eq 0 ]; then
    log_error "没有图片文件需要上传"
    exit 1
fi

# 使用 Python 脚本上传
log_info "开始批量上传..."
python3 upload_to_cloud.py --provider r2 --bucket $BUCKET_NAME --dir collected_characters

log_success "图片上传完成"

# ============================================================================
# 步骤 4: 配置 R2 公开访问
# ============================================================================

log_info "配置 R2 公开访问..."

# 注意: R2 公开域名需要在 Dashboard 中手动启用
log_warning "请在 Cloudflare Dashboard 中启用 R2 公开域名："
log_warning "1. 访问: https://dash.cloudflare.com → R2"
log_warning "2. 选择 bucket: $BUCKET_NAME"
log_warning "3. Settings → Public Access → 启用 r2.dev subdomain"

read -p "完成后按 Enter 继续..."

# ============================================================================
# 步骤 5: 创建 KV Namespace
# ============================================================================

log_info "创建 KV Namespace..."

KV_OUTPUT=$(wrangler kv:namespace create "CHAR_MAPPING" 2>&1)
echo "$KV_OUTPUT"

# 提取 KV ID
KV_ID=$(echo "$KV_OUTPUT" | grep -oP 'id = "\K[^"]+' || echo "")

if [ -z "$KV_ID" ]; then
    log_warning "无法自动提取 KV ID，请手动配置"
    log_info "从上面的输出中复制 id，然后编辑 wrangler.toml"
    read -p "输入 KV Namespace ID: " KV_ID
fi

log_success "KV Namespace ID: $KV_ID"

# 更新 wrangler.toml
log_info "更新 wrangler.toml..."
sed -i.bak "s/YOUR_KV_NAMESPACE_ID/$KV_ID/g" wrangler.toml
log_success "wrangler.toml 已更新"

# ============================================================================
# 步骤 6: 上传字符映射到 KV
# ============================================================================

log_info "上传字符映射到 KV..."

if [ ! -f "cdn_url_mapping.json" ]; then
    log_error "未找到 cdn_url_mapping.json"
    log_info "请确保已运行上传脚本生成此文件"
    exit 1
fi

wrangler kv:key put \
    --binding=CHAR_MAPPING \
    "char_mapping" \
    --path=cdn_url_mapping.json

log_success "字符映射已上传到 KV"

# ============================================================================
# 步骤 7: 部署 Worker
# ============================================================================

log_info "部署 Cloudflare Worker..."

# 创建 src 目录
mkdir -p src
cp worker-api.js src/index.js

# 部署
wrangler deploy

WORKER_URL=$(wrangler deployments list --json | jq -r '.[0].url' || echo "")

if [ -n "$WORKER_URL" ]; then
    log_success "Worker 部署成功！"
    log_info "API URL: $WORKER_URL"
else
    log_warning "无法自动获取 Worker URL"
    log_info "请运行: wrangler deployments list"
fi

# ============================================================================
# 步骤 8: 测试 API
# ============================================================================

log_info "测试 API..."

if [ -n "$WORKER_URL" ]; then
    # 测试健康检查
    log_info "测试健康检查..."
    curl -s "${WORKER_URL}/api/health" | jq .
    
    # 测试搜索
    log_info "测试搜索功能..."
    curl -s "${WORKER_URL}/api/search?q=水" | jq .
    
    log_success "API 测试通过"
fi

# ============================================================================
# 步骤 9: 部署前端
# ============================================================================

log_info "部署前端到 Cloudflare Pages..."

# 更新前端中的 API URL
if [ -n "$WORKER_URL" ]; then
    sed -i.bak "s|https://your-worker.workers.dev|$WORKER_URL|g" frontend-search.html
    log_success "前端 API URL 已更新"
fi

# 创建 Pages 项目目录
mkdir -p pages-deploy
cp frontend-search.html pages-deploy/index.html

log_info "部署到 Cloudflare Pages..."
wrangler pages deploy pages-deploy --project-name=chinese-char-search

PAGES_URL=$(wrangler pages deployments list --project-name=chinese-char-search --json | jq -r '.[0].url' || echo "")

if [ -n "$PAGES_URL" ]; then
    log_success "前端部署成功！"
    log_info "访问: $PAGES_URL"
fi

# ============================================================================
# 完成
# ============================================================================

echo ""
echo "========================================================================="
echo -e "${GREEN}🎉 部署完成！${NC}"
echo "========================================================================="
echo ""
echo "📊 部署信息："
echo "   - R2 Bucket: $BUCKET_NAME"
echo "   - 图片数量: $FILE_COUNT"
echo "   - KV Namespace: $KV_ID"
echo "   - Worker URL: ${WORKER_URL:-请运行 wrangler deployments list 查看}"
echo "   - Frontend URL: ${PAGES_URL:-请运行 wrangler pages deployments list 查看}"
echo ""
echo "🔗 下一步："
echo "   1. 访问前端页面测试搜索功能"
echo "   2. 配置自定义域名（可选）"
echo "   3. 查看监控和日志: wrangler tail"
echo ""
echo "📖 文档："
echo "   - API 文档: ${WORKER_URL}/"
echo "   - 完整指南: COMPLETE_IMPLEMENTATION_GUIDE.md"
echo ""
echo "========================================================================="

# 保存部署信息
cat > deployment-info.json << EOF
{
  "deployed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "bucket": "$BUCKET_NAME",
  "image_count": $FILE_COUNT,
  "kv_namespace_id": "$KV_ID",
  "worker_url": "$WORKER_URL",
  "pages_url": "$PAGES_URL"
}
EOF

log_success "部署信息已保存到 deployment-info.json"
