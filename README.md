# Discord Bot Template

![Python 3.10](https://img.shields.io/badge/Python-3.10-blue?logo=python) ![License MIT](https://img.shields.io/badge/License-MIT-green)

## 📦 專案介紹

這是一個使用 [`discord.py`](https://github.com/Rapptz/discord.py) 架設的 Discord Bot 範本，目標是讓 **自己或任何想寫 Discord 機器人的人** 都能輕鬆上手。

設計理念是：

- 結構清晰，方便日後擴充功能或模組化管理
- 適合快速原型、自訂開發、朋友之間分享使用

如果你剛好也想寫 Discord Bot，又不想從空白開始，這份範本應該能幫上忙 🛠

---

## 🧩 功能特色

這個範本本身就具備一些可直接使用的功能：

🔹 **自訂前綴 HelpCommand**
  - 取代內建前綴指令 `help`，改為更美觀的 `Embed` 輸出樣式
  - 支援查詢所有指令、單一指令、分類群組

🔹 **斜線指令同步與載入**
  - 開機自動同步 `/` 斜線指令
  - 支援 `cogs` 模組化擴充（自動載入）

🔹 **管理指令模組**（限管理員／擁有者）
  - `/載入模組`、`/卸載模組`、`/重新載入模組`
  - `/機器人狀態`：可顯示延遲、權限、載入模組狀態

🔹 **重啟機器人指令**
  - `/重啟機器人`：支援確認按鈕，避免誤操作

🔹 **錯誤處理系統**
  - 當指令錯誤時會自動通知 Bot 擁有者
  - 支援前綴與斜線指令錯誤的 Embed 報告

🔹 **Log 記錄系統（loguru）**
  - 自動建立 log 檔案，支援壓縮與過期清理
  - 命令錯誤、模組載入失敗都會詳細記錄

---

## 📁 專案結構

```
📦 discord-bot-template/
├── cogs/                    # 所有功能模組放置處
│   └── basic.py             # 範例指令包含前墜、斜線、混合
│
├── config/
│   └── settings.json.template   # 設定檔範本
│
├── module/                # 輔助模組，可依需求擴充 (可移除)
│   └── __init__.py
│
├── .env.template          # .env 環境變數範本（需填入 Bot Token）
├── main.py                # 主程序入口
├── Dockerfile             # Docker 部署（可選）
├── requirements.txt       # 套件需求
└── README.md              # 說明文件
```

---

## 🚀 快速開始

### 1️⃣ 安裝依賴套件

請先確認使用 Python 3.10 或以上版本：

```bash
pip install -r requirements.txt
```

### 2️⃣ 建立設定檔

將 `config/settings.json.template` 複製為：

```bash
cp config/settings.json.template config/settings.json
```

再根據註解說明，填入你的偏好設定（例如：是否啟用 DEBUG、Log 輸出設定等）

### 3️⃣ 設定 .env

將 `.env.template` 改名為 `.env`，並加入你的 Discord Bot Token：

```env
DISCORD_BOT_TOKEN=你的TOKEN
```

---

## ▶️ 執行

```bash
python main.py
```

若一切設定正確，機器人將會啟動並同步斜線指令。

---

## 🐳 Docker 執行（可選）

若你希望部署到 Docker，可使用以下方式：

```bash
docker build -t discord-bot-template .
docker run -d \
  --name my_discord_bot \
  -e DISCORD_BOT_TOKEN=你的TOKEN \
  -v /path/to/config:/app/config \
  discord-bot-template
```
