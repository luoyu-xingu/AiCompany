import tkinter as tk
import os
import sys

# 添加backend目录到导入路径
backend_path = os.path.join(os.path.dirname(__file__), 'ai_companion_system', 'backend')
if os.path.exists(backend_path):
    sys.path.insert(0, backend_path)
    print(f"[Info] 添加backend路径到导入路径: {backend_path}")

# 导入app模块
try:
    from ai_companion_system.backend import app
    print("[OK] app模块导入成功")
except ImportError as e:
    print(f"[Error] app模块导入失败: {e}")
    print("[Info] 程序将退出")
    sys.exit(1)

# 导入拆分后的模块
from gui.chat_gui import ChatGUI
from gui.config_gui import ConfigGUI

# 全局变量
chat_gui = None
config_root = None

# 配置保存回调
def on_config_save(log_path):
    """配置保存回调"""
    global chat_gui, config_root
    
    # 关闭配置窗口
    if config_root:
        config_root.destroy()
    
    # 创建聊天窗口
    chat_root = tk.Tk()
    chat_gui = ChatGUI(chat_root, log_path)
    chat_root.mainloop()

if __name__ == "__main__":
    # 创建配置窗口
    config_root = tk.Tk()
    config_gui = ConfigGUI(config_root, on_config_save)
    config_root.mainloop()
