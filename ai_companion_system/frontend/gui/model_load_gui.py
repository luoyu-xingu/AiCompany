import tkinter as tk
import os
import threading
from PIL import Image, ImageDraw, ImageFont, ImageTk

class ModelLoadGUI:
    def __init__(self, root, on_start_chat, log_path, bg_cache=None, prompt=None, ai_name=None):
        self.root = root
        self.root.title("AI陪伴系统 - 模型加载")
        self.on_start_chat = on_start_chat
        self.log_path = log_path
        self._prompt = prompt or "你是一个智能AI助手，帮助用户回答问题"
        self._ai_name = ai_name or "L"
        
        self.root.resizable(False, False)
        
        self.window_width = 500
        self.window_height = 350
        
        self._asr_loaded = False
        self._llm_loaded = False
        self._loading = False
        
        self._model_manager = None
        
        if bg_cache:
            self.bg_image = ImageTk.PhotoImage(bg_cache)
            self.background_label = tk.Label(self.root, image=self.bg_image)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.root.configure(bg='#ffffff')
        
        self.create_model_status_area()
        self.create_control_area()
        
        # 在后台线程中初始化模型管理器，避免阻塞界面
        import threading
        thread = threading.Thread(target=self._init_model_manager)
        thread.daemon = True
        thread.start()
    
    def create_model_status_area(self):
        self.status_frame = tk.Frame(self.root, width=460, height=180, bg='#ffffff', bd=0)
        self.status_frame.place(x=20, y=80)
        self.status_frame.pack_propagate(False)
        
        self.status_canvas = tk.Canvas(
            self.status_frame,
            width=460,
            height=180,
            bg='#ffffff',
            highlightthickness=1,
            highlightbackground='#dddddd'
        )
        self.status_canvas.place(x=0, y=0)
        
        self.status_canvas.create_text(
            230, 20,
            text="模型加载状态",
            font=("SimHei", 14, "bold"),
            fill='#333333'
        )
        
        self.asr_status_label = tk.Label(
            self.status_frame,
            text="● ASR模型: 未加载",
            font=("SimHei", 12),
            bg='#ffffff',
            fg='#999999'
        )
        self.asr_status_label.place(x=30, y=55)
        
        self.llm_status_label = tk.Label(
            self.status_frame,
            text="● LLM模型: 未加载",
            font=("SimHei", 12),
            bg='#ffffff',
            fg='#999999'
        )
        self.llm_status_label.place(x=30, y=90)
        
        self.memory_label = tk.Label(
            self.status_frame,
            text="显存使用: --",
            font=("SimHei", 11),
            bg='#ffffff',
            fg='#666666'
        )
        self.memory_label.place(x=30, y=130)
        
        self.device_label = tk.Label(
            self.status_frame,
            text="设备: --",
            font=("SimHei", 11),
            bg='#ffffff',
            fg='#666666'
        )
        self.device_label.place(x=250, y=130)
    
    def create_control_area(self):
        self.control_frame = tk.Frame(self.root, width=460, height=60, bg='#ffffff', bd=0)
        self.control_frame.place(x=20, y=270)
        self.control_frame.pack_propagate(False)
        
        self.load_button = tk.Button(
            self.control_frame,
            text="加载模型",
            command=self.load_models,
            font=('SimHei', 12, 'bold'),
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
            font=('SimHei', 12, 'bold'),
            width=12,
            bg='#d9534f',
            relief='flat',
            bd=0,
            highlightthickness=0,
            activebackground='#c9302c',
            fg='#ffffff',
            cursor='hand2',
            state=tk.DISABLED
        )
        self.start_button.place(x=280, y=10)
    
    def _init_model_manager(self):
        try:
            from app.models.model_manager import model_manager
            self._model_manager = model_manager
            self._model_manager.set_log_path(self.log_path)
            self._model_manager.set_prompt(self._prompt)
            self._model_manager.set_ai_name(self._ai_name)
            self._update_device_info()
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
                self.memory_label.config(text=f"显存使用: {allocated:.2f}GB / {total:.2f}GB")
            else:
                self.memory_label.config(text="显存使用: CPU模式")
    
    def load_models(self):
        if self._loading:
            return
        
        self._loading = True
        self.load_button.config(text="加载中...", state=tk.DISABLED)
        self.start_button.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._load_models_thread)
        thread.daemon = True
        thread.start()
    
    def _load_models_thread(self):
        try:
            if self._model_manager:
                self._update_asr_status("创建模型...", '#f0ad4e')
                
                asr_model = self._model_manager.load_asr_model()
                if asr_model:
                    self._update_asr_status("初始化中...", '#f0ad4e')
                    
                    if self._model_manager.initialize_asr_model():
                        self._asr_loaded = True
                        self._update_asr_status("已加载", '#5cb85c')
                    else:
                        self._update_asr_status("初始化失败", '#d9534f')
                else:
                    self._update_asr_status("创建失败", '#d9534f')
                
                self._update_llm_status("创建模型...", '#f0ad4e')
                
                llm_model = self._model_manager.load_llm_model()
                if llm_model:
                    self._update_llm_status("初始化中...", '#f0ad4e')
                    
                    if self._model_manager.initialize_llm_model():
                        self._llm_loaded = True
                        self._update_llm_status("已加载", '#5cb85c')
                    else:
                        self._update_llm_status("初始化失败", '#d9534f')
                else:
                    self._update_llm_status("创建失败", '#d9534f')
                
                self._update_memory_info()
        except Exception as e:
            print(f"[Error] 加载模型失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._loading = False
            self.root.after(0, lambda: self.load_button.config(text="加载模型", state=tk.NORMAL))
            # 只有当ASR和LLM模型都加载完成时，才启用开始聊天按钮
            if self._asr_loaded and self._llm_loaded:
                self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            else:
                self.root.after(0, lambda: self.start_button.config(state=tk.DISABLED))
    
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
            self.on_start_chat(self.log_path, self._asr_loaded, self._llm_loaded, self._ai_name)
        self.root.quit()
    
    def is_asr_loaded(self) -> bool:
        return self._asr_loaded
    
    def is_llm_loaded(self) -> bool:
        return self._llm_loaded
