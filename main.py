#!/usr/bin/env python3
"""
油井报表管理系统 - Android WebView Bootstrap 启动器

webview bootstrap 已自动创建 WebView 和 WebViewLoader。
WebViewLoader 会检测 localhost:5000 并自动加载 URL。
我们只需启动 Flask 服务器在端口 5000 即可。
"""
import os
import sys
import threading
import time

# 错误日志
app_dir = os.environ.get('ANDROID_PRIVATE', os.path.expanduser('~'))
log_file = os.path.join(app_dir, 'app_error.log')

def log(msg):
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} {msg}\n')
    except Exception:
        pass

log('=== APP START ===')
log(f'platform={sys.platform}')
for k, v in sorted(os.environ.items()):
    if k.startswith('ANDROID'):
        log(f'env: {k}={v}')

try:
    from backend import run_app
    log('backend imported')
    
    # webview bootstrap 的 WebViewLoader 期望端口 5000
    port = 5000
    port_actual, flask_run = run_app(host='127.0.0.1', port=port)
    log(f'Flask port={port_actual}')
    
    flask_thread = threading.Thread(target=flask_run, daemon=True)
    flask_thread.start()
    log('Flask thread started')
    
    # 等待 Flask 就绪
    time.sleep(2)
    log('Flask should be ready')
    
    # webview bootstrap 的 WebViewLoader 会自动检测 localhost:5000
    # 成功后会在 UI 线程上调用 loadUrl
    # 我们只需保持 Python 进程运行
    log('Waiting for WebViewLoader to load URL...')
    while True:
        time.sleep(1)

except Exception as e:
    log(f'FATAL ERROR: {str(e)}')
    import traceback
    log(traceback.format_exc())
    log('Keeping process alive')
    while True:
        time.sleep(1)
