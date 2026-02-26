import tkinter as tk
import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageTk

class ConfigGUI:
    _bg_image_cache = None
    _font_cache = None
    _third_bg_cache = None
    
    def __init__(self, root, on_config_save):
        self.root = root
        self.root.title("AI陪伴系统配置")
        self.on_config_save = on_config_save
        
        self.root.resizable(False, False)
        
        self.window_width = 500
        self.window_height = 300
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        self.bg_image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "photo1.jpg")
        
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
        
        self._init_caches()
        
        self.create_first_config_area()
    
    def _init_caches(self):
        if ConfigGUI._bg_image_cache is None:
            try:
                img = Image.open(self.bg_image_path)
                ConfigGUI._bg_image_cache = img
            except:
                ConfigGUI._bg_image_cache = None
        
        if ConfigGUI._font_cache is None:
            try:
                ConfigGUI._font_cache = {
                    'title': ImageFont.truetype("simhei.ttf", 24),
                    'label': ImageFont.truetype("simhei.ttf", 14)
                }
            except:
                default_font = ImageFont.load_default()
                ConfigGUI._font_cache = {
                    'title': default_font,
                    'label': default_font
                }
        
        if ConfigGUI._third_bg_cache is None:
            try:
                img = Image.open(self.bg_image_path)
                img = img.resize((500, 350), Image.Resampling.LANCZOS)
                
                draw = ImageDraw.Draw(img)
                font = ConfigGUI._font_cache.get('title', ImageFont.load_default())
                
                text = "AICompany"
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                x = (500 - text_width) // 2
                y = 30
                
                for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    draw.text((x+dx, y+dy), text, font=font, fill="white")
                draw.text((x, y), text, font=font, fill="#1a1a1a")
                
                ConfigGUI._third_bg_cache = img
            except:
                ConfigGUI._third_bg_cache = None
    
    def _get_bg_image(self, width, height):
        if ConfigGUI._bg_image_cache:
            return ConfigGUI._bg_image_cache.resize((width, height), Image.Resampling.LANCZOS)
        return None
    
    def _draw_title_on_image(self, image, text, y=100):
        if image is None:
            return None
        
        draw = ImageDraw.Draw(image)
        font = ConfigGUI._font_cache.get('title', ImageFont.load_default())
        
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x = (image.width - text_width) // 2
        
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text((x+dx, y+dy), text, font=font, fill="white")
        draw.text((x, y), text, font=font, fill="#1a1a1a")
        
        return image
    
    def setup_background(self, image):
        if image:
            self.bg_image = ImageTk.PhotoImage(image)
            self.background_label = tk.Label(self.root, image=self.bg_image)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('log_path', None)
        except:
            pass
        return None
    
    def save_config(self, log_path):
        try:
            config = {
                'log_path': log_path,
                'prompt': self.prompt_var.get() if hasattr(self, 'prompt_var') else "你是一个智能AI助手，帮助用户回答问题",
                'ai_name': self.ai_name_var.get() if hasattr(self, 'ai_name_var') else "L"
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def load_history_prompt(self):
        """加载历史Prompt"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'prompt' in config:
                        self.prompt_var.set(config['prompt'])
        except:
            pass
    
    def delete_logs(self, log_path):
        try:
            if os.path.exists(log_path):
                import shutil
                shutil.rmtree(log_path, ignore_errors=True)
        except:
            pass
    
    def create_first_config_area(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        bg = self._get_bg_image(self.window_width, self.window_height)
        bg = self._draw_title_on_image(bg, "AICompany", y=100)
        self.setup_background(bg)
        
        self.start_button = tk.Button(
            self.root, 
            text="开始", 
            command=self.show_second_config, 
            font=('SimHei', 12, 'bold'), 
            width=12, 
            bg='#d9534f', 
            relief='flat', 
            bd=0, 
            highlightthickness=0,
            activebackground='#c9302c', 
            fg='#ffffff', 
            cursor='hand2'
        )
        self.start_button.place(x=215, y=200)
    
    def show_second_config(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_second_config_area()
    
    def create_second_config_area(self):
        self.window_height = 400
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        bg = self._get_bg_image(self.window_width, self.window_height)
        bg = self._draw_title_on_image(bg, "AICompany", y=30)
        
        if bg:
            draw = ImageDraw.Draw(bg)
            font = ConfigGUI._font_cache.get('label', ImageFont.load_default())
            draw.text((50, 80), "日志保存路径:", font=font, fill="#333333")
            draw.text((50, 160), "模型Prompt:", font=font, fill="#333333")
            draw.text((50, 240), "AI回复者名称:", font=font, fill="#333333")
        
        self.setup_background(bg)
        
        saved_log_path = self.load_config()
        default_log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        final_log_path = saved_log_path if saved_log_path else default_log_path
        
        self.path_var = tk.StringVar(value=final_log_path)
        self.path_entry = tk.Entry(
            self.root, 
            textvariable=self.path_var, 
            font=("SimHei", 11), 
            bg='#ffffff', 
            relief='flat', 
            bd=0, 
            highlightthickness=1, 
            highlightbackground='#888888', 
            insertbackground='#000000', 
            fg='#1a1a1a'
        )
        self.path_entry.place(x=50, y=105, width=400, height=30)
        
        # 添加Prompt输入框
        default_prompt = "你是一个智能AI助手，帮助用户回答问题"
        # 尝试从配置文件加载保存的prompt
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'prompt' in config:
                        default_prompt = config['prompt']
        except:
            pass
        
        self.prompt_var = tk.StringVar(value=default_prompt)
        self.prompt_entry = tk.Entry(
            self.root, 
            textvariable=self.prompt_var, 
            font=("SimHei", 11), 
            bg='#ffffff', 
            relief='flat', 
            bd=0, 
            highlightthickness=1, 
            highlightbackground='#888888', 
            insertbackground='#000000', 
            fg='#1a1a1a'
        )
        self.prompt_entry.place(x=50, y=185, width=320, height=30)
        
        # 添加加载历史Prompt按钮
        self.load_prompt_button = tk.Button(
            self.root, 
            text="加载历史", 
            command=self.load_history_prompt, 
            font=('SimHei', 10, 'bold'), 
            width=8, 
            bg='#5cb85c', 
            relief='flat', 
            bd=0, 
            highlightthickness=0,
            activebackground='#449d44', 
            fg='#ffffff', 
            cursor='hand2'
        )
        self.load_prompt_button.place(x=380, y=185, width=70, height=30)
        
        # 添加AI回复者名称输入框
        default_ai_name = "L"
        # 尝试从配置文件加载保存的AI名称
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'ai_name' in config:
                        default_ai_name = config['ai_name']
        except:
            pass
        
        self.ai_name_var = tk.StringVar(value=default_ai_name)
        self.ai_name_entry = tk.Entry(
            self.root, 
            textvariable=self.ai_name_var, 
            font=("SimHei", 11), 
            bg='#ffffff', 
            relief='flat', 
            bd=0, 
            highlightthickness=1, 
            highlightbackground='#888888', 
            insertbackground='#000000', 
            fg='#1a1a1a'
        )
        self.ai_name_entry.place(x=50, y=265, width=320, height=30)
        
        self.continue_button = tk.Button(
            self.root, 
            text="继续", 
            command=self.continue_config, 
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
        self.continue_button.place(x=120, y=310)
        
        self.new_start_button = tk.Button(
            self.root, 
            text="新的开始", 
            command=self.new_start_config, 
            font=('SimHei', 12, 'bold'), 
            width=12, 
            bg='#5cb85c', 
            relief='flat', 
            bd=0, 
            highlightthickness=0,
            activebackground='#449d44', 
            fg='#ffffff', 
            cursor='hand2'
        )
        self.new_start_button.place(x=260, y=310)
        
        self.back_button = tk.Button(
            self.root, 
            text="返回上一步", 
            command=self.create_first_config_area, 
            font=('SimHei', 12, 'bold'), 
            width=12, 
            bg='#d9534f', 
            relief='flat', 
            bd=0, 
            highlightthickness=0,
            activebackground='#c9302c', 
            fg='#ffffff', 
            cursor='hand2'
        )
        self.back_button.place(x=215, y=350)
    
    def continue_config(self):
        log_path = self.path_var.get()
        if not os.path.exists(log_path):
            try:
                os.makedirs(log_path)
            except:
                return
        self.save_config(log_path)
        self.show_third_config(log_path)
    
    def new_start_config(self):
        log_path = self.path_var.get()
        self.delete_logs(log_path)
        try:
            if not os.path.exists(log_path):
                os.makedirs(log_path)
        except:
            pass
        self.save_config(log_path)
        self.show_third_config(log_path)
    
    def show_third_config(self, log_path):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.window_height = 350
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        if ConfigGUI._third_bg_cache:
            self.bg_image = ImageTk.PhotoImage(ConfigGUI._third_bg_cache)
            self.background_label = tk.Label(self.root, image=self.bg_image)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        from gui.model_load_gui import ModelLoadGUI
        self.model_load_gui = ModelLoadGUI(
            self.root,
            self._on_model_config_done,
            log_path,
            prompt=self.prompt_var.get() if hasattr(self, 'prompt_var') else "你是一个智能AI助手，帮助用户回答问题",
            ai_name=self.ai_name_var.get() if hasattr(self, 'ai_name_var') else "L"
        )
    
    def _on_model_config_done(self, log_path, asr_loaded, llm_loaded, ai_name="L"):
        if self.on_config_save:
            self.on_config_save(log_path, True, asr_loaded, llm_loaded, ai_name)
