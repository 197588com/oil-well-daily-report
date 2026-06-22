#!/usr/bin/env python3
"""
油井报表管理系统 - Windows 单文件启动器
使用 pywebview + Flask + SQLite

安装依赖:
    pip install pywebview flask flask-cors pyinstaller

打包命令:
    pyinstaller --onefile --windowed --add-data "templates;templates" --add-data "static;static" --name 油井报表管理系统 main_windows.py

运行(开发模式):
    python main_windows.py
"""
import sys
import os
import threading
import time

# 确保资源路径兼容 PyInstaller
if hasattr(sys, '_MEIPASS'):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)

def main():
    try:
        import webview
    except ImportError:
        print("错误：缺少 pywebview 库。请运行：pip install pywebview")
        input("按回车键退出...")
        sys.exit(1)
    
    from backend import run_app
    
    # 启动 Flask，获取实际端口
    port, flask_run = run_app(host='127.0.0.1', port=0)
    
    flask_thread = threading.Thread(target=flask_run)
    flask_thread.daemon = True
    flask_thread.start()
    
    # 等待服务器就绪
    time.sleep(1.5)
    
    url = f'http://127.0.0.1:{port}'
    print(f'油井报表管理系统已启动：{url}')
    
    # 创建 webview 窗口
    webview.create_window(
        '油井报表管理系统',
        url,
        width=1400,
        height=900,
        min_size=(900, 600),
        text_select=True
    )
    webview.start(debug=False)

if __name__ == '__main__':
    main()
