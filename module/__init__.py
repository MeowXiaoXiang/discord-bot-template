"""
Discord Bot 模組區
------------------
用於封裝與指令無關的共用邏輯，例如：
- 資料庫操作
- 快取管理
- 通知系統
- 第三方 API 整合

使用範例：
    from .your_module import some_function
    __all__ = ['some_function']

在其他檔案中：
    from module import some_function
"""