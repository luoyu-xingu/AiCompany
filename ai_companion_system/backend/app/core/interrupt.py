import webrtcvad
import numpy as np
import pyaudio
from app.utils.logger import audio_logger
from app.utils.audio import AudioUtils

class InterruptDetector:
    def __init__(self, rate=16000, mode=3):
        """
        初始化打断检测器
        rate: 采样率，必须是8000, 16000, 32000, 48000之一
        mode: 检测模式，0-3，数字越大检测越敏感
        """
        try:
            self.vad = webrtcvad.Vad(mode)
            self.rate = rate
            self.frame_duration = 30  # 30ms
            self.frame_size = int(rate * self.frame_duration / 1000)
            self.channels = 1
            self.format = pyaudio.paInt16
            
            # 音频流
            self.p = pyaudio.PyAudio()
            self.stream = None
            
            # 打断状态
            self.is_interrupting = False
            self.tts_playing = False
            
            # 能量阈值
            self.energy_threshold = 10000
            
            audio_logger.info(f"打断检测器初始化成功，采样率: {rate}, 帧大小: {self.frame_size}")
        except Exception as e:
            audio_logger.error(f"打断检测器初始化失败: {e}")
            self.vad = None
            self.p = None
    
    def start_detection(self, callback):
        """开始打断检测"""
        if not self.vad or not self.p:
            audio_logger.error("打断检测器未初始化")
            return False
        
        try:
            # 打开音频流
            self.stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                output=False,
                frames_per_buffer=self.frame_size,
                stream_callback=lambda in_data, frame_count, time_info, status: self._stream_callback(in_data, frame_count, time_info, status, callback)
            )
            
            self.stream.start_stream()
            audio_logger.info("打断检测已启动")
            return True
        except Exception as e:
            audio_logger.error(f"启动打断检测失败: {e}")
            return False
    
    def stop_detection(self):
        """停止打断检测"""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.p:
                self.p.terminate()
            audio_logger.info("打断检测已停止")
            return True
        except Exception as e:
            audio_logger.error(f"停止打断检测失败: {e}")
            return False
    
    def _stream_callback(self, in_data, frame_count, time_info, status, callback):
        """音频流回调函数"""
        try:
            if not self.tts_playing:
                return (in_data, pyaudio.paContinue)
            
            # 检测语音活动
            is_voice = self.vad.is_speech(in_data, self.rate)
            
            # 计算音频能量
            energy = AudioUtils.calculate_energy(in_data)
            
            # 检测打断
            if is_voice and energy > self.energy_threshold:
                audio_logger.info(f"检测到打断，能量: {energy}")
                self.is_interrupting = True
                if callback:
                    callback()
            
            return (in_data, pyaudio.paContinue)
        except Exception as e:
            audio_logger.error(f"音频流回调失败: {e}")
            return (in_data, pyaudio.paContinue)
    
    def set_tts_playing(self, playing):
        """设置TTS播放状态"""
        self.tts_playing = playing
        if not playing:
            self.is_interrupting = False
        audio_logger.info(f"设置TTS播放状态: {playing}")
    
    def get_interrupt_status(self):
        """获取打断状态"""
        return self.is_interrupting
    
    def reset_interrupt_status(self):
        """重置打断状态"""
        self.is_interrupting = False
        audio_logger.info("打断状态已重置")

class InterruptHandler:
    def __init__(self, tts_module):
        """
        初始化打断处理器
        tts_module: TTS模块实例
        """
        self.tts = tts_module
        self.interrupt_detector = InterruptDetector()
        self.interrupted_text = ""
        self.interrupt_position = 0
        audio_logger.info("打断处理器初始化成功")
    
    def start_interrupt_detection(self):
        """开始打断检测"""
        return self.interrupt_detector.start_detection(self._handle_interrupt)
    
    def stop_interrupt_detection(self):
        """停止打断检测"""
        return self.interrupt_detector.stop_detection()
    
    def _handle_interrupt(self):
        """处理打断"""
        try:
            audio_logger.info("处理打断事件")
            
            # 停止TTS播放
            if self.tts:
                self.tts.stop()
                audio_logger.info("已停止TTS播放")
            
            # 记录打断位置
            # 这里可以根据实际情况记录打断时的文本位置
            
            # 触发打断回调
            if hasattr(self, 'interrupt_callback') and self.interrupt_callback:
                self.interrupt_callback()
                
        except Exception as e:
            audio_logger.error(f"处理打断失败: {e}")
    
    def set_interrupt_callback(self, callback):
        """设置打断回调函数"""
        self.interrupt_callback = callback
        audio_logger.info("打断回调函数已设置")
    
    def set_tts_playing(self, playing):
        """设置TTS播放状态"""
        self.interrupt_detector.set_tts_playing(playing)
    
    def get_interrupt_status(self):
        """获取打断状态"""
        return self.interrupt_detector.get_interrupt_status()
    
    def reset_interrupt_status(self):
        """重置打断状态"""
        self.interrupt_detector.reset_interrupt_status()
        self.interrupted_text = ""
        self.interrupt_position = 0
        audio_logger.info("打断状态已重置")
    
    def handle_interrupted_speech(self, text):
        """处理被打断的 speech"""
        try:
            # 这里可以根据打断位置处理被打断的文本
            # 例如，记录被打断的文本，以便后续处理
            self.interrupted_text = text
            audio_logger.info(f"记录被打断的文本: {text[:50]}...")
            return text
        except Exception as e:
            audio_logger.error(f"处理被打断的 speech 失败: {e}")
            return text
