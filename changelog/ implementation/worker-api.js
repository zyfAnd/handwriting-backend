/**
 * Cloudflare Worker - 汉字图片搜索 API
 * 
 * 功能：
 * - 单字/多字搜索
 * - 拼音搜索（可选）
 * - 返回图片URL列表
 * - CORS支持
 * - 速率限制
 */

// ============================================================================
// 主路由处理器
// ============================================================================

export default {
  async fetch(request, env, ctx) {
    // CORS 预检请求
    if (request.method === 'OPTIONS') {
      return handleCORS();
    }

    const url = new URL(request.url);
    const path = url.pathname;

    // 路由分发
    if (path === '/api/search') {
      return handleSearch(request, env);
    } else if (path === '/api/health') {
      return handleHealth();
    } else if (path === '/api/stats') {
      return handleStats(env);
    } else if (path === '/') {
      return handleRoot();
    } else {
      return new Response('Not Found', { status: 404 });
    }
  }
};


// ============================================================================
// 搜索处理器
// ============================================================================

async function handleSearch(request, env) {
  try {
    const url = new URL(request.url);
    const query = url.searchParams.get('q');
    
    if (!query) {
      return jsonResponse({
        success: false,
        error: 'Missing query parameter: q'
      }, 400);
    }

    // 速率限制检查
    const rateLimitResult = await checkRateLimit(request, env);
    if (!rateLimitResult.allowed) {
      return jsonResponse({
        success: false,
        error: 'Rate limit exceeded. Try again later.'
      }, 429);
    }

    // 加载字符映射
    const charMapping = await loadCharMapping(env);
    
    // 处理查询
    const results = await searchCharacters(query, charMapping, env);

    return jsonResponse({
      success: true,
      query: query,
      results: results,
      count: results.length,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Search error:', error);
    return jsonResponse({
      success: false,
      error: 'Internal server error'
    }, 500);
  }
}


// ============================================================================
// 搜索逻辑
// ============================================================================

async function searchCharacters(query, charMapping, env) {
  const results = [];
  const chars = Array.from(query); // 支持Unicode

  for (const char of chars) {
    // 只处理汉字
    if (isChineseChar(char)) {
      const charData = charMapping[char];
      
      if (charData) {
        results.push({
          char: char,
          url: charData.url || constructImageUrl(char, env),
          unicode: charData.unicode || `U+${char.charCodeAt(0).toString(16).toUpperCase()}`,
          filename: charData.filename,
          metadata: {
            size: charData.size,
            timestamp: charData.timestamp
          }
        });
      } else {
        // 字符未采集，返回占位信息
        results.push({
          char: char,
          url: null,
          unicode: `U+${char.charCodeAt(0).toString(16).toUpperCase()}`,
          available: false,
          message: 'Character not yet collected'
        });
      }
    }
  }

  return results;
}


// ============================================================================
// 辅助函数
// ============================================================================

function isChineseChar(char) {
  const code = char.charCodeAt(0);
  return (
    (code >= 0x4e00 && code <= 0x9fff) ||  // CJK统一汉字
    (code >= 0x3400 && code <= 0x4dbf) ||  // CJK扩展A
    (code >= 0x20000 && code <= 0x2a6df)   // CJK扩展B
  );
}

function constructImageUrl(char, env) {
  const unicode = char.charCodeAt(0).toString(16).padStart(4, '0');
  const filename = `${unicode}_${char}.png`;
  
  // 使用R2公开域名
  const domain = env.R2_PUBLIC_DOMAIN || 'chinese-characters.r2.dev';
  return `https://${domain}/chars/${filename}`;
}

async function loadCharMapping(env) {
  // 从KV加载映射数据
  const cached = await env.CHAR_MAPPING.get('char_mapping', { type: 'json' });
  
  if (cached) {
    return cached;
  }

  // 如果KV中没有，返回空对象
  console.warn('Character mapping not found in KV');
  return {};
}


// ============================================================================
// 速率限制
// ============================================================================

async function checkRateLimit(request, env) {
  // 简单的IP限速：每分钟100请求
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  const key = `ratelimit:${ip}`;
  
  try {
    const current = await env.CHAR_MAPPING.get(key);
    const count = current ? parseInt(current) : 0;
    
    if (count >= 100) {
      return { allowed: false };
    }
    
    // 增加计数，60秒过期
    await env.CHAR_MAPPING.put(key, (count + 1).toString(), {
      expirationTtl: 60
    });
    
    return { allowed: true };
  } catch (error) {
    // 速率限制失败时允许请求
    console.error('Rate limit error:', error);
    return { allowed: true };
  }
}


// ============================================================================
// 健康检查
// ============================================================================

async function handleHealth() {
  return jsonResponse({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
}


// ============================================================================
// 统计信息
// ============================================================================

async function handleStats(env) {
  try {
    const charMapping = await loadCharMapping(env);
    const totalChars = Object.keys(charMapping).length;
    
    return jsonResponse({
      total_characters: totalChars,
      api_version: '1.0.0',
      endpoints: [
        '/api/search?q={query}',
        '/api/health',
        '/api/stats'
      ]
    });
  } catch (error) {
    return jsonResponse({
      error: 'Failed to load stats'
    }, 500);
  }
}


// ============================================================================
// 根路径
// ============================================================================

function handleRoot() {
  const html = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>汉字图片搜索 API</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      max-width: 800px;
      margin: 50px auto;
      padding: 20px;
      line-height: 1.6;
    }
    h1 { color: #333; }
    code {
      background: #f4f4f4;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: monospace;
    }
    pre {
      background: #f4f4f4;
      padding: 15px;
      border-radius: 5px;
      overflow-x: auto;
    }
    .endpoint {
      margin: 20px 0;
      padding: 15px;
      border-left: 4px solid #4CAF50;
      background: #f9f9f9;
    }
  </style>
</head>
<body>
  <h1>🔍 汉字图片搜索 API</h1>
  
  <p>欢迎使用汉字图片搜索API！本API提供3000+常用汉字的高清图片。</p>
  
  <h2>📖 API端点</h2>
  
  <div class="endpoint">
    <h3>GET /api/search</h3>
    <p><strong>参数:</strong> <code>q</code> - 要搜索的汉字</p>
    <p><strong>示例:</strong></p>
    <pre>curl "https://your-worker.workers.dev/api/search?q=水火山"</pre>
    <p><strong>响应:</strong></p>
    <pre>{
  "success": true,
  "query": "水火山",
  "results": [
    {
      "char": "水",
      "url": "https://cdn.example.com/chars/6c34_水.png",
      "unicode": "U+6C34"
    },
    ...
  ],
  "count": 3
}</pre>
  </div>
  
  <div class="endpoint">
    <h3>GET /api/health</h3>
    <p>检查API健康状态</p>
  </div>
  
  <div class="endpoint">
    <h3>GET /api/stats</h3>
    <p>获取API统计信息</p>
  </div>
  
  <h2>⚡ 速率限制</h2>
  <p>每个IP每分钟最多100次请求</p>
  
  <h2>🔗 相关链接</h2>
  <ul>
    <li><a href="/api/health">健康检查</a></li>
    <li><a href="/api/stats">统计信息</a></li>
    <li><a href="https://github.com">GitHub 仓库</a></li>
  </ul>
  
  <footer style="margin-top: 50px; color: #666; font-size: 0.9em;">
    <p>Powered by Cloudflare Workers | Made with ❤️</p>
  </footer>
</body>
</html>
  `;
  
  return new Response(html, {
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      ...getCORSHeaders()
    }
  });
}


// ============================================================================
// 响应辅助函数
// ============================================================================

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status: status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      ...getCORSHeaders()
    }
  });
}

function handleCORS() {
  return new Response(null, {
    headers: getCORSHeaders()
  });
}

function getCORSHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400'
  };
}


// ============================================================================
// 部署说明
// ============================================================================

/*
部署步骤:

1. 安装 Wrangler
   npm install -g wrangler

2. 登录 Cloudflare
   wrangler login

3. 创建 KV Namespace
   wrangler kv:namespace create "CHAR_MAPPING"
   
   复制输出的ID到 wrangler.toml:
   [[kv_namespaces]]
   binding = "CHAR_MAPPING"
   id = "your_kv_namespace_id"

4. 上传字符映射数据
   wrangler kv:key put --binding=CHAR_MAPPING "char_mapping" \
     --path=cdn_url_mapping.json

5. 部署 Worker
   wrangler deploy

6. 测试
   curl "https://your-worker.workers.dev/api/search?q=水"

环境变量配置（wrangler.toml）:
[vars]
R2_PUBLIC_DOMAIN = "chinese-characters.r2.dev"

或在 Cloudflare Dashboard 中设置环境变量。
*/
