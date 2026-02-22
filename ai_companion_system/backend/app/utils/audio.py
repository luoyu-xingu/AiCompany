import pyaudio
import numpy as np
from app.utils.logger import audio_logger

class AudioUtils:
    @staticmethod
    def calculate_energy(audio_frame):
        """计算音频能量"""
        try:
            if isinstance(audio_frame, bytes):
                audio_data = np.frombuffer(audio_frame, dtype=np.int16)
            else:
                audio_data = np.array(audio_frame, dtype=np.int16)
            
            energy = np.sum(np.square(audio_data)) / len(audio_data)
            return energy
        except Exception as e:
            audio_logger.error(f"计算音频能量失败: {e}")
            return 0
    
    @staticmethod
    def calculate_speech_rate(audio_data, sample_rate, text_length):
        """计算语速（字符/秒）"""
        try:
            # 计算音频时长
            duration = len(audio_data) / sample_rate
            if duration == 0:
                return 0
            
            # 计算语速
            speech_rate = text_length / duration
            return speech_rate
        except Exception as e:
            audio_logger.error(f"计算语速失败: {e}")
            return 0
    
    @staticmethod
    def convert_audio_format(audio_data, from_format, to_format):
        """转换音频格式"""
        try:
            if from_format == to_format:
                return audio_data
            
            # 这里可以添加不同格式之间的转换逻辑
            audio_logger.info(f"转换音频格式: {from_format} -> {to_format}")
            return audio_data
        except Exception as e:
            audio_logger.error(f"转换音频格式失败: {e}")
            return audio_data
    
    @staticmethod
    def get_audio_devices():
        """获取音频设备列表"""
        try:
            p = pyaudio.PyAudio()
            devices = []
            
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'max_input_channels': device_info['maxInputChannels'],
                    'max_output_channels': device_info['maxOutputChannels']
                })
            
            p.terminate()
            audio_logger.info(f"获取到 {len(devices)} 个音频设备")
            return devices
        except Exception as e:
            audio_logger.error(f"获取音频设备失败: {e}")
            return []
    
    @staticmethod
    def validate_audio_data(audio_data, sample_rate, channels):
        """验证音频数据"""
        try:
            if not audio_data:
                return False, "音频数据为空"
            
            if sample_rate not in [8000, 16000, 32000, 48000]:
                return False, f"不支持的采样率: {sample_rate}"
            
            if channels not in [1, 2]:
                return False, f"不支持的声道数: {channels}"
            
            return True, "音频数据有效"
        except Exception as e:
            audio_logger.error(f"验证音频数据失败: {e}")
            return False, str(e)
