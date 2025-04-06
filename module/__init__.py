"""
Discord Bot 模組區
------------------------

此資料夾用於擴充自訂功能模組，建議用來封裝與指令無關的共用邏輯，例如：

- 資料庫操作（如 SQLite、TinyDB）
- 快取狀態管理（如暫存清單）
- 通知系統（如定時推播）
- 第三方 API 整合（如遊戲查詢等）

將邏輯自 `cogs` 拆分出來，可提升可讀性與維護性。

----------------------------------
【__init__.py 的用途】

此檔為 Python 模組初始化入口，當執行：

    from module import send_notify, some_class

Python 將載入 `module/__init__.py`，並只允許匯入 `__all__` 列出的成員。

範例如下：

    # module/__init__.py
    from .notifier import send_notify
    from .manager import some_class

    __all__ = ['send_notify', 'some_class']

如此在其他檔案中可直接使用：

    from module import send_notify, some_class

而不需知道實際檔案名稱，具封裝性與集中管理匯出的優點。

多個成員請用逗號分隔，例如：

    __all__ = ['class_1', 'class_2']

----------------------------------
【不使用 __init__.py 時的寫法】

若未定義 `__init__.py` 或未使用 `__all__`，則必須這樣匯入：

    from module.notifier import send_notify
    from module.manager import some_class

此寫法較直觀，適合快速開發，但當模組數量增多時建議改用 `__init__.py` 管理，避免重複與混亂。

----------------------------------
【完整範例】

1. 建立 `notifier.py`：
    
    # module/notifier.py
    def send_notify(msg: str):
        print(f"[通知] {msg}")

2. 建立 `manager.py`：

    # module/manager.py
    class some_class:
        pass

3. 在 `__init__.py` 中整合公開項目：

    from .notifier import send_notify
    from .manager import some_class

    __all__ = ['send_notify', 'some_class']

4. 在其他檔案中匯入使用：

    from module import send_notify, some_class

    @commands.command()
    async def ping(ctx):
        send_notify("收到 ping 指令")
        await ctx.send("Pong!")

----------------------------------

你可自由新增其他模組，並依需求選擇是否加入 `__init__.py` 的匯出清單，建立一套適合自身開發流程的工具架構。
"""