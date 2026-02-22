import tkinter as tk
import random
import threading
import os
import json
from PIL import Image, ImageTk

# 确保app模块可用
try:
    import app
    from app.core.chat import LocalChatModel
    from app.core.tts import TextToSpeech
    from app.utils.logger import set_log_directory, setup_logger
except ImportError:
    pass

class ChatGUI:
    """聊天GUI界面"""
    def __init__(self, root, log_path):
        """初始化GUI"""
        self.root = root
        self.root.title("AI陪伴系统")
        self.log_path = log_path
        
        # 禁用放大按钮
        self.root.resizable(False, False)
        
        # 窗口大小
        self.window_width = 800
        self.window_height = 500
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        # 设置背景图片
        self.bg_image_path = r"d:\AiCompany\photo1.jpg"
        
        # 先加载原始背景图片
        self.load_background_image()
        
        # 确保日志目录存在
        if not os.path.exists(log_path):
            try:
                os.makedirs(log_path)
            except Exception as e:
                print(f"创建日志目录失败: {e}")
        
        # 更新日志路径
        self.update_log_path(log_path)
        
        # 初始化本地小模型
        try:
            from app.core.chat import LocalChatModel
            self.chat_model = LocalChatModel()
            self.chat_history = []
        except Exception as e:
            # 使用备用的简单模型
            self.chat_model = None
            self.chat_history = []
        
        # 初始化语音输出
        try:
            from app.core.tts import TextToSpeech
            self.tts = TextToSpeech()
            # 设置女声，婉转悠扬，带有情绪
            self.setup_voice_parameters()
        except Exception as e:
            self.tts = None
        
        # 创建主背景
        self.setup_main_background()
        
        # 创建聊天历史区域
        self.create_chat_history_area()
        
        # 创建右侧图片区域
        self.create_right_image_area()
        
        # 创建输入区域
        self.create_input_area()
        
        # 创建控制按钮区域
        self.create_control_area()
        
        # 创建右下角图片区域
        self.create_bottom_right_image_area()
        
        # 绑定回车键发送消息
        self.input_text.bind("<Return>", lambda event: self.send_message())
        
        # 加载之前的聊天历史记录
        self.load_chat_history()
        
        # 如果没有历史记录，显示欢迎消息
        if not self.chat_history:
            welcome_message = "你好，我是L"
            self.display_message("L", welcome_message)
            
            # 确保GUI更新后再播放语音
            self.root.update_idletasks()
            
            # 语音播放欢迎消息（使用线程避免阻塞主线程）
            thread = threading.Thread(target=self.speak_message, args=(welcome_message,))
            thread.daemon = True
            thread.start()
    
    def load_background_image(self):
        """加载背景图片"""
        try:
            self.original_bg_image = Image.open(self.bg_image_path)
            self.original_bg_image = self.original_bg_image.resize(
                (self.window_width, self.window_height), Image.Resampling.LANCZOS
            )
        except Exception as e:
            self.original_bg_image = None
    
    def setup_main_background(self):
        """设置主背景 - 白色背景"""
        self.root.configure(bg='#ffffff')
    
    def create_chat_history_area(self):
        """创建聊天历史区域"""
        # 聊天历史区域位置和大小 - 左3/4
        self.chat_area_x = 10
        self.chat_area_y = 10
        self.chat_area_width = 585
        self.chat_area_height = 340
        
        # 创建Frame作为容器 - 白色背景
        self.chat_frame = tk.Frame(self.root, width=self.chat_area_width, height=self.chat_area_height, bg='#ffffff')
        self.chat_frame.place(x=self.chat_area_x, y=self.chat_area_y)
        self.chat_frame.pack_propagate(False)
        
        # 创建Text控件（不带滚动条）
        self.chat_history_text = tk.Text(
            self.chat_frame, width=70, height=20, 
            font=("SimHei", 12, "bold"), 
            bg='#ffffff', relief='flat', bd=0,
            highlightthickness=0,
            insertbackground='#000000',
            fg='#1a1a1a', padx=10, pady=10,
            wrap=tk.WORD
        )
        self.chat_history_text.place(x=0, y=0, relwidth=0.95, relheight=1)
        
        # 创建滚动条
        self.chat_scrollbar = tk.Scrollbar(self.chat_frame, command=self.chat_history_text.yview)
        self.chat_scrollbar.place(relx=0.95, y=0, relwidth=0.05, relheight=1)
        self.chat_history_text.config(yscrollcommand=self.chat_scrollbar.set)
        
        self.chat_history_text.config(state=tk.DISABLED)
    
    def create_right_image_area(self):
        """创建右侧图片区域"""
        # 右侧图片区域位置和大小 - 右1/4
        self.image_area_x = 605
        self.image_area_y = 10
        self.image_area_width = 185
        self.image_area_height = 340
        
        # 创建Frame - 白色背景
        self.image_frame = tk.Frame(self.root, width=self.image_area_width, height=self.image_area_height, bg='#ffffff')
        self.image_frame.place(x=self.image_area_x, y=self.image_area_y)
        self.image_frame.pack_propagate(False)
        
        # 加载并裁剪photo2.jpg的左半部分
        try:
            photo2_path = r"d:\AiCompany\photo2.jpg"
            original_image = Image.open(photo2_path)
            
            # 裁剪左半部分
            width, height = original_image.size
            left_crop = original_image.crop((0, 0, width // 2, height))
            
            # 保持原图比例，调整到目标宽度
            crop_width, crop_height = left_crop.size
            target_width = self.image_area_width
            target_height = int(crop_height * (target_width / crop_width))
            
            left_crop = left_crop.resize(
                (target_width, target_height), 
                Image.Resampling.LANCZOS
            )
            
            # 转换为PhotoImage
            self.right_image = ImageTk.PhotoImage(left_crop)
            
            # 创建Label显示图片 - 向上顶格
            self.image_label = tk.Label(self.image_frame, image=self.right_image, bg='#ffffff')
            self.image_label.place(x=0, y=0, relwidth=1, relheight=(target_height / self.image_area_height))
        except Exception:
            # 如果加载失败，创建一个占位Label
            self.image_label = tk.Label(
                self.image_frame, 
                text="图片区域", 
                bg='#ffffff', 
                font=("SimHei", 12)
            )
            self.image_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    def create_input_area(self):
        """创建输入区域"""
        # 输入区域位置和大小 - 左3/4
        self.input_area_x = 10
        self.input_area_y = 360
        self.input_area_width = 585
        self.input_area_height = 50
        
        # 创建Frame - 白色背景
        self.input_frame = tk.Frame(self.root, width=self.input_area_width, height=self.input_area_height, bg='#ffffff')
        self.input_frame.place(x=self.input_area_x, y=self.input_area_y)
        self.input_frame.pack_propagate(False)
        
        # 创建输入框
        self.input_text = tk.Entry(
            self.input_frame, width=50, font=("SimHei", 12, "bold"),
            bg='#ffffff', relief='flat', bd=0,
            highlightthickness=1, highlightbackground='#888888',
            insertbackground='#000000', fg='#1a1a1a'
        )
        self.input_text.place(relx=0.02, rely=0.1, relwidth=0.7, relheight=0.8)
        
        # 创建发送按钮
        self.send_button = tk.Button(
            self.input_frame, text="发送", command=self.send_message,
            font=("SimHei", 11, "bold"), width=10, bg='#4a90d9', 
            relief='flat', bd=0, highlightthickness=0,
            activebackground='#357abd', fg='#ffffff', cursor='hand2'
        )
        self.send_button.place(relx=0.75, rely=0.1, relwidth=0.22, relheight=0.8)
    
    def create_control_area(self):
        """创建控制按钮区域"""
        # 控制区域位置和大小 - 左3/4
        self.control_area_x = 10
        self.control_area_y = 420
        self.control_area_width = 585
        self.control_area_height = 50
        
        # 创建Frame - 白色背景
        self.control_frame = tk.Frame(self.root, width=self.control_area_width, height=self.control_area_height, bg='#ffffff')
        self.control_frame.place(x=self.control_area_x, y=self.control_area_y)
        self.control_frame.pack_propagate(False)
        
        # 创建刷新按钮
        self.refresh_button = tk.Button(
            self.control_frame, text="刷新", command=self.refresh_app,
            font=("SimHei", 11, "bold"), width=15, bg='#5cb85c', 
            relief='flat', bd=0, highlightthickness=0,
            activebackground='#449d44', fg='#ffffff', cursor='hand2'
        )
        self.refresh_button.place(relx=0.35, rely=0.1, relwidth=0.3, relheight=0.8)
    
    def create_bottom_right_image_area(self):
        """创建右下角图片区域"""
        # 右下角图片区域位置和大小
        self.bottom_image_area_x = 605
        self.bottom_image_area_y = 350
        self.bottom_image_area_width = 185
        self.bottom_image_area_height = 120
        
        # 创建Frame - 白色背景
        self.bottom_image_frame = tk.Frame(self.root, width=self.bottom_image_area_width, height=self.bottom_image_area_height, bg='#ffffff')
        self.bottom_image_frame.place(x=self.bottom_image_area_x, y=self.bottom_image_area_y)
        self.bottom_image_frame.pack_propagate(False)
        
        # 加载photo3.png并裁剪左上角部分
        try:
            photo3_path = r"d:\AiCompany\photo3.png"
            original_image = Image.open(photo3_path)
            
            # 获取图片尺寸
            width, height = original_image.size
            
            # 裁剪左上角区域（保留小人）
            crop_size = min(width, height) // 2
            top_left_crop = original_image.crop((0, 0, crop_size, crop_size))
            
            # 放大到目标尺寸
            top_left_crop = top_left_crop.resize(
                (self.bottom_image_area_width, self.bottom_image_area_height), 
                Image.Resampling.LANCZOS
            )
            
            # 转换为PhotoImage
            self.bottom_image = ImageTk.PhotoImage(top_left_crop)
            
            # 创建Label显示图片 - 居中
            self.bottom_image_label = tk.Label(self.bottom_image_frame, image=self.bottom_image, bg='#ffffff')
            self.bottom_image_label.place(relx=0.5, rely=0.5, anchor='center')
        except Exception:
            # 如果加载失败，创建一个空占位Label
            self.bottom_image_label = tk.Label(
                self.bottom_image_frame, 
                text="", 
                bg='#ffffff'
            )
            self.bottom_image_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    def setup_voice_parameters(self):
        """设置语音参数，使用女声，婉转悠扬，带有情绪"""
        if self.tts:
            # 设置语速较快，减少停顿
            speed = 1.2
            # 增加音量，确保清晰可闻
            volume = 1.0
            # 尝试找到女声
            voice_id = 0  # 默认使用第一个声音（中文女声）
            try:
                # 尝试获取声音列表
                voices = []
                if hasattr(self.tts, 'voices') and self.tts.voices:
                    voices = self.tts.voices
                elif hasattr(self.tts, 'engine') and self.tts.engine:
                    voices = self.tts.engine.getProperty('voices')
                
                # 尝试找到女声
                for i, voice in enumerate(voices):
                    if '女' in voice.name or 'female' in voice.name.lower() or 'huihui' in voice.name.lower():
                        voice_id = i
                        break
            except Exception:
                pass
            
            # 设置语音参数
            try:
                self.tts.set_parameters(speed=speed, volume=volume, voice_id=voice_id)
            except Exception:
                pass
    
    def speak_message(self, message):
        """语音播放消息"""
        # 确保TTS对象存在
        if not self.tts:
            return False
        
        # 检查TTS引擎状态
        if not hasattr(self.tts, 'engine') or not self.tts.engine:
            return False
        
        try:
            # 直接调用TTS的speak方法
            return self.tts.speak(message)
        except Exception:
            return False
    
    def display_message(self, sender, message):
        """显示消息到聊天历史"""
        self.chat_history_text.config(state=tk.NORMAL)
        self.chat_history_text.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_history_text.config(state=tk.DISABLED)
        self.chat_history_text.see(tk.END)
        
        # 保存到聊天历史
        self.chat_history.append({"sender": sender, "message": message})
        
        # 保存聊天历史到文件
        self.save_chat_history()
    
    def send_message(self):
        """发送消息"""
        user_input = self.input_text.get().strip()
        if not user_input:
            return
        
        # 打断当前语音播放
        if self.tts:
            try:
                self.tts.stop()
            except Exception:
                pass
        
        # 显示用户消息
        self.display_message("远边", user_input)
        
        # 清空输入框
        self.input_text.delete(0, tk.END)
        
        # 获取L的回复
        if self.chat_model:
            try:
                response = self.chat_model.get_response(user_input)
                # 优化回复，添加情感色彩
                enhanced_response = f"{response}希望我的回答能给你带来帮助和温暖。"
            except Exception as e:
                enhanced_response = "抱歉，我暂时无法回答你的问题，请稍后再试。不过请相信，我一直在努力提升自己，希望能更好地帮助你。"
        else:
            # 使用简单的回复
            response = self.get_simple_response(user_input)
            enhanced_response = f"{response}我是你的智能陪伴助手L，随时在这里倾听你的心声。"
        
        # 显示L的回复
        self.display_message("L", enhanced_response)
        
        # 语音播放L的回复（使用线程避免阻塞主线程）
        thread = threading.Thread(target=self.speak_message, args=(enhanced_response,))
        thread.daemon = True
        thread.start()
    
    def get_simple_response(self, user_input):
        """简单的回复生成"""
        # 关键词匹配
        keywords = {
            "greeting": ["你好", "嗨", "哈喽", "早上好", "下午好", "晚上好"],
            "farewell": ["再见", "拜拜", "下次见", "晚安"],
            "thanks": ["谢谢", "多谢", "感谢", "麻烦了"],
            "weather": ["天气", "晴天", "下雨", "下雪", "温度"],
            "hobby": ["爱好", "喜欢", "兴趣", "娱乐"]
        }
        
        # 回复模板
        templates = {
            "greeting": ["你好！很高兴见到你，今天过得怎么样？", "嗨！有什么我可以帮忙的吗？", "你好，最近怎么样呀？"],
            "farewell": ["再见！祝你有愉快的一天！", "拜拜，期待下次和你聊天！", "再见，有需要随时告诉我！"],
            "thanks": ["不客气，能帮到你我很开心！", "没关系，这是我应该做的。", "不用谢，随时可以问我！"],
            "weather": ["今天天气看起来不错呢！", "最近天气变化挺大的，注意增减衣物哦。", "天气真的很重要，影响我们的心情呢。"],
            "hobby": ["你的爱好听起来很有趣！", "我也很喜欢类似的活动呢。", "爱好可以丰富我们的生活，真不错！"],
            "default": ["我理解你的意思。", "这是个有趣的话题。", "我不太确定，我们可以换个话题聊聊。", "能再详细说说吗？"]
        }
        
        # 匹配关键词
        intent = "default"
        for key, word_list in keywords.items():
            for word in word_list:
                if word in user_input:
                    intent = key
                    break
            if intent != "default":
                break
        
        # 生成回复
        return random.choice(templates[intent])
    
    def update_log_path(self, log_path):
        """更新日志路径"""
        try:
            # 导入日志模块
            import app.utils.logger
            
            # 使用set_log_directory函数
            if hasattr(app.utils.logger, 'set_log_directory'):
                app.utils.logger.set_log_directory(log_path)
            elif hasattr(app.utils.logger, 'setup_logger'):
                # 降级处理：重新创建日志记录器
                app.utils.logger.app_logger = app.utils.logger.setup_logger('app', os.path.join(log_path, 'app.log'))
                app.utils.logger.audio_logger = app.utils.logger.setup_logger('audio', os.path.join(log_path, 'audio.log'))
                app.utils.logger.chat_logger = app.utils.logger.setup_logger('chat', os.path.join(log_path, 'chat.log'))
                app.utils.logger.emotion_logger = app.utils.logger.setup_logger('emotion', os.path.join(log_path, 'emotion.log'))
        except Exception:
            pass
    
    def load_chat_history(self):
        """加载聊天历史记录"""
        try:
            # 聊天历史文件路径
            chat_history_file = os.path.join(self.log_path, "chat_history.json")
            
            if os.path.exists(chat_history_file):
                with open(chat_history_file, 'r', encoding='utf-8') as f:
                    self.chat_history = json.load(f)
                
                print(f"[Info] 加载聊天历史记录成功，共{len(self.chat_history)}条记录")
                
                # 显示聊天历史记录
                for record in self.chat_history:
                    sender = record.get('sender', '')
                    message = record.get('message', '')
                    if sender and message:
                        self.chat_history_text.config(state=tk.NORMAL)
                        self.chat_history_text.insert(tk.END, f"{sender}: {message}\n\n")
                        self.chat_history_text.config(state=tk.DISABLED)
                
                # 滚动到底部
                self.chat_history_text.see(tk.END)
            else:
                print(f"[Info] 聊天历史文件不存在: {chat_history_file}")
        except Exception as e:
            print(f"[Error] 加载聊天历史记录失败: {e}")
    
    def save_chat_history(self):
        """保存聊天历史记录"""
        try:
            # 聊天历史文件路径
            chat_history_file = os.path.join(self.log_path, "chat_history.json")
            
            with open(chat_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            
            print(f"[Info] 保存聊天历史记录成功，共{len(self.chat_history)}条记录")
        except Exception as e:
            print(f"[Error] 保存聊天历史记录失败: {e}")
    
    def refresh_app(self):
        """刷新应用"""
        # 打断当前语音播放
        if self.tts:
            try:
                self.tts.stop()
            except Exception:
                pass
        
        # 清空聊天历史
        self.chat_history.clear()
        
        # 清空聊天历史区域
        self.chat_history_text.config(state=tk.NORMAL)
        self.chat_history_text.delete(1.0, tk.END)
        
        # 删除聊天历史文件
        try:
            chat_history_file = os.path.join(self.log_path, "chat_history.json")
            if os.path.exists(chat_history_file):
                os.remove(chat_history_file)
                print(f"[Info] 已删除聊天历史文件: {chat_history_file}")
        except Exception as e:
            print(f"[Error] 删除聊天历史文件失败: {e}")
        
        # 重新显示欢迎消息
        welcome_message = "你好，我是L"
        self.display_message("L", welcome_message)
        
        # 语音播放欢迎消息
        thread = threading.Thread(target=self.speak_message, args=(welcome_message,))
        thread.daemon = True
        thread.start()
