#!/usr/bin/env python3
"""
油井报表管理系统 - Android WebView Bootstrap 启动器

p4a webview bootstrap 入口文件。
打包命令:
    buildozer android debug

p4a webview bootstrap 会自动提供 WebView 环境，
我们只需启动 Flask 服务器并加载本地页面。
"""
import os
import sys
import threading
import time

IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ

# 启动 Flask 后端
from backend import run_app

port, flask_run = run_app(host='127.0.0.1', port=0)
flask_thread = threading.Thread(target=flask_run, daemon=True)
flask_thread.start()

# 等待 Flask 就绪
time.sleep(2)

if IS_ANDROID:
    # Android 平台：使用 jnius 加载 WebView
    from jnius import autoclass
    
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    WebView = autoclass('android.webkit.WebView')
    WebViewClient = autoclass('android.webkit.WebViewClient')
    LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
    View = autoclass('android.view.View')
    
    activity = PythonActivity.mActivity
    
    # 创建 WebView
    webview = WebView(activity)
    webview.setWebViewClient(WebViewClient())
    
    # 配置 WebView
    settings = webview.getSettings()
    settings.setJavaScriptEnabled(True)
    settings.setDomStorageEnabled(True)
    settings.setDatabaseEnabled(True)
    settings.setAllowFileAccess(True)
    settings.setAllowContentAccess(True)
    settings.setMixedContentMode(0)  # MIXED_CONTENT_ALWAYS_ALLOW
    
    # 全屏
    webview.setSystemUiVisibility(
        View.SYSTEM_UI_FLAG_FULLSCREEN |
        View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
        View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
    )
    
    # 添加 WebView 到 Activity
    layout_params = LayoutParams(-1, -1)  # MATCH_PARENT x MATCH_PARENT
    activity.addContentView(webview, layout_params)
    
    # 加载 Flask 页面
    url = f'http://127.0.0.1:{port}'
    webview.loadUrl(url)
else:
    # 桌面测试
    print(f'Flask server running at http://127.0.0.1:{port}')
    print('Press Ctrl+C to stop')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Shutting down...')
