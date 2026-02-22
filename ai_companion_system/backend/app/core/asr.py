import speech_recognition as sr

class SimpleLogger:
    def info(self, message):
        pass
    def warning(self, message):
        pass
    def error(self, message):
        pass

try:
    from app.utils.logger import audio_logger
except Exception:
    audio_logger = SimpleLogger()

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
    
    def recognize_from_microphone(self, timeout=5, phrase_time_limit=10):
        """从麦克风识别语音"""
        try:
            with self.microphone as source:
                # 调整环境噪音
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # 监听语音输入
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                # 使用Google Web Speech API识别
                text = self.recognizer.recognize_google(audio, language="zh-CN")
                return text
                
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""
        except Exception:
            return ""
    
    def recognize_from_audio_file(self, audio_file):
        """从音频文件识别语音"""
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                
                # 使用Google Web Speech API识别
                text = self.recognizer.recognize_google(audio, language="zh-CN")
                return text
                
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""
        except Exception:
            return ""
