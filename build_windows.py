#!/usr/bin/env python3
"""
Windows 单文件 exe 构建脚本

使用说明:
1. 安装依赖:
    pip install pywebview flask flask-cors pyinstaller

2. 运行构建:
    python build_windows.py

3. 输出文件:
    dist/油井报表管理系统.exe

4. 运行:
    双击 dist/油井报表管理系统.exe 即可运行
"""
import os
import sys
import subprocess

def main():
    # 检查依赖
    try:
        import pywebview
        import flask
        import PyInstaller
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请运行: pip install pywebview flask flask-cors pyinstaller")
        sys.exit(1)
    
    # 构建命令
    # --onefile: 单文件模式
    # --windowed: 不显示控制台窗口
    # --add-data: 添加模板和静态资源
    # --name: 输出文件名
    # --icon: 图标（可选）
    # --clean: 清理临时文件
    # --noconfirm: 覆盖已有输出
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--add-data', 'templates;templates',
        '--add-data', 'static;static',
        '--name', '油井报表管理系统',
        '--clean',
        '--noconfirm',
        'main_windows.py'
    ]
    
    print("开始构建 Windows 单文件版...")
    print("命令:", ' '.join(cmd))
    
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    if result.returncode == 0:
        print("\n✅ 构建成功！")
        print("输出文件: dist/油井报表管理系统.exe")
        print("\n运行方式:")
        print("  1. 直接双击 dist/油井报表管理系统.exe")
        print("  2. 或在命令行运行: .\\dist\\油井报表管理系统.exe")
        print("\n数据文件:")
        print("  数据库文件 oil_well.db 会在 exe 同级目录自动创建")
    else:
        print(f"\n❌ 构建失败，返回码: {result.returncode}")
        sys.exit(1)

if __name__ == '__main__':
    main()
