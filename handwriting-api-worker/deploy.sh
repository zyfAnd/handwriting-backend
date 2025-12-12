#!/bin/bash
#
# 一键部署脚本 - Handwriting API Worker
#
# 使用方法:
#   ./deploy.sh              # 完整部署（创建资源 + 上传数据 + 部署）
#   ./deploy.sh --skip-setup # 跳过资源创建
#   ./deploy.sh --data-only  # 仅上传数据
#   ./deploy.sh --deploy-only # 仅部署 Worker

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_section() {
    echo ""
    echo -e "${BLUE}=====================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=====================================================================${NC}"
    echo ""
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 未安装，请先安装"
        exit 1
    fi
}

# 解析命令行参数
SKIP_SETUP=false
DATA_ONLY=false
DEPLOY_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-setup)
            SKIP_SETUP=true
            shift
            ;;
        --data-only)
            DATA_ONLY=true
            shift
            ;;
        --deploy-only)
            DEPLOY_ONLY=true
            shift
            ;;
        *)
            print_error "未知参数: $1"
            echo "使用方法:"
            echo "  ./deploy.sh              # 完整部署"
            echo "  ./deploy.sh --skip-setup # 跳过资源创建"
            echo "  ./deploy.sh --data-only  # 仅上传数据"
            echo "  ./deploy.sh --deploy-only # 仅部署 Worker"
            exit 1
            ;;
    esac
done

# 打印欢迎信息
print_section "🚀 Handwriting API Worker - 部署脚本"

# 检查依赖
print_info "检查依赖..."
check_command "node"
check_command "npm"
check_command "wrangler"
check_command "python3"
print_success "所有依赖已安装"

# 检查 wrangler 登录状态
print_info "检查 Wrangler 登录状态..."
if wrangler whoami &> /dev/null; then
    print_success "已登录到 Cloudflare"
else
    print_warning "未登录到 Cloudflare，开始登录..."
    wrangler login
fi

# 步骤 1: 创建 Cloudflare 资源
if [ "$SKIP_SETUP" = false ] && [ "$DATA_ONLY" = false ] && [ "$DEPLOY_ONLY" = false ]; then
    print_section "📦 步骤 1: 创建 Cloudflare 资源"

    # 创建 R2 Bucket
    print_info "创建 R2 Bucket: handwriting-characters"
    if wrangler r2 bucket list | grep -q "handwriting-characters"; then
        print_warning "R2 Bucket 已存在，跳过创建"
    else
        wrangler r2 bucket create handwriting-characters
        print_success "R2 Bucket 创建成功"
    fi

    # 创建 KV Namespace
    print_info "创建 KV Namespace: CHAR_MAPPING"
    print_warning "请将输出的 ID 更新到 wrangler.toml 文件"
    wrangler kv:namespace create "CHAR_MAPPING"

    print_info "创建预览 KV Namespace (可选)"
    wrangler kv:namespace create "CHAR_MAPPING" --preview

    print_warning ""
    print_warning "===================================================================="
    print_warning "重要: 请更新 wrangler.toml 中的 KV Namespace ID"
    print_warning "===================================================================="
    print_warning ""

    read -p "是否已更新 wrangler.toml? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "请先更新 wrangler.toml，然后重新运行脚本"
        exit 1
    fi
fi

# 步骤 2: 上传数据
if [ "$DEPLOY_ONLY" = false ]; then
    print_section "📤 步骤 2: 上传数据到 Cloudflare"

    # 检查数据目录
    DATA_DIR="../data-collection/collected_characters"
    if [ ! -d "$DATA_DIR" ]; then
        print_error "数据目录不存在: $DATA_DIR"
        print_info "请先运行数据采集脚本"
        exit 1
    fi

    # 统计图片数量
    PNG_COUNT=$(find "$DATA_DIR" -name "*.png" -type f | wc -l)
    print_info "找到 $PNG_COUNT 个 PNG 文件"

    if [ $PNG_COUNT -eq 0 ]; then
        print_error "没有找到任何 PNG 文件"
        print_info "请先运行数据采集脚本"
        exit 1
    fi

    # 运行上传脚本
    print_info "开始上传数据..."
    python3 upload-data.py --data-dir "$DATA_DIR"

    print_success "数据上传完成"
fi

# 步骤 3: 安装依赖
if [ "$DATA_ONLY" = false ]; then
    print_section "📦 步骤 3: 安装 npm 依赖"

    if [ ! -d "node_modules" ]; then
        print_info "安装依赖..."
        npm install
        print_success "依赖安装完成"
    else
        print_info "依赖已安装，跳过"
    fi
fi

# 步骤 4: 部署 Worker
if [ "$DATA_ONLY" = false ]; then
    print_section "🚀 步骤 4: 部署 Worker"

    print_info "部署到 Cloudflare Workers..."
    wrangler deploy

    print_success "Worker 部署成功"
fi

# 步骤 5: 验证部署
if [ "$DATA_ONLY" = false ]; then
    print_section "✅ 步骤 5: 验证部署"

    print_info "等待 Worker 启动..."
    sleep 3

    # 获取 Worker URL
    WORKER_URL=$(wrangler deployments list 2>/dev/null | grep "https://" | head -1 | awk '{print $1}')

    if [ -z "$WORKER_URL" ]; then
        print_warning "无法自动获取 Worker URL"
        print_info "请手动测试: wrangler tail"
    else
        print_info "Worker URL: $WORKER_URL"

        # 健康检查
        print_info "测试健康检查..."
        if curl -s "${WORKER_URL}/api/health" | grep -q "healthy"; then
            print_success "健康检查通过"
        else
            print_warning "健康检查失败，请检查日志"
        fi

        # 统计信息
        print_info "测试统计信息..."
        curl -s "${WORKER_URL}/api/stats" | python3 -m json.tool
    fi
fi

# 完成
print_section "🎉 部署完成！"

echo ""
print_success "部署流程已完成！"
echo ""
echo "后续步骤:"
echo "  1. 测试 API: curl \"https://your-worker.workers.dev/api/search?q=水\""
echo "  2. 查看日志: wrangler tail"
echo "  3. 查看统计: 访问 Cloudflare Dashboard"
echo ""
print_info "参考文档: README.md 和 DEPLOYMENT.md"
echo ""
