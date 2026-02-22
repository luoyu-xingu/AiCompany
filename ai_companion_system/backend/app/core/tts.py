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
    def __init__(self):
        self.voices = []
        self.rate = 200
        self.volume = 1.0
        self._current_engine = None
        self._current_engine_lock = threading.Lock()
        # 初始化声音列表
        self._init_voices()
    
    def _init_voices(self):
        """初始化声音列表"""
        try:
            engine = pyttsx3.init(driverName=None)
            self.voices = engine.getProperty('voices')
            self.rate = engine.getProperty('rate')
            self.volume = engine.getProperty('volume')
            del engine  # 释放引擎资源
        except Exception:
            self.voices = []
    
    @property
    def engine(self):
        """每次访问时创建新的引擎实例，解决多线程问题"""
        try:
            return pyttsx3.init(driverName=None)
        except Exception:
            return None
    
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
            
            if voice_id is not None and 0 <= voice_id < len(self.voices):
                engine.setProperty('voice', self.voices[voice_id].id)
        except Exception:
            pass
    
    def speak(self, text, callback=None):
        """播放语音"""
        if not text:
            return True
        
        with _tts_lock:
            try:
                engine = pyttsx3.init(driverName=None)
                
                # 保存当前引擎实例
                with self._current_engine_lock:
                    self._current_engine = engine
                
                self._apply_parameters(engine)
                engine.say(text)
                engine.runAndWait()
                
                # 播放完成后清空当前引擎实例
                with self._current_engine_lock:
                    self._current_engine = None
                
                if callback:
                    try:
                        callback()
                    except Exception:
                        pass
                
                return True
            except Exception:
                # 发生异常时也清空当前引擎实例
                with self._current_engine_lock:
                    self._current_engine = None
                return False
    
    def stop(self):
        """停止播放"""
        try:
            # 停止当前正在运行的引擎实例
            with self._current_engine_lock:
                if self._current_engine:
                    try:
                        self._current_engine.stop()
                    except Exception:
                        pass
                    finally:
                        # 清空当前引擎实例
                        self._current_engine = None
            
            return True
        except Exception:
            return False
    
    def save_to_file(self, text, file_path):
        """保存语音到文件"""
        if not text:
            return False
            
        with _tts_lock:
            try:
                engine = pyttsx3.init(driverName=None)
                self._apply_parameters(engine)
                engine.save_to_file(text, file_path)
                engine.runAndWait()
                return True
            except Exception:
                return False
