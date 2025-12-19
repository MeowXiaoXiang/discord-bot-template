# Discord Bot Template

![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?logo=python) ![License MIT](https://img.shields.io/badge/License-MIT-green)

## 📦 專案介紹

基於 [`discord.py`](https://github.com/Rapptz/discord.py) 的 Discord Bot 開發模板。

設計理念：

- 結構清晰，易於擴充
- 模組化管理
- 適合快速開發

---

## 🧩 功能特色

🔹 **自訂 HelpCommand**  
  美化的 Embed 輸出樣式，支援指令查詢

🔹 **斜線指令同步**  
  自動同步與載入 `/` 指令

🔹 **管理指令**（限管理員）  
  `/載入模組`、`/卸載模組`、`/重新載入模組`、`/機器人狀態`

🔹 **重啟機器人**  
  `/重啟機器人`：含確認按鈕

🔹 **錯誤處理**  
  自動通知 Bot 擁有者

🔹 **Log 系統（loguru）**  
  自動建立、壓縮、輪替日誌

---

## 📁 專案結構

```bash
📦 discord-bot-template/
├── cogs/                # 功能模組
│   └── basic.py         # 範例指令
│
├── module/              # 輔助模組 (可選)
│   └── __init__.py
│
├── .vscode/             # VSCode 配置
│   └── launch.json      # F5 Debug 配置
│
├── .env.template        # 環境變數範本
├── main.py              # 主程式
├── Dockerfile           # Docker 部署 (可選)
├── requirements.txt     # 套件需求
└── README.md            # 說明文件
```

---

## 🚀 快速開始

### 1️⃣ 安裝依賴套件

確認 Python 3.12 或以上：

```bash
pip install -r requirements.txt
```

### 2️⃣ 設定環境變數

### 方式一：使用 .env 檔案（推薦）

將 `.env.template` 複製為 `.env`：

```bash
cp .env.template .env
```

編輯 `.env` 並填入你的設定：

```env
DISCORD_BOT_TOKEN=your_token_here
DEBUG=false
```

### 方式二：直接在啟動指令指定

```bash
# Linux/macOS
DISCORD_BOT_TOKEN="your_token_here" DEBUG="false" python main.py

# Windows (PowerShell)
$env:DISCORD_BOT_TOKEN="your_token_here"; $env:DEBUG="false"; python main.py

# Windows (CMD)
set DISCORD_BOT_TOKEN=your_token_here && set DEBUG=false && python main.py
```

---

## ▶️ 執行

**使用 .env 檔案：**

```bash
python main.py
```

**或直接指定環境變數：**

```bash
# Linux/macOS
DISCORD_BOT_TOKEN="your_token_here" DEBUG="false" python main.py

# Windows (PowerShell)
$env:DISCORD_BOT_TOKEN="your_token_here"; $env:DEBUG="false"; python main.py
```

### VSCode Debug 模式

按 `F5` 或使用「執行與偵錯」選擇 `Discord Bot (Debug)`，將自動啟用 DEBUG 模式。

---

## 🐳 Docker 部署（可選）

### 方式一：使用環境變數（推薦）

```bash
docker build -t discord-bot-template .
docker run -d \
  --name my_discord_bot \
  --restart unless-stopped \
  -e DISCORD_BOT_TOKEN="your_token_here" \
  -e DEBUG="false" \
  discord-bot-template
```

### 方式二：使用 .env 檔案

```bash
docker build -t discord-bot-template .
docker run -d \
  --name my_discord_bot \
  --restart unless-stopped \
  --env-file .env \
  discord-bot-template
```
