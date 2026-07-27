# Discord Bot Template

![Python 3.13](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![discord.py 2.7.1](https://img.shields.io/badge/discord.py-2.7.1-5865F2?logo=discord&logoColor=white)
![License MIT](https://img.shields.io/badge/License-MIT-green)

以 [`discord.py`](https://github.com/Rapptz/discord.py) 建立的 Discord Bot 基礎模板，內含 Cog 載入、前綴與斜線指令、管理指令、錯誤回報及日誌輪替。

## 功能

- 使用 Cog 拆分功能模組，啟動時自動載入 `cogs/` 下的模組。
- 提供前綴指令、斜線指令與 hybrid command 範例。
- 自動同步 application commands。
- 提供限伺服器管理員使用的模組管理與狀態指令。
- 提供限 application owner 使用的重啟指令與確認按鈕。
- 將未預期錯誤寫入日誌並回報給維護者。
- 使用 Loguru 輪替、保留及壓縮日誌。

## 環境需求

- Python 3.13
- discord.py 2.7.1

discord.py 官方目前要求 Python 3.8 以上；本專案以 Python 3.13 作為開發與 Docker 的驗證版本。

## Discord 應用程式設定

1. 到 [Discord Developer Portal](https://discord.com/developers/applications) 建立 application 與 Bot。
2. 在 Bot 頁面啟用 `Message Content Intent`，供前綴與 hybrid command 讀取訊息內容。
3. 使用 OAuth2 URL Generator 邀請 Bot，勾選以下 scopes：
   - `bot`
   - `applications.commands`
4. 至少授予以下 Bot permissions：
   - View Channels
   - Send Messages
   - Embed Links
   - Read Message History

模板預設不啟用 `Server Members Intent`。如果新增的 Cog 需要完整成員快取或成員事件，再於 Developer Portal 與程式中一併開啟。

## 安裝

### Windows PowerShell

```powershell
py -V:3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.template .env
```

### Linux / macOS

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.template .env
```

編輯 `.env`：

```env
DISCORD_BOT_TOKEN=your_token_here
DEBUG=false
MAINTAINER_ID=
```

| 變數 | 必填 | 說明 |
|------|------|------|
| `DISCORD_BOT_TOKEN` | 是 | Discord Bot Token |
| `DEBUG` | 否 | 設為 `true` 時輸出 DEBUG 等級的終端日誌 |
| `MAINTAINER_ID` | 否 | 接收錯誤回報的使用者 ID；未設定時使用 application owner |

## 執行

```bash
python main.py
```

VS Code 使用者也可以按 `F5`，選擇 `Discord Bot (Debug)` 啟動除錯設定。

## 範例指令

| 指令 | 說明 |
|------|------|
| `!ping` | 前綴指令範例 |
| `/ping_slash` | 斜線指令範例 |
| `!ping_hybrid`、`/ping_hybrid` | Hybrid command 範例 |
| `/載入模組` | 載入 Cog；限伺服器管理員 |
| `/卸載模組` | 卸載 Cog；限伺服器管理員 |
| `/重新載入模組` | 重新載入 Cog；限伺服器管理員 |
| `/機器人狀態` | 顯示延遲與模組狀態；限伺服器管理員 |
| `/重啟機器人` | 重新啟動程式；限 application owner |

`management` 是核心管理模組，無法透過指令卸載。

## 專案結構

```text
discord-bot-template/
├── cogs/
│   ├── basic.py           # 指令範例
│   └── management.py      # 管理與重啟指令
├── module/                # 可選的共用模組
├── tests/                 # 模板設定與權限測試
├── .dockerignore          # Docker build context 排除規則
├── .env.template          # 環境變數範本
├── Dockerfile
├── main.py                # Bot 啟動、Cog 載入與錯誤處理
└── requirements.txt
```

新增 Cog 時，在 `cogs/` 建立 Python 模組並提供非同步 `setup()`：

```python
from discord.ext import commands


class Example(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Example(bot))
```

## Docker

```bash
docker build -t discord-bot-template .
docker run -d \
  --name discord-bot-template \
  --restart unless-stopped \
  --env-file .env \
  discord-bot-template
```

日誌預設寫入容器內的 `/app/logs/system.log`。需要保留日誌時，可額外掛載 volume。

## 驗證

```bash
python -m unittest discover -s tests -v
python -m compileall main.py cogs module tests
```

## 授權

本專案採用 [MIT License](LICENSE)。
