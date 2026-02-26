import tkinter as tk
import random
import threading
import os
import json
from PIL import Image, ImageTk
import numpy as np
import queue
import time

class ChatGUI:
    def __init__(self, root, log_path, mic_enabled=False, asr_loaded=False, llm_loaded=False, ai_name="L"):
        self.root = root
        self.root.title("AI陪伴系统")
        self.log_path = log_path
        self._ai_name = ai_name
        
        self.root.resizable(False, False)
        
        self.window_width = 800
        self.window_height = 500
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        self.bg_image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "photo1.jpg")
        
        self._mic_enabled = mic_enabled
        self._asr_loaded = asr_loaded
        self._llm_loaded = llm_loaded
        
        self._model_manager = None
        self._is_recording = False
        self._recording_thread = None
        self._audio_queue = queue.Queue()
        
        self._tts_playing = False
        self._interrupted = False
        self._current_speech_text = ""
        
        self._emotion_analyzer = None
        self._voice_adjuster = None
        self._interrupt_detector = None
        self._vad = None
        
        self._current_user_emotion = "calm"
        self._current_speech_rate = 1.0
        
        self._init_modules()
        
        self.load_background_image()
        
        if not os.path.exists(log_path):
            try:
                os.makedirs(log_path)
            except Exception as e:
                print(f"创建日志目录失败: {e}")
        
        self.update_log_path(log_path)
        
        self._init_model_manager()
        
        self.chat_history = []
        
        try:
            from app.core.tts import TextToSpeech
            self.tts = TextToSpeech()
            self.setup_voice_parameters()
        except Exception as e:
            self.tts = None
        
        self.setup_main_background()
        
        self.create_chat_history_area()
        
        self.create_right_image_area()
        
        self.create_input_area()
        
        self.create_control_area()
        
        self.create_bottom_right_image_area()
        
        self.create_emotion_indicator()
        

        
        self.load_chat_history()
        
        if not self.chat_history:
            welcome_message = f"你好，我是{self._ai_name}"
            self.display_message(self._ai_name, welcome_message)
            
            self.root.update_idletasks()
            
            thread = threading.Thread(target=self._speak_with_interrupt, args=(welcome_message,))
            thread.daemon = True
            thread.start()
    
    def _init_modules(self):
        try:
            from app.core.emotion import EmotionAnalyzer
            self._emotion_analyzer = EmotionAnalyzer()
            print("[Info] 情感分析模块初始化成功")
        except Exception as e:
            print(f"[Error] 情感分析模块初始化失败: {e}")
        
        try:
            from app.core.voice_adjuster import VoiceAdjuster
            self._voice_adjuster = VoiceAdjuster()
            print("[Info] 声音调节模块初始化成功")
        except Exception as e:
            print(f"[Error] 声音调节模块初始化失败: {e}")
        
        try:
            from app.core.interrupt import InterruptDetector
            self._interrupt_detector = InterruptDetector()
            print("[Info] 打断检测模块初始化成功")
        except Exception as e:
            print(f"[Error] 打断检测模块初始化失败: {e}")
        
        try:
            from app.core.vad import VoiceActivityDetector
            self._vad = VoiceActivityDetector()
            print("[Info] VAD模块初始化成功")
        except Exception as e:
            print(f"[Error] VAD模块初始化失败: {e}")
    
    def _init_model_manager(self):
        try:
            from app.models.model_manager import model_manager
            self._model_manager = model_manager
            self._model_manager.set_log_path(self.log_path)
        except Exception as e:
            print(f"[Error] 初始化模型管理器失败: {e}")
    
    def load_background_image(self):
        try:
            self.original_bg_image = Image.open(self.bg_image_path)
            self.original_bg_image = self.original_bg_image.resize(
                (self.window_width, self.window_height), Image.Resampling.LANCZOS
            )
        except Exception as e:
            self.original_bg_image = None
    
    def setup_main_background(self):
        self.root.configure(bg='#ffffff')
    
    def create_chat_history_area(self):
        self.chat_area_x = 10
        self.chat_area_y = 10
        self.chat_area_width = 585
        self.chat_area_height = 340
        
        self.chat_frame = tk.Frame(self.root, width=self.chat_area_width, height=self.chat_area_height, bg='#ffffff')
        self.chat_frame.place(x=self.chat_area_x, y=self.chat_area_y)
        self.chat_frame.pack_propagate(False)
        
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
        
        self.chat_scrollbar = tk.Scrollbar(self.chat_frame, command=self.chat_history_text.yview)
        self.chat_scrollbar.place(relx=0.95, y=0, relwidth=0.05, relheight=1)
        self.chat_history_text.config(yscrollcommand=self.chat_scrollbar.set)
        
        self.chat_history_text.config(state=tk.DISABLED)
    
    def create_right_image_area(self):
        self.image_area_x = 605
        self.image_area_y = 10
        self.image_area_width = 185
        self.image_area_height = 340
        
        self.image_frame = tk.Frame(self.root, width=self.image_area_width, height=self.image_area_height, bg='#ffffff')
        self.image_frame.place(x=self.image_area_x, y=self.image_area_y)
        self.image_frame.pack_propagate(False)
        
        try:
            photo2_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "photo2.jpg")
            original_image = Image.open(photo2_path)
            
            width, height = original_image.size
            left_crop = original_image.crop((0, 0, width // 2, height))
            
            crop_width, crop_height = left_crop.size
            target_width = self.image_area_width
            target_height = int(crop_height * (target_width / crop_width))
            
            left_crop = left_crop.resize(
                (target_width, target_height), 
                Image.Resampling.LANCZOS
            )
            
            self.right_image = ImageTk.PhotoImage(left_crop)
            
            self.image_label = tk.Label(self.image_frame, image=self.right_image, bg='#ffffff')
            self.image_label.place(x=0, y=0, relwidth=1, relheight=(target_height / self.image_area_height))
        except Exception:
            self.image_label = tk.Label(
                self.image_frame, 
                text="图片区域", 
                bg='#ffffff', 
                font=("SimHei", 12)
            )
            self.image_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    def create_input_area(self):
        self.input_area_x = 10
        self.input_area_y = 400
        self.input_area_width = 585
        self.input_area_height = 60
        
        self.input_frame = tk.Frame(self.root, width=self.input_area_width, height=self.input_area_height, bg='#ffffff')
        self.input_frame.place(x=self.input_area_x, y=self.input_area_y)
        self.input_frame.pack_propagate(False)
        
        self.mic_button = tk.Button(
            self.input_frame, text="🎤", command=self.toggle_recording,
            font=("SimHei", 18), width=5, bg='#5cb85c', 
            relief='flat', bd=0, highlightthickness=0,
            activebackground='#449d44', fg='#ffffff', cursor='hand2'
        )
        self.mic_button.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.2, relheight=0.8)
    
    def create_control_area(self):
        pass
    
    def create_bottom_right_image_area(self):
        self.bottom_image_area_x = 605
        self.bottom_image_area_y = 350
        self.bottom_image_area_width = 185
        self.bottom_image_area_height = 120
        
        self.bottom_image_frame = tk.Frame(self.root, width=self.bottom_image_area_width, height=self.bottom_image_area_height, bg='#ffffff')
        self.bottom_image_frame.place(x=self.bottom_image_area_x, y=self.bottom_image_area_y)
        self.bottom_image_frame.pack_propagate(False)
        
        try:
            photo3_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "photo3.png")
            original_image = Image.open(photo3_path)
            
            width, height = original_image.size
            
            crop_size = min(width, height) // 2
            top_left_crop = original_image.crop((0, 0, crop_size, crop_size))
            
            top_left_crop = top_left_crop.resize(
                (self.bottom_image_area_width, self.bottom_image_area_height), 
                Image.Resampling.LANCZOS
            )
            
            self.bottom_image = ImageTk.PhotoImage(top_left_crop)
            
            self.bottom_image_label = tk.Label(self.bottom_image_frame, image=self.bottom_image, bg='#ffffff')
            self.bottom_image_label.place(relx=0.5, rely=0.5, anchor='center')
        except Exception:
            self.bottom_image_label = tk.Label(
                self.bottom_image_frame, 
                text="", 
                bg='#ffffff'
            )
            self.bottom_image_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    def create_emotion_indicator(self):
        self.emotion_frame = tk.Frame(self.root, width=185, height=30, bg='#ffffff')
        self.emotion_frame.place(x=605, y=470)
        
        self.emotion_label = tk.Label(
            self.emotion_frame,
            text="情感: 平静",
            font=("SimHei", 10),
            bg='#ffffff',
            fg='#666666'
        )
        self.emotion_label.place(relx=0.5, rely=0.5, anchor='center')
    
    def setup_voice_parameters(self):
        if self.tts:
            speed = 1.2
            volume = 1.0
            voice_id = 0
            try:
                voices = []
                if hasattr(self.tts, 'voices') and self.tts.voices:
                    voices = self.tts.voices
                elif hasattr(self.tts, 'engine') and self.tts.engine:
                    voices = self.tts.engine.getProperty('voices')
                
                for i, voice in enumerate(voices):
                    if '女' in voice.name or 'female' in voice.name.lower() or 'huihui' in voice.name.lower():
                        voice_id = i
                        break
            except Exception:
                pass
            
            try:
                self.tts.set_parameters(speed=speed, volume=volume, voice_id=voice_id)
            except Exception:
                pass
    
    def _adjust_voice_by_emotion(self, emotion):
        if self._voice_adjuster and self.tts:
            params = self._voice_adjuster.adjust_voice_by_emotion(emotion)
            self.tts.set_parameters(
                speed=params.get("speed", 1.0),
                pitch=params.get("pitch", 1.0),
                volume=params.get("volume", 1.0)
            )
            print(f"[Info] 根据情感调整声音参数: {params}")
    
    def _adjust_voice_by_speech_rate(self, speech_rate):
        if self._voice_adjuster and self.tts:
            params = self._voice_adjuster.adjust_voice_by_speech_rate(speech_rate)
            self.tts.set_parameters(
                speed=params.get("speed", 1.0),
                pitch=params.get("pitch", 1.0),
                volume=params.get("volume", 1.0)
            )
            print(f"[Info] 根据语速调整声音参数: {params}")
    
    def _adjust_voice_combined(self, emotion, speech_rate):
        if self._voice_adjuster and self.tts:
            params = self._voice_adjuster.adjust_voice_combined(emotion, speech_rate)
            self.tts.set_parameters(
                speed=params.get("speed", 1.0),
                pitch=params.get("pitch", 1.0),
                volume=params.get("volume", 1.0)
            )
            print(f"[Info] 综合调整声音参数: {params}")
    
    def _analyze_emotion(self, audio_data, sample_rate=16000):
        if self._emotion_analyzer:
            try:
                emotion, features = self._emotion_analyzer.analyze_audio(audio_data, sample_rate)
                return emotion, features
            except Exception as e:
                print(f"[Error] 情感分析失败: {e}")
        return "calm", {}
    
    def _update_emotion_indicator(self, emotion):
        emotion_names = {
            "happy": "开心",
            "sad": "难过",
            "angry": "愤怒",
            "anxious": "焦虑",
            "calm": "平静",
            "surprised": "惊讶"
        }
        emotion_text = emotion_names.get(emotion, emotion)
        self.root.after(0, lambda: self.emotion_label.config(text=f"情感: {emotion_text}"))
    
    def _speak_with_interrupt(self, message):
        if not self.tts:
            return False
        
        self._tts_playing = True
        self._current_speech_text = message
        self._interrupted = False
        
        if self._interrupt_detector:
            self._interrupt_detector.set_tts_playing(True)
        
        # 启动打断检测线程
        interrupt_thread = threading.Thread(target=self._monitor_interrupt)
        interrupt_thread.daemon = True
        interrupt_thread.start()
        
        try:
            result = self.tts.speak(message)
        except Exception:
            result = False
        
        self._tts_playing = False
        if self._interrupt_detector:
            self._interrupt_detector.set_tts_playing(False)
        
        return result
    
    def _monitor_interrupt(self):
        """监控用户语音输入，检测打断"""
        try:
            import pyaudio
            
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT,
                           channels=CHANNELS,
                           rate=RATE,
                           input=True,
                           frames_per_buffer=CHUNK)
            
            while self._tts_playing and not self._interrupted:
                data = stream.read(CHUNK, exception_on_overflow=False)
                
                # 使用VAD检测语音活动
                if self._vad:
                    is_voice = self._vad.is_voice(data)
                    if is_voice:
                        # 检测到用户语音，打断TTS播放
                        print("[Info] 检测到用户语音，打断TTS播放")
                        if self.tts:
                            self.tts.stop()
                        self._interrupted = True
                        self._tts_playing = False
                        if self._interrupt_detector:
                            self._interrupt_detector.set_tts_playing(False)
                        break
                
                # 使用打断检测器
                if self._interrupt_detector:
                    audio_chunk = np.frombuffer(data, dtype=np.int16)
                    energy = np.abs(audio_chunk).mean()
                    if energy > 500 and self._interrupt_detector.get_interrupt_status():
                        print("[Info] 打断检测器触发，打断TTS播放")
                        if self.tts:
                            self.tts.stop()
                        self._interrupted = True
                        self._tts_playing = False
                        self._interrupt_detector.set_tts_playing(False)
                        break
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except Exception as e:
            print(f"[Error] 打断监控失败: {e}")
    
    def speak_message(self, message):
        return self._speak_with_interrupt(message)
    
    def test_tts(self):
        """测试TTS功能"""
        test_message = "语音测试，这是一个测试消息"
        print(f"[Info] 测试TTS: {test_message}")
        if self.tts:
            try:
                result = self.tts.speak(test_message)
                print(f"[Info] TTS测试结果: {result}")
            except Exception as e:
                print(f"[Error] TTS测试失败: {e}")
        else:
            print("[Error] TTS未初始化")
    
    def display_message(self, sender, message):
        self.chat_history_text.config(state=tk.NORMAL)
        self.chat_history_text.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_history_text.config(state=tk.DISABLED)
        self.chat_history_text.see(tk.END)
        
        self.chat_history.append({"sender": sender, "message": message})
        
        self.save_chat_history()
    
    def toggle_recording(self):
        if self._is_recording:
            self._is_recording = False
            self.mic_button.config(text="🎤", bg='#5cb85c')
        else:
            self._is_recording = True
            self.mic_button.config(text="⏹", bg='#d9534f')
            
            if self._tts_playing and self.tts:
                self.tts.stop()
                self._interrupted = True
                self._tts_playing = False
                if self._interrupt_detector:
                    self._interrupt_detector.set_tts_playing(False)
            
            self._recording_thread = threading.Thread(target=self._record_audio_vad)
            self._recording_thread.daemon = True
            self._recording_thread.start()
    
    def _record_audio_vad(self):
        try:
            import pyaudio
            
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            
            SILENCE_THRESHOLD = 500
            SILENCE_FRAMES = 25
            
            p = pyaudio.PyAudio()
            
            stream = p.open(format=FORMAT,
                           channels=CHANNELS,
                           rate=RATE,
                           input=True,
                           frames_per_buffer=CHUNK)
            
            frames = []
            silence_count = 0
            has_speech = False
            start_time = time.time()
            
            self.root.after(0, lambda: self.mic_button.config(text="⏹", bg='#d9534f'))
            
            while self._is_recording:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
                
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                energy = np.abs(audio_chunk).mean()
                
                # 使用VAD检测语音活动
                vad_detected = False
                if self._vad:
                    is_voice = self._vad.is_voice(data)
                    if is_voice:
                        has_speech = True
                        silence_count = 0
                        vad_detected = True
                    elif has_speech:
                        silence_count += 1
                
                # 如果VAD不可用或未检测到语音，使用能量检测作为后备
                if not vad_detected:
                    if energy > SILENCE_THRESHOLD:
                        has_speech = True
                        silence_count = 0
                    elif has_speech:
                        silence_count += 1
                
                # 检查是否需要停止录音
                if has_speech and silence_count > SILENCE_FRAMES:
                    break
                
                # 超时保护，最多录音30秒
                if time.time() - start_time > 30:
                    break
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            if frames and has_speech:
                audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                audio_data_float = audio_data.astype(np.float32) / 32768.0
                
                speech_duration = len(audio_data) / RATE
                
                self.root.after(0, lambda: self.mic_button.config(text="识别中...", bg='#f0ad4e'))
                
                emotion, features = self._analyze_emotion(audio_data_float, RATE)
                self._current_user_emotion = emotion
                self._update_emotion_indicator(emotion)
                
                text = self._transcribe_audio(audio_data_float)
                
                if text and speech_duration > 0:
                    text_length = len(text)
                    self._current_speech_rate = text_length / speech_duration
                    # 自动发送识别结果
                    self.send_message(text)
                
            self.root.after(0, lambda: self.mic_button.config(text="🎤", bg='#5cb85c'))
            
        except Exception as e:
            print(f"[Error] 录音失败: {e}")
            self.root.after(0, lambda: self.mic_button.config(text="🎤", bg='#5cb85c'))
    
    def _transcribe_audio(self, audio_data):
        if self._model_manager:
            asr_model = self._model_manager.get_asr_model()
            if asr_model:
                try:
                    return asr_model.transcribe(audio_data)
                except Exception as e:
                    print(f"[Error] ASR识别失败: {e}")
        
        try:
            from app.core.asr import SpeechRecognizer
            recognizer = SpeechRecognizer()
            return recognizer.recognize_from_microphone()
        except Exception as e:
            print(f"[Error] 备用ASR识别失败: {e}")
        
        return ""
    
    def send_message(self, user_input):
        if not user_input:
            return
        
        if self.tts:
            try:
                self.tts.stop()
            except Exception:
                pass
        
        self.display_message("远边", user_input)
        
        self._adjust_voice_combined(self._current_user_emotion, self._current_speech_rate)
        
        response = self._get_llm_response(user_input, self._current_user_emotion)
        
        enhanced_response = f"{response}"
        
        self.display_message(self._ai_name, enhanced_response)
        
        self.root.update_idletasks()
        
        thread = threading.Thread(target=self._speak_with_interrupt, args=(enhanced_response,))
        thread.daemon = True
        thread.start()
    
    def _get_llm_response(self, user_input, emotion=None):
        if self._model_manager:
            llm_model = self._model_manager.get_llm_model()
            if llm_model:
                try:
                    return llm_model.get_response(user_input, emotion)
                except Exception as e:
                    print(f"[Error] LLM回复失败: {e}")
        
        try:
            from app.core.chat import LocalChatModel
            chat_model = LocalChatModel()
            return chat_model.get_response(user_input)
        except Exception as e:
            print(f"[Error] 本地模型回复失败: {e}")
        
        return self.get_simple_response(user_input)
    
    def get_simple_response(self, user_input):
        keywords = {
            "greeting": ["你好", "嗨", "哈喽", "早上好", "下午好", "晚上好"],
            "farewell": ["再见", "拜拜", "下次见", "晚安"],
            "thanks": ["谢谢", "多谢", "感谢", "麻烦了"],
            "weather": ["天气", "晴天", "下雨", "下雪", "温度"],
            "hobby": ["爱好", "喜欢", "兴趣", "娱乐"]
        }
        
        templates = {
            "greeting": ["你好！很高兴见到你，今天过得怎么样？", "嗨！有什么我可以帮忙的吗？", "你好，最近怎么样呀？"],
            "farewell": ["再见！祝你有愉快的一天！", "拜拜，期待下次和你聊天！", "再见，有需要随时告诉我！"],
            "thanks": ["不客气，能帮到你我很开心！", "没关系，这是我应该做的。", "不用谢，随时可以问我！"],
            "weather": ["今天天气看起来不错呢！", "最近天气变化挺大的，注意增减衣物哦。", "天气真的很重要，影响我们的心情呢。"],
            "hobby": ["你的爱好听起来很有趣！", "我也很喜欢类似的活动呢。", "爱好可以丰富我们的生活，真不错！"],
            "default": ["我理解你的意思。", "这是个有趣的话题。", "我不太确定，我们可以换个话题聊聊。", "能再详细说说吗？"]
        }
        
        intent = "default"
        for key, word_list in keywords.items():
            for word in word_list:
                if word in user_input:
                    intent = key
                    break
            if intent != "default":
                break
        
        return random.choice(templates[intent])
    
    def update_log_path(self, log_path):
        try:
            import app.utils.logger
            
            if hasattr(app.utils.logger, 'set_log_directory'):
                app.utils.logger.set_log_directory(log_path)
            elif hasattr(app.utils.logger, 'setup_logger'):
                app.utils.logger.app_logger = app.utils.logger.setup_logger('app', os.path.join(log_path, 'app.log'))
                app.utils.logger.audio_logger = app.utils.logger.setup_logger('audio', os.path.join(log_path, 'audio.log'))
                app.utils.logger.chat_logger = app.utils.logger.setup_logger('chat', os.path.join(log_path, 'chat.log'))
                app.utils.logger.emotion_logger = app.utils.logger.setup_logger('emotion', os.path.join(log_path, 'emotion.log'))
        except Exception:
            pass
    
    def load_chat_history(self):
        try:
            chat_history_file = os.path.join(self.log_path, "chat_history.json")
            
            if os.path.exists(chat_history_file):
                with open(chat_history_file, 'r', encoding='utf-8') as f:
                    self.chat_history = json.load(f)
                
                print(f"[Info] 加载聊天历史记录成功，共{len(self.chat_history)}条记录")
                
                for record in self.chat_history:
                    sender = record.get('sender', '')
                    message = record.get('message', '')
                    if sender and message:
                        self.chat_history_text.config(state=tk.NORMAL)
                        self.chat_history_text.insert(tk.END, f"{sender}: {message}\n\n")
                        self.chat_history_text.config(state=tk.DISABLED)
                
                self.chat_history_text.see(tk.END)
            else:
                print(f"[Info] 聊天历史文件不存在: {chat_history_file}")
        except Exception as e:
            print(f"[Error] 加载聊天历史记录失败: {e}")
    
    def save_chat_history(self):
        try:
            chat_history_file = os.path.join(self.log_path, "chat_history.json")
            
            with open(chat_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            
            print(f"[Info] 保存聊天历史记录成功，共{len(self.chat_history)}条记录")
        except Exception as e:
            print(f"[Error] 保存聊天历史记录失败: {e}")
    
    def refresh_app(self):
        if self.tts:
            try:
                self.tts.stop()
            except Exception:
                pass
        
        self.chat_history.clear()
        
        self.chat_history_text.config(state=tk.NORMAL)
        self.chat_history_text.delete(1.0, tk.END)
        
        try:
            chat_history_file = os.path.join(self.log_path, "chat_history.json")
            if os.path.exists(chat_history_file):
                os.remove(chat_history_file)
                print(f"[Info] 已删除聊天历史文件: {chat_history_file}")
        except Exception as e:
            print(f"[Error] 删除聊天历史文件失败: {e}")
        
        self._current_user_emotion = "calm"
        self._update_emotion_indicator("calm")
        
        welcome_message = f"你好，我是{self._ai_name}"
        self.display_message(self._ai_name, welcome_message)
        
        thread = threading.Thread(target=self._speak_with_interrupt, args=(welcome_message,))
        thread.daemon = True
        thread.start()
