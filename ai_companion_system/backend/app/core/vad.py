import webrtcvad
import numpy as np
import pyaudio
from app.utils.logger import audio_logger

class VoiceActivityDetector:
    def __init__(self, rate=16000, mode=3):
        """
        初始化语音活动检测器
        rate: 采样率，必须是8000, 16000, 32000, 48000之一
        mode: 检测模式，0-3，数字越大检测越敏感
        """
        try:
            self.vad = webrtcvad.Vad(mode)
            self.rate = rate
            self.frame_duration = 30  # 30ms
            self.frame_size = int(rate * self.frame_duration / 1000)
            audio_logger.info(f"VAD初始化成功，采样率: {rate}, 帧大小: {self.frame_size}")
        except Exception as e:
            audio_logger.error(f"VAD初始化失败: {e}")
            self.vad = None
    
    def is_voice(self, audio_frame):
        """检测音频帧是否包含语音"""
        if not self.vad:
            audio_logger.error("VAD未初始化")
            return False
        
        try:
            # 确保音频帧大小正确
            if len(audio_frame) < self.frame_size:
                return False
            
            # 检测语音活动
            return self.vad.is_speech(audio_frame, self.rate)
        except Exception as e:
            audio_logger.error(f"语音活动检测失败: {e}")
            return False
    
    def process_audio_stream(self, audio_data, sample_rate):
        """处理音频流，返回语音活动片段"""
        if not self.vad:
            audio_logger.error("VAD未初始化")
            return []
        
        try:
            # 如果采样率不匹配，需要重采样
            if sample_rate != self.rate:
                audio_logger.warning(f"采样率不匹配: {sample_rate} != {self.rate}")
                # 这里可以添加重采样逻辑
                return []
            
            # 分割音频为帧
            frames = []
            for i in range(0, len(audio_data), self.frame_size):
                frame = audio_data[i:i+self.frame_size]
                if len(frame) == self.frame_size:
                    frames.append(frame)
            
            # 检测每个帧是否包含语音
            voice_frames = []
            for i, frame in enumerate(frames):
                if self.is_voice(frame):
                    voice_frames.append((i * self.frame_duration, (i+1) * self.frame_duration))
            
            audio_logger.info(f"检测到 {len(voice_frames)} 个语音活动片段")
            return voice_frames
        except Exception as e:
            audio_logger.error(f"处理音频流失败: {e}")
            return []
    
    def detect_speech_start(self, audio_data, sample_rate):
        """检测语音开始位置"""
        if not self.vad:
            audio_logger.error("VAD未初始化")
            return -1
        
        try:
            # 如果采样率不匹配，需要重采样
            if sample_rate != self.rate:
                audio_logger.warning(f"采样率不匹配: {sample_rate} != {self.rate}")
                return -1
            
            # 分割音频为帧
            frames = []
            for i in range(0, len(audio_data), self.frame_size):
                frame = audio_data[i:i+self.frame_size]
                if len(frame) == self.frame_size:
                    frames.append(frame)
            
            # 检测语音开始
            for i, frame in enumerate(frames):
                if self.is_voice(frame):
                    start_time = i * self.frame_duration / 1000.0  # 转换为秒
                    audio_logger.info(f"检测到语音开始于: {start_time:.3f}秒")
                    return start_time
            
            audio_logger.info("未检测到语音")
            return -1
        except Exception as e:
            audio_logger.error(f"检测语音开始失败: {e}")
            return -1
