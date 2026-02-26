import tkinter as tk
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, 'backend')
frontend_path = os.path.join(current_dir, 'frontend')

if os.path.exists(backend_path):
    sys.path.insert(0, backend_path)
    print(f"[Info] 添加backend路径到导入路径: {backend_path}")

if os.path.exists(frontend_path):
    sys.path.insert(0, frontend_path)
    print(f"[Info] 添加frontend路径到导入路径: {frontend_path}")

print("[Info] 初始化完成，准备启动GUI")

from gui.chat_gui import ChatGUI
from gui.config_gui import ConfigGUI

chat_gui = None
config_root = None

def on_config_save(log_path, mic_enabled=False, asr_loaded=False, llm_loaded=False, ai_name="L"):
    global chat_gui, config_root
    
    if config_root:
        config_root.destroy()
    
    chat_root = tk.Tk()
    chat_gui = ChatGUI(chat_root, log_path, mic_enabled, asr_loaded, llm_loaded, ai_name)
    chat_root.mainloop()

if __name__ == "__main__":
    config_root = tk.Tk()
    config_gui = ConfigGUI(config_root, on_config_save)
    config_root.mainloop()
