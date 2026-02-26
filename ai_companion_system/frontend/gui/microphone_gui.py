import tkinter as tk
from tkinter import ttk
import os
import threading
from PIL import Image, ImageDraw, ImageFont, ImageTk

class MicrophoneGUI:
    def __init__(self, root, on_start_chat, log_path):
        self.root = root
        self.root.title("AI陪伴系统 - 语音设置")
        self.on_start_chat = on_start_chat
        self.log_path = log_path
        
        self.root.resizable(False, False)
        
        self.window_width = 500
        self.window_height = 400
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        self.bg_image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "photo1.jpg")
        
        self._mic_enabled = False
        self._asr_loaded = False
        self._llm_loaded = False
        self._loading = False
        
        self._model_manager = None
        
        self.load_background_image()
        self.setup_main_background()
        self.create_microphone_area()
        self.create_model_status_area()
        self.create_control_area()
        
        self.load_button.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._init_model_manager)
        thread.daemon = True
        thread.start()
    
    def load_background_image(self):
        try:
            self.original_bg_image = Image.open(self.bg_image_path)
            self.original_bg_image = self.original_bg_image.resize(
                (self.window_width, self.window_height), Image.Resampling.LANCZOS
            )
        except Exception as e:
            self.original_bg_image = None
    
    def setup_main_background(self):
        if self.original_bg_image:
            self.bg_image = ImageTk.PhotoImage(self.original_bg_image)
            self.background_label = tk.Label(self.root, image=self.bg_image)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.root.configure(bg='#ffffff')
    
    def create_microphone_area(self):
        self.mic_frame = tk.Frame(self.root, width=460, height=120, bg='#ffffff', bd=0)
        self.mic_frame.place(x=20, y=20)
        self.mic_frame.pack_propagate(False)
        
        self.mic_canvas = tk.Canvas(
            self.mic_frame, 
            width=460, 
            height=120, 
            bg='#ffffff',
            highlightthickness=0
        )
        self.mic_canvas.place(x=0, y=0)
        
        self._draw_microphone_icon(disabled=True)
        
        self.mic_status_label = tk.Label(
            self.mic_frame,
            text="麦克风状态: 未启用",
            font=("SimHei", 12, "bold"),
            bg='#ffffff',
            fg='#666666'
        )
        self.mic_status_label.place(x=150, y=20)
        
        self.mic_button = tk.Button(
            self.mic_frame,
            text="启用麦克风",
            command=self.toggle_microphone,
            font=('SimHei', 11, 'bold'),
            width=12,
            bg='#5cb85c',
            relief='flat',
            bd=0,
            highlightthickness=0,
            activebackground='#449d44',
            fg='#ffffff',
            cursor='hand2'
        )
        self.mic_button.place(x=180, y=70)
    
    def _draw_microphone_icon(self, disabled=True):
        self.mic_canvas.delete("all")
        
        center_x = 60
        center_y = 60
        
        color = '#cccccc' if disabled else '#4a90d9'
        
        self.mic_canvas.create_oval(
            center_x - 20, center_y - 30,
            center_x + 20, center_y + 10,
            fill=color, outline=color
        )
        
        self.mic_canvas.create_rectangle(
            center_x - 25, center_y + 5,
            center_x + 25, center_y + 25,
            fill='#ffffff', outline=color, width=2
        )
        
        self.mic_canvas.create_arc(
            center_x - 30, center_y - 10,
            center_x + 30, center_y + 40,
            start=200, extent=140,
            style=tk.ARC, outline=color, width=3
        )
        
        self.mic_canvas.create_line(
            center_x, center_y + 40,
            center_x, center_y + 55,
            fill=color, width=3
        )
        
        self.mic_canvas.create_line(
            center_x - 15, center_y + 55,
            center_x + 15, center_y + 55,
            fill=color, width=3
        )
    
    def create_model_status_area(self):
        self.status_frame = tk.Frame(self.root, width=460, height=160, bg='#ffffff', bd=0)
        self.status_frame.place(x=20, y=150)
        self.status_frame.pack_propagate(False)
        
        self.status_canvas = tk.Canvas(
            self.status_frame,
            width=460,
            height=160,
            bg='#ffffff',
            highlightthickness=1,
            highlightbackground='#dddddd'
        )
        self.status_canvas.place(x=0, y=0)
        
        self.status_canvas.create_text(
            230, 20,
            text="模型加载状态",
            font=("SimHei", 12, "bold"),
            fill='#333333'
        )
        
        self.asr_status_label = tk.Label(
            self.status_frame,
            text="● ASR模型: 未加载",
            font=("SimHei", 11),
            bg='#ffffff',
            fg='#999999'
        )
        self.asr_status_label.place(x=30, y=50)
        
        self.llm_status_label = tk.Label(
            self.status_frame,
            text="● LLM模型: 未加载",
            font=("SimHei", 11),
            bg='#ffffff',
            fg='#999999'
        )
        self.llm_status_label.place(x=30, y=80)
        
        self.memory_label = tk.Label(
            self.status_frame,
            text="显存使用: --",
            font=("SimHei", 11),
            bg='#ffffff',
            fg='#666666'
        )
        self.memory_label.place(x=30, y=110)
        
        self.device_label = tk.Label(
            self.status_frame,
            text="设备: --",
            font=("SimHei", 11),
            bg='#ffffff',
            fg='#666666'
        )
        self.device_label.place(x=250, y=110)
    
    def create_control_area(self):
        self.control_frame = tk.Frame(self.root, width=460, height=60, bg='#ffffff', bd=0)
        self.control_frame.place(x=20, y=320)
        self.control_frame.pack_propagate(False)
        
        self.load_button = tk.Button(
            self.control_frame,
            text="加载模型",
            command=self.load_models,
            font=('SimHei', 11, 'bold'),
            width=12,
            bg='#4a90d9',
            relief='flat',
            bd=0,
            highlightthickness=0,
            activebackground='#357abd',
            fg='#ffffff',
            cursor='hand2'
        )
        self.load_button.place(x=50, y=10)
        
        self.start_button = tk.Button(
            self.control_frame,
            text="开始聊天",
            command=self.start_chat,
            font=('SimHei', 11, 'bold'),
            width=12,
            bg='#d9534f',
            relief='flat',
            bd=0,
            highlightthickness=0,
            activebackground='#c9302c',
            fg='#ffffff',
            cursor='hand2'
        )
        self.start_button.place(x=280, y=10)
    
    def _init_model_manager(self):
        try:
            from app.models.model_manager import model_manager
            self._model_manager = model_manager
            
            self._update_device_info()
            
            def enable_button():
                if hasattr(self, 'load_button') and self.load_button.winfo_exists():
                    try:
                        self.load_button.config(state=tk.NORMAL)
                    except:
                        pass
            self.root.after(0, enable_button)
        except Exception as e:
            print(f"[Error] 初始化模型管理器失败: {e}")

    def _update_device_info(self):
        if self._model_manager:
            device = self._model_manager.get_device()
            device_name = {
                "cuda": "GPU (CUDA)",
                "mps": "GPU (MPS)",
                "cpu": "CPU"
            }.get(device, device)
            
            self.device_label.config(text=f"设备: {device_name}")
            self._update_memory_info()

    def _update_memory_info(self):
        if self._model_manager:
            memory_info = self._model_manager.get_memory_usage()
            
            if "gpu_memory_allocated" in memory_info:
                allocated = memory_info["gpu_memory_allocated"]
                total = memory_info["gpu_memory_total"]
                self.memory_label.config(
                    text=f"显存使用: {allocated:.2f}GB / {total:.2f}GB"
                )
            else:
                self.memory_label.config(text="显存使用: CPU模式")
    
    def toggle_microphone(self):
        self._mic_enabled = not self._mic_enabled
        
        if self._mic_enabled:
            self.mic_button.config(text="禁用麦克风", bg='#d9534f')
            self.mic_status_label.config(
                text="麦克风状态: 已启用",
                fg='#4a90d9'
            )
            self._draw_microphone_icon(disabled=False)
        else:
            self.mic_button.config(text="启用麦克风", bg='#5cb85c')
            self.mic_status_label.config(
                text="麦克风状态: 未启用",
                fg='#666666'
            )
            self._draw_microphone_icon(disabled=True)
    
    def load_models(self):
        if self._loading:
            return
        
        if not self._model_manager:
            print("[Error] 模型管理器未初始化")
            return
        
        self._loading = True
        self.load_button.config(text="加载中...", state=tk.DISABLED)
        
        thread = threading.Thread(target=self._load_models_thread)
        thread.daemon = True
        thread.start()
    
    def _load_models_thread(self):
        print("[Info] 开始加载模型线程...")
        try:
            if self._model_manager:
                print("[Info] 模型管理器可用，开始加载模型...")
                self._asr_loaded = False
                self._llm_loaded = False
                
                self._update_asr_status("加载中...", '#f0ad4e')
                print("[Info] 开始加载ASR模型...")
                asr_model = self._model_manager.load_asr_model()
                if asr_model:
                    self._asr_loaded = True
                    self._update_asr_status("已加载", '#5cb85c')
                    print("[Info] ASR模型加载成功")
                else:
                    self._asr_loaded = False
                    self._update_asr_status("加载失败", '#d9534f')
                    print("[Error] ASR模型加载失败")
                
                self._update_llm_status("加载中...", '#f0ad4e')
                print("[Info] 开始加载LLM模型...")
                llm_model = self._model_manager.load_llm_model()
                if llm_model:
                    self._llm_loaded = True
                    self._update_llm_status("已加载", '#5cb85c')
                    print("[Info] LLM模型加载成功")
                else:
                    self._llm_loaded = False
                    self._update_llm_status("加载失败", '#d9534f')
                    print("[Error] LLM模型加载失败")
                
                self._update_memory_info()
                print("[Info] 显存信息已更新")
                
                if self._asr_loaded and self._llm_loaded:
                    print("[Info] 所有模型加载完成")
                else:
                    print("[Warning] 部分模型未加载成功")
        
        except Exception as e:
            print(f"[Error] 加载模型失败: {e}")
            import traceback
            traceback.print_exc()
            self._asr_loaded = False
            self._llm_loaded = False
            self._update_asr_status("加载失败", '#d9534f')
            self._update_llm_status("加载失败", '#d9534f')
        
        finally:
            self._loading = False
            print("[Info] 加载线程完成，更新按钮状态...")
            def update_button():
                if hasattr(self, 'load_button') and self.load_button.winfo_exists():
                    try:
                        button_text = "重新加载模型" if self._asr_loaded or self._llm_loaded else "加载模型"
                        self.load_button.config(text=button_text, state=tk.NORMAL)
                        print(f"[Info] 按钮状态已更新为: {button_text}")
                    except tk.TclError:
                        pass
            self.root.after(0, update_button)
    
    def _update_asr_status(self, status: str, color: str):
        self.root.after(0, lambda: self.asr_status_label.config(
            text=f"● ASR模型: {status}",
            fg=color
        ))
    
    def _update_llm_status(self, status: str, color: str):
        self.root.after(0, lambda: self.llm_status_label.config(
            text=f"● LLM模型: {status}",
            fg=color
        ))
    
    def start_chat(self):
        if self.on_start_chat:
            self.on_start_chat(
                self.log_path,
                self._mic_enabled,
                self._asr_loaded,
                self._llm_loaded
            )
        
        self.root.quit()
    
    def is_mic_enabled(self) -> bool:
        return self._mic_enabled
    
    def is_asr_loaded(self) -> bool:
        return self._asr_loaded
    
    def is_llm_loaded(self) -> bool:
        return self._llm_loaded
