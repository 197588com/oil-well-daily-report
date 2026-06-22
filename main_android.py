#!/usr/bin/env python3
"""
油井报表管理系统 - Android 启动器 (Kivy + Flask + WebView)
使用 Buildozer 打包为 APK

打包步骤:
1. 安装依赖: pip install buildozer cython
2. 配置 Android SDK/NDK (buildozer 会自动下载)
3. 连接 Android 设备或启动模拟器
4. 运行: buildozer android debug deploy run

配置 buildozer.spec 后执行上述命令。

注意：在 Android 上，Kivy 的 SDL2 视图和 WebView 会共存。
Flask 服务器在后台运行，WebView 访问 localhost 加载前端页面。
"""
import sys
import os
import threading

# Kivy 日志配置
os.environ['KIVY_NO_CONSOLELOG'] = '1'

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.logger import Logger

IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ

from backend import run_app


class OilWellApp(App):
    def build(self):
        # 创建一个透明的 Widget，作为占位
        return Widget(size_hint=(1, 1))
    
    def on_start(self):
        # 启动 Flask 服务器
        port, flask_run = run_app(host='127.0.0.1', port=0)
        self.flask_port = port
        
        self.flask_thread = threading.Thread(target=flask_run, daemon=True)
        self.flask_thread.start()
        
        Logger.info(f'Flask server started on port {port}')
        
        if IS_ANDROID:
            Clock.schedule_once(self._create_android_webview, 2)
        else:
            Clock.schedule_once(self._create_desktop_webview, 1)
    
    def _create_desktop_webview(self, dt):
        """桌面测试：使用 pywebview 或浏览器打开"""
        try:
            import webview
            webview.create_window(
                '油井报表管理系统',
                f'http://127.0.0.1:{self.flask_port}',
                width=1400, height=900
            )
            webview.start()
        except ImportError:
            Logger.info(f'请访问: http://127.0.0.1:{self.flask_port}')
    
    def _create_android_webview(self, dt):
        """Android：使用 jnius 创建原生 WebView 覆盖全屏"""
        try:
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            WebView = autoclass('android.webkit.WebView')
            WebViewClient = autoclass('android.webkit.WebViewClient')
            ViewGroup = autoclass('android.view.ViewGroup')
            LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
            View = autoclass('android.view.View')
            R = autoclass('android.R')
            
            activity = PythonActivity.mActivity
            
            # 创建 WebView
            webview = WebView(activity)
            webview.setWebViewClient(WebViewClient())
            
            # 配置设置
            settings = webview.getSettings()
            settings.setJavaScriptEnabled(True)
            settings.setDomStorageEnabled(True)
            settings.setDatabaseEnabled(True)
            settings.setAllowFileAccess(True)
            settings.setAllowContentAccess(True)
            settings.setMixedContentMode(0)  # MIXED_CONTENT_ALWAYS_ALLOW
            
            # 设置全屏
            webview.setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_FULLSCREEN |
                View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            )
            
            # 添加到布局（覆盖 Kivy 视图）
            layout_params = LayoutParams(-1, -1)  # MATCH_PARENT x MATCH_PARENT
            activity.addContentView(webview, layout_params)
            
            # 加载 Flask 页面
            url = f'http://127.0.0.1:{self.flask_port}'
            Logger.info(f'Loading WebView URL: {url}')
            webview.loadUrl(url)
            
            self.webview = webview
            
        except Exception as e:
            Logger.error(f'WebView creation failed: {e}')
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    OilWellApp().run()
