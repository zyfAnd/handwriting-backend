#!/bin/bash
#
# API 测试脚本
# 测试所有 Worker API 端点
#

set -e

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 配置
API_URL="${1:-https://your-worker.workers.dev}"

echo "========================================================================="
echo "🧪 API 测试"
echo "========================================================================="
echo "API URL: $API_URL"
echo ""

# ============================================================================
# 测试 1: 健康检查
# ============================================================================

echo "测试 1: 健康检查"
echo "----------------------------------------"

RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/api/health")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ 通过${NC} (HTTP $HTTP_CODE)"
    echo "$BODY" | jq .
else
    echo -e "${RED}✗ 失败${NC} (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

echo ""

# ============================================================================
# 测试 2: 统计信息
# ============================================================================

echo "测试 2: 统计信息"
echo "----------------------------------------"

RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/api/stats")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ 通过${NC} (HTTP $HTTP_CODE)"
    echo "$BODY" | jq .
    
    # 提取字符数量
    CHAR_COUNT=$(echo "$BODY" | jq -r '.total_characters')
    echo "📊 数据库包含 $CHAR_COUNT 个汉字"
else
    echo -e "${RED}✗ 失败${NC} (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

echo ""

# ============================================================================
# 测试 3: 单字搜索
# ============================================================================

echo "测试 3: 单字搜索"
echo "----------------------------------------"

TEST_CHAR="水"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/api/search?q=$TEST_CHAR")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    SUCCESS=$(echo "$BODY" | jq -r '.success')
    if [ "$SUCCESS" = "true" ]; then
        echo -e "${GREEN}✓ 通过${NC} (HTTP $HTTP_CODE)"
        echo "$BODY" | jq .
        
        # 检查结果
        RESULTS=$(echo "$BODY" | jq -r '.results | length')
        echo "找到 $RESULTS 个结果"
        
        # 显示图片 URL
        IMAGE_URL=$(echo "$BODY" | jq -r '.results[0].url')
        echo "图片 URL: $IMAGE_URL"
    else
        echo -e "${YELLOW}⚠ 警告${NC}: API 返回 success=false"
        echo "$BODY" | jq .
    fi
else
    echo -e "${RED}✗ 失败${NC} (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

echo ""

# ============================================================================
# 测试 4: 多字搜索
# ============================================================================

echo "测试 4: 多字搜索"
echo "----------------------------------------"

TEST_CHARS="水火山"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/api/search?q=$TEST_CHARS")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ 通过${NC} (HTTP $HTTP_CODE)"
    echo "$BODY" | jq .
    
    RESULTS=$(echo "$BODY" | jq -r '.results | length')
    echo "找到 $RESULTS 个结果"
else
    echo -e "${RED}✗ 失败${NC} (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

echo ""

# ============================================================================
# 测试 5: 空查询
# ============================================================================

echo "测试 5: 空查询（应该失败）"
echo "----------------------------------------"

RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/api/search?q=")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "400" ]; then
    echo -e "${GREEN}✓ 通过${NC} (正确返回 400)"
    echo "$BODY" | jq .
else
    echo -e "${YELLOW}⚠ 警告${NC}: 应该返回 400，实际返回 $HTTP_CODE"
    echo "$BODY"
fi

echo ""

# ============================================================================
# 测试 6: 不存在的字符
# ============================================================================

echo "测试 6: 不存在的字符"
echo "----------------------------------------"

TEST_CHAR="𠀀"  # 罕见字符
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/api/search?q=$TEST_CHAR")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ 通过${NC} (HTTP $HTTP_CODE)"
    
    AVAILABLE=$(echo "$BODY" | jq -r '.results[0].available')
    if [ "$AVAILABLE" = "false" ]; then
        echo "正确返回 available=false"
    fi
    
    echo "$BODY" | jq .
else
    echo -e "${RED}✗ 失败${NC} (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

echo ""

# ============================================================================
# 测试 7: CORS 检查
# ============================================================================

echo "测试 7: CORS 配置"
echo "----------------------------------------"

RESPONSE=$(curl -s -I -X OPTIONS "$API_URL/api/search")
CORS_HEADER=$(echo "$RESPONSE" | grep -i "access-control-allow-origin" || echo "")

if [ -n "$CORS_HEADER" ]; then
    echo -e "${GREEN}✓ 通过${NC}"
    echo "$CORS_HEADER"
else
    echo -e "${YELLOW}⚠ 警告${NC}: 未找到 CORS 头"
fi

echo ""

# ============================================================================
# 测试 8: 速率限制
# ============================================================================

echo "测试 8: 速率限制（发送110个请求）"
echo "----------------------------------------"

echo "发送请求..."
COUNT=0
RATE_LIMITED=false

for i in {1..110}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/health")
    
    if [ "$HTTP_CODE" = "429" ]; then
        RATE_LIMITED=true
        COUNT=$i
        break
    fi
    
    if [ $((i % 10)) -eq 0 ]; then
        echo "已发送 $i 个请求..."
    fi
done

if [ "$RATE_LIMITED" = true ]; then
    echo -e "${GREEN}✓ 通过${NC}"
    echo "在第 $COUNT 个请求时触发速率限制"
else
    echo -e "${YELLOW}⚠ 警告${NC}"
    echo "未触发速率限制（可能未配置或限制较高）"
fi

echo ""

# ============================================================================
# 测试 9: 性能测试
# ============================================================================

echo "测试 9: 性能测试（10次请求）"
echo "----------------------------------------"

TOTAL_TIME=0

for i in {1..10}; do
    START=$(date +%s%N)
    curl -s "$API_URL/api/search?q=水" > /dev/null
    END=$(date +%s%N)
    
    TIME=$((($END - $START) / 1000000))  # 转换为毫秒
    TOTAL_TIME=$(($TOTAL_TIME + $TIME))
    
    echo "请求 $i: ${TIME}ms"
done

AVG_TIME=$(($TOTAL_TIME / 10))
echo ""
echo "平均响应时间: ${AVG_TIME}ms"

if [ $AVG_TIME -lt 100 ]; then
    echo -e "${GREEN}✓ 优秀${NC} (<100ms)"
elif [ $AVG_TIME -lt 500 ]; then
    echo -e "${YELLOW}⚠ 良好${NC} (<500ms)"
else
    echo -e "${RED}✗ 较慢${NC} (>500ms)"
fi

echo ""

# ============================================================================
# 总结
# ============================================================================

echo "========================================================================="
echo "📊 测试完成"
echo "========================================================================="
echo ""
echo "💡 建议："
echo "   - 如果有测试失败，检查 Worker 日志: wrangler tail"
echo "   - 验证 KV 数据已正确上传"
echo "   - 确保 R2 公开访问已启用"
echo ""
echo "🔗 相关命令："
echo "   wrangler tail                    # 查看实时日志"
echo "   wrangler kv:key list             # 查看 KV 数据"
echo "   wrangler deployments list        # 查看部署历史"
echo ""
