import pyttsx3
import threading

class SimpleLogger:
    def info(self, message):
        pass
    def error(self, message):
        pass
    def warning(self, message):
        pass

try:
    from app.utils.logger import audio_logger
except Exception:
    audio_logger = SimpleLogger()

_tts_lock = threading.Lock()

class TextToSpeech:
    _instance = None
    _instance_lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        self.voices = []
        self.rate = 200
        self.volume = 1.0
        self._current_engine = None
        self._current_engine_lock = threading.Lock()
        self._speed = 1.0
        self._pitch = 1.0
        self._volume = 1.0
        self._voice_id = 0
        self._engine_pool = []
        self._engine_pool_lock = threading.Lock()
        self._init_voices()
    
    def _init_voices(self):
        """初始化声音列表"""
        try:
            engine = self._get_or_create_engine()
            if engine:
                self.voices = engine.getProperty('voices')
                self.rate = engine.getProperty('rate')
                self.volume = engine.getProperty('volume')
        except Exception:
            self.voices = []
    
    def _get_or_create_engine(self):
        """获取或创建引擎实例"""
        try:
            print("[TTS] _get_or_create_engine")
            with self._engine_pool_lock:
                if self._engine_pool:
                    print(f"[TTS] 从池中获取引擎: {len(self._engine_pool)}个")
                    return self._engine_pool.pop()
            
            print("[TTS] 初始化新引擎")
            engine = pyttsx3.init()
            print(f"[TTS] 引擎初始化成功: {engine}")
            return engine
        except Exception as e:
            print(f"[TTS] 引擎初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _return_engine(self, engine):
        """归还引擎实例到池中"""
        if engine:
            try:
                with self._engine_pool_lock:
                    if len(self._engine_pool) < 3:
                        self._engine_pool.append(engine)
                    else:
                        del engine
            except Exception:
                pass
    
    @property
    def engine(self):
        """获取引擎实例"""
        return self._get_or_create_engine()
    
    def set_parameters(self, speed=1.0, pitch=1.0, volume=1.0, voice_id=None):
        """设置TTS参数（保存参数，在播放时应用）"""
        try:
            self._speed = speed
            self._pitch = pitch
            self._volume = volume
            self._voice_id = voice_id
            return True
        except Exception:
            return False
    
    def _apply_parameters(self, engine):
        """将保存的参数应用到引擎"""
        if not engine:
            return
        
        try:
            speed = getattr(self, '_speed', 1.0)
            volume = getattr(self, '_volume', 1.0)
            voice_id = getattr(self, '_voice_id', None)
            
            new_rate = int(self.rate * speed)
            engine.setProperty('rate', new_rate)
            
            new_volume = max(0.0, min(1.0, self.volume * volume))
            engine.setProperty('volume', new_volume)
            
            if voice_id is not None and self.voices and 0 <= voice_id < len(self.voices):
                engine.setProperty('voice', self.voices[voice_id].id)
        except Exception:
            pass
    
    def speak(self, text, callback=None):
        """播放语音"""
        print(f"[TTS] 播放语音: {text}")
        if not text:
            print("[TTS] 文本为空")
            return True
        
        try:
            print("[TTS] 直接初始化引擎")
            engine = pyttsx3.init()
            print(f"[TTS] 引擎初始化成功: {engine}")
            
            print("[TTS] 设置属性")
            engine.setProperty('rate', int(self.rate * self._speed))
            engine.setProperty('volume', min(1.0, self.volume * self._volume))
            
            if self.voices and self._voice_id is not None and 0 <= self._voice_id < len(self.voices):
                print(f"[TTS] 设置语音: {self._voice_id}")
                engine.setProperty('voice', self.voices[self._voice_id].id)
            
            print("[TTS] 播放语音")
            engine.say(text)
            engine.runAndWait()
            print("[TTS] 播放完成")
            
            engine.stop()
            del engine
            
            if callback:
                try:
                    callback()
                except Exception:
                    pass
            
            print("[TTS] 返回True")
            return True
        except Exception as e:
            print(f"[TTS] 异常: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def stop(self):
        """停止播放"""
        try:
            with self._current_engine_lock:
                if self._current_engine:
                    try:
                        self._current_engine.stop()
                    except Exception:
                        pass
                    finally:
                        self._current_engine = None
            
            return True
        except Exception:
            return False
    
    def save_to_file(self, text, file_path):
        """保存语音到文件"""
        if not text:
            return False
            
        with _tts_lock:
            engine = None
            try:
                engine = self._get_or_create_engine()
                if not engine:
                    return False
                    
                self._apply_parameters(engine)
                engine.save_to_file(text, file_path)
                engine.runAndWait()
                return True
            except Exception:
                return False
            finally:
                if engine:
                    self._return_engine(engine)
