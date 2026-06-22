# 油井报表管理系统

支持 **Windows 单文件版** 和 **Android APK 版** 的本地数据库版油井报表管理系统。

## 功能特性

- 📝 **数据录入**：录入每日井口压力、温度、含水、气表读数，自动计算液量、油量、水量、气量
- 📋 **历史报表**：查看每口井的历史数据，默认显示最近5条，可展开查看全部
- ✏️ **历史编辑**：支持修改任意历史日期的数据
- 🗑️ **数据删除**：支持删除单条记录或整口井
- 🔄 **补录功能**：自动检测缺失日期，一键补录
- ⚙️ **系数设置**：自定义液量系数、气量计算方式（差值法/系数法）
- 📈 **趋势分析**：Chart.js 绘制日产油/液/水趋势图
- 📰 **日报生成**：自动生成对比日报，支持 PDF/PNG 导出
- 🏗️ **井名管理**：支持添加、删除油井，完全自定义井名
- 💾 **数据备份**：支持 JSON/CSV 导入导出
- 🗄️ **本地数据库**：使用 SQLite 持久化存储，数据安全可靠

## 项目结构

```
oil_well_app/
├── backend.py              # Flask + SQLite 后端 API
├── main_windows.py         # Windows 桌面启动器 (pywebview)
├── main_android.py         # Android 启动器 (Kivy + WebView)
├── build_windows.py        # Windows 打包脚本 (PyInstaller)
├── buildozer.spec          # Android 打包配置 (Buildozer)
├── requirements.txt        # Python 依赖列表
├── templates/
│   └── index.html          # 前端页面
├── static/                 # 静态资源目录
└── README.md               # 本文件
```

## 技术栈

| 组件 | Windows | Android |
|------|---------|---------|
| 后端 | Flask + SQLite | Flask + SQLite |
| 前端 | HTML5 + Tailwind CSS + Chart.js | HTML5 + Tailwind CSS + Chart.js |
| 窗口 | pywebview | Kivy + jnius WebView |
| 打包 | PyInstaller | Buildozer |

## 一、Windows 单文件版

### 1.1 安装依赖

```bash
pip install pywebview flask flask-cors pyinstaller
```

### 1.2 开发运行

```bash
cd oil_well_app
python main_windows.py
```

### 1.3 打包为单文件 exe

```bash
cd oil_well_app
python build_windows.py
```

或直接运行 PyInstaller 命令：

```bash
cd oil_well_app
pyinstaller --onefile --windowed --add-data "templates;templates" --add-data "static;static" --name "油井报表管理系统" --clean --noconfirm main_windows.py
```

打包完成后，`dist/油井报表管理系统.exe` 即为单文件可执行程序。

数据库文件 `oil_well.db` 会在 exe 同级目录自动创建。

## 二、Android APK 版

### 2.1 环境准备

#### 系统要求
- Python 3.8+
- 操作系统：Linux 推荐（Windows 可用 WSL2）
- 至少 10GB 磁盘空间
- 8GB+ 内存

#### 安装依赖

```bash
pip install buildozer cython
```

#### 安装 Android SDK/NDK（可选）

Buildozer 可以自动下载，但首次下载需要较长时间。

### 2.2 配置 buildozer.spec

已包含在项目根目录，关键配置项：

```ini
[app]
title = 油井报表管理系统
package.name = oilwellreport
package.domain = com.yourcompany
version = 1.0.0

android.api = 33
android.minapi = 21
android.archs = armeabi-v7a, arm64-v8a

android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.fullscreen = 1

requirements = python3,flask,flask-cors,sqlite3,jnius,pyjnius,urllib3,charset_normalizer,idna,certifi,requests,click,itsdangerous,jinja2,markupsafe,werkzeug

p4a.bootstrap = sdl2
```

### 2.3 构建 APK

#### 调试版（Debug）

```bash
cd oil_well_app
buildozer android debug
```

构建完成后，APK 位于 `.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/oilwellreport/bin/` 目录。

#### 构建并部署到设备

```bash
# 构建
cd oil_well_app
buildozer android debug

# 部署到已连接的 Android 设备
buildozer android deploy

# 部署并运行
buildozer android deploy run
```

#### 完整日志

```bash
buildozer android debug deploy run logcat
```

### 2.4 常见问题

#### 首次构建失败

首次构建会自动下载 Android SDK、NDK、Gradle 等工具，需要很长时间。如果下载失败，可以手动配置：

```bash
# 设置环境变量（在 .bashrc 或 .zshrc 中）
export ANDROIDSDK="$HOME/.buildozer/android/platform/android-sdk"
export ANDROIDNDK="$HOME/.buildozer/android/platform/android-ndk-r25b"
```

#### 内存不足

如果构建时出现内存不足错误，增加交换空间：

```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 设备连接失败

确保设备已开启 USB 调试模式：
1. 设置 → 关于手机 → 连续点击"版本号"7次开启开发者模式
2. 设置 → 系统 → 开发者选项 → 开启 USB 调试
3. 连接电脑后允许调试授权

验证连接：
```bash
adb devices
```

## 三、开发运行（测试模式）

### 3.1 纯 Flask 模式（浏览器访问）

```bash
cd oil_well_app
python backend.py
# 访问 http://localhost:5000
```

### 3.2 桌面 Kivy 测试（Android 代码桌面测试）

```bash
cd oil_well_app
python main_android.py
```

这会在桌面启动 Flask 服务器，并尝试打开 webview（如果安装了 pywebview）。

## 四、数据库说明

系统使用 SQLite 本地数据库，数据表结构：

| 表名 | 说明 |
|------|------|
| `well_data` | 油井日报数据（日期、压力、液量、油量、水量、气量、累计值等） |
| `well_coeff` | 油井系数配置（液量系数、气量计算方式、气量系数） |
| `well_names` | 油井名称列表 |
| `daily_notes` | 日报备注 |

数据库文件位置：
- **Windows**: 与 `油井报表管理系统.exe` 同级目录
- **Android**: 应用私有存储目录（`/data/data/com.yourcompany.oilwellreport/files/`）

## 五、API 接口

后端提供以下 RESTful API：

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 返回前端页面 |
| `/api/data` | GET | 获取所有数据（井列表、数据、系数） |
| `/api/data` | POST | 保存所有数据 |
| `/api/well` | POST | 添加新井 |
| `/api/well/<name>` | DELETE | 删除油井及其所有数据 |
| `/api/well/<name>/record/<date>` | DELETE | 删除单条记录 |
| `/api/note/<date>` | GET | 获取日报备注 |
| `/api/note/<date>` | POST | 保存日报备注 |
| `/api/export/json` | GET | 导出 JSON 备份 |
| `/api/import/json` | POST | 导入 JSON 备份 |
| `/api/export/csv` | GET | 导出 CSV 报表 |

## 六、截图与使用

1. 启动应用后，默认显示"历史报表"页面
2. 点击"📝 录入今日数据"录入新的日报数据
3. 点击"⚙️ 系数设置"配置各井的计算系数
4. 点击"📈 趋势分析"查看产量趋势图
5. 点击"📰 日报生成"生成对比日报并导出 PDF/PNG
6. 点击"🏗️ 井名管理"添加或删除油井

## 七、更新日志

### v1.0.0
- 支持历史报表编辑、删除、补录
- 默认展示5条记录，可展开查看全部
- 产液量单独显示
- 支持自定义井名（添加/删除）
- 本地 SQLite 数据库存储
- 支持 Windows 单文件 exe 和 Android APK

## 八、开源协议

MIT License
