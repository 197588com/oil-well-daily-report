#
# Buildozer 配置文件 - 油井报表管理系统 Android APK
#
# 打包命令:
#   buildozer android debug          # 构建 APK
#   buildozer android debug deploy   # 构建并部署到设备
#   buildozer android debug deploy run  # 构建、部署并运行
#

[app]
# 应用标题
title = 油井报表管理系统

# 包名（必须唯一）
package.name = oilwellreport

# 域名（反向域名格式）
package.domain = com.yourcompany

# 源代码目录
source.dir = .

# 主程序入口
source.include_exts = py,html,css,js,png,jpg,jpeg,ttf,txt,db

# 版本号
version = 1.0.0

# (str) Android SDK 路径（留空则自动下载）
android.sdk_path = /Users/yanglin/Library/Android/sdk

# (str) Android NDK 路径（留空则自动下载）
android.ndk_path = /Users/yanglin/Library/Android/sdk/ndk

# (str) Python for android branch to use
p4a.branch = develop

# 最低 Android API 级别
# Android 8.0+ (API 26)
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b

# 构建工具版本
android.build_tools = 33.0.0

# 应用权限
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# 允许明文 HTTP 通信（用于访问 localhost Flask）
android.uses_library = 
android.manifest.placeholders = [android:usesCleartextTraffic="true"]

# 是否使用私人存储
android.private_storage = True

# 是否需要互联网权限
android.add_aars = 
android.add_assets = 

# 图标配置（可选）
# android.presplash = presplash.png
# android.icon = icon.png

# 屏幕方向
android.orientation = portrait

# 是否全屏
android.fullscreen = 1

# 日志级别
android.logcat_filters = *:S python:D

# 启动模式（标准 Kivy 启动）
android.archs = armeabi-v7a, arm64-v8a

# 额外依赖（Python 库）
requirements = python3,flask,flask-cors,sqlite3,pyjnius,urllib3,charset_normalizer,idna,certifi,requests,click,itsdangerous,jinja2,markupsafe,werkzeug

# 使用 webview bootstrap（不需要 Kivy/SDL2）
p4a.bootstrap = webview

# 源码包含的文件和目录
source.include_patterns = templates/*, static/*, backend.py, main.py

# Android 主程序入口
# webview bootstrap 自动查找 main.py 作为入口
# （不需要额外设置）

[buildozer]
# 构建日志级别
log_level = 2

# 是否显示警告
warn_on_root = 1
