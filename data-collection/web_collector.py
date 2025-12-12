#!/usr/bin/env python3
"""
可视化汉字采集 Web 界面
提供实时抓包、进度展示、自动同步到 GitHub/Cloudflare
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import os
import subprocess
import threading
from pathlib import Path
from datetime import datetime
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'handwriting-collector-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局状态
collector_status = {
    'is_running': False,
    'total_chars': 3500,
    'collected_chars': 0,
    'collected_list': [],
    'last_collected': None,
    'start_time': None,
    'mitmproxy_process': None,
    'github_synced': False,
    'cloudflare_synced': False
}

OUTPUT_DIR = Path("./collected_characters")
OUTPUT_DIR.mkdir(exist_ok=True)
MAPPING_FILE = OUTPUT_DIR / "char_url_mapping.json"
COMMON_CHARS_FILE = Path("./common_3500_chars.txt")


class CollectorMonitor:
    """采集器监控类"""

    def __init__(self):
        self.char_mapping = self.load_mapping()
        self.common_chars = self.load_common_chars()
        collector_status['total_chars'] = len(self.common_chars)
        collector_status['collected_chars'] = len(self.char_mapping)
        collector_status['collected_list'] = list(self.char_mapping.keys())

    def load_mapping(self):
        """加载字符映射"""
        if MAPPING_FILE.exists():
            with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except:
                    return {}
        return {}

    def load_common_chars(self):
        """加载常用汉字列表"""
        if COMMON_CHARS_FILE.exists():
            with open(COMMON_CHARS_FILE, 'r', encoding='utf-8') as f:
                chars = f.read().strip()
                return list(set(chars))
        return []

    def save_mapping(self):
        """保存字符映射"""
        with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.char_mapping, f, ensure_ascii=False, indent=2)

    def add_character(self, char, data):
        """添加采集的字符"""
        if char not in self.char_mapping:
            self.char_mapping[char] = data
            self.save_mapping()

            collector_status['collected_chars'] = len(self.char_mapping)
            collector_status['collected_list'] = list(self.char_mapping.keys())
            collector_status['last_collected'] = {
                'char': char,
                'time': datetime.now().isoformat()
            }

            # 通过 WebSocket 发送更新
            socketio.emit('collection_update', {
                'char': char,
                'total': collector_status['collected_chars'],
                'percentage': (collector_status['collected_chars'] / collector_status['total_chars']) * 100
            })

            return True
        return False

    def get_progress(self):
        """获取采集进度"""
        return {
            'total': collector_status['total_chars'],
            'collected': collector_status['collected_chars'],
            'percentage': (collector_status['collected_chars'] / collector_status['total_chars'] * 100) if collector_status['total_chars'] > 0 else 0,
            'missing': collector_status['total_chars'] - collector_status['collected_chars'],
            'collected_list': collector_status['collected_list'][-20:],  # 最近20个
        }


monitor = CollectorMonitor()


@app.route('/')
def index():
    """主页"""
    return render_template('collector.html')


@app.route('/api/status')
def get_status():
    """获取采集状态"""
    return jsonify({
        'status': collector_status,
        'progress': monitor.get_progress()
    })


@app.route('/api/start', methods=['POST'])
def start_collection():
    """启动采集"""
    if collector_status['is_running']:
        return jsonify({'error': 'Already running'}), 400

    try:
        # 启动 mitmproxy
        cmd = [
            'mitmweb',
            '-s', 'enhanced_collector.py',
            '-p', '8080',
            '--web-port', '8081',
            '--no-web-open-browser'
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        collector_status['is_running'] = True
        collector_status['start_time'] = datetime.now().isoformat()
        collector_status['mitmproxy_process'] = process.pid

        return jsonify({
            'success': True,
            'message': 'Collection started',
            'pid': process.pid
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stop', methods=['POST'])
def stop_collection():
    """停止采集"""
    if not collector_status['is_running']:
        return jsonify({'error': 'Not running'}), 400

    try:
        pid = collector_status['mitmproxy_process']
        if pid:
            os.kill(pid, 9)

        collector_status['is_running'] = False
        collector_status['mitmproxy_process'] = None

        return jsonify({
            'success': True,
            'message': 'Collection stopped'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sync/github', methods=['POST'])
def sync_to_github():
    """同步到 GitHub"""
    try:
        # Git 操作
        subprocess.run(['git', 'add', 'collected_characters/'], check=True, cwd='..')
        subprocess.run([
            'git', 'commit', '-m',
            f'Update collected characters: {collector_status["collected_chars"]} chars'
        ], cwd='..')
        subprocess.run(['git', 'push'], check=True, cwd='..')

        collector_status['github_synced'] = True

        return jsonify({
            'success': True,
            'message': f'Synced {collector_status["collected_chars"]} characters to GitHub',
            'collected': collector_status['collected_chars']
        })
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/characters')
def get_characters():
    """获取已采集字符列表"""
    return jsonify({
        'characters': list(monitor.char_mapping.keys()),
        'total': len(monitor.char_mapping),
        'mapping': monitor.char_mapping
    })


@app.route('/api/missing')
def get_missing():
    """获取未采集字符"""
    collected = set(monitor.char_mapping.keys())
    missing = [c for c in monitor.common_chars if c not in collected]

    return jsonify({
        'missing': missing[:100],  # 前100个
        'total': len(missing)
    })


@socketio.on('connect')
def handle_connect():
    """WebSocket 连接"""
    emit('status', {
        'connected': True,
        'status': collector_status,
        'progress': monitor.get_progress()
    })


@socketio.on('request_update')
def handle_update_request():
    """请求更新"""
    emit('status', {
        'status': collector_status,
        'progress': monitor.get_progress()
    })


def monitor_directory():
    """监控目录变化"""
    last_count = len(list(OUTPUT_DIR.glob("*.png")))

    while True:
        time.sleep(2)
        current_count = len(list(OUTPUT_DIR.glob("*.png")))

        if current_count > last_count:
            # 重新加载映射
            monitor.char_mapping = monitor.load_mapping()
            collector_status['collected_chars'] = len(monitor.char_mapping)

            # 通知客户端
            socketio.emit('status_update', {
                'collected': collector_status['collected_chars'],
                'progress': monitor.get_progress()
            })

            last_count = current_count


if __name__ == '__main__':
    import socket

    # 尝试找一个可用的端口
    port = 5001  # 避免与 AirPlay Receiver 冲突

    print("=" * 70)
    print("🚀 汉字采集可视化界面启动")
    print("=" * 70)
    print(f"📊 Web 界面: http://localhost:{port}")
    print(f"🔧 mitmproxy 界面: http://localhost:8081 (启动采集后)")
    print(f"📱 代理设置: localhost:8080")
    print("=" * 70)
    print("\n配置你的 iPhone:")
    print("1. 连接同一 WiFi")
    print("2. 设置代理: 你的电脑IP:8080")
    print("3. 安装证书: http://mitm.it")
    print("4. 打开 CloudBrush App 开始浏览")
    print("\n" + "=" * 70)

    # 启动目录监控线程
    monitor_thread = threading.Thread(target=monitor_directory, daemon=True)
    monitor_thread.start()

    # 启动 Flask 应用
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
