import librosa
import numpy as np
from app.utils.logger import emotion_logger

class EmotionAnalyzer:
    def __init__(self):
        # 情感分类映射
        self.emotions = {
            "happy": "开心",
            "sad": "难过",
            "angry": "愤怒",
            "anxious": "焦虑",
            "calm": "平静",
            "surprised": "惊讶"
        }
        emotion_logger.info("情感分析器初始化成功")
    
    def extract_features(self, audio_data, sample_rate):
        """提取音频情感特征"""
        try:
            # 计算基频
            f0, _ = librosa.piptrack(y=audio_data, sr=sample_rate)
            f0 = f0[f0 > 0]
            
            # 计算能量
            energy = librosa.feature.rms(y=audio_data)[0]
            
            # 提取频谱特征
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)[0]
            
            # 提取语速特征（简化处理）
            speech_rate = len(audio_data) / sample_rate
            
            # 提取零交叉率
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y=audio_data)[0]
            
            features = {
                'f0_mean': np.mean(f0) if len(f0) > 0 else 0,
                'f0_std': np.std(f0) if len(f0) > 0 else 0,
                'f0_max': np.max(f0) if len(f0) > 0 else 0,
                'f0_min': np.min(f0) if len(f0) > 0 else 0,
                'energy_mean': np.mean(energy),
                'energy_std': np.std(energy),
                'energy_max': np.max(energy),
                'spectral_centroid': np.mean(spectral_centroid),
                'spectral_bandwidth': np.mean(spectral_bandwidth),
                'zero_crossing_rate': np.mean(zero_crossing_rate),
                'speech_rate': speech_rate
            }
            
            emotion_logger.info("成功提取音频情感特征")
            return features
        except Exception as e:
            emotion_logger.error(f"提取音频情感特征失败: {e}")
            return {}
    
    def recognize_emotion(self, features):
        """识别情感"""
        try:
            if not features:
                emotion_logger.warning("特征为空，返回默认情感")
                return "calm"
            
            # 基于特征的简单情感分类（实际应用中应使用机器学习模型）
            
            # 开心：高基频，高能量，快速语速
            if features['energy_mean'] > 0.1 and features['f0_std'] > 50 and features['speech_rate'] > 0.5:
                emotion = "happy"
            # 难过：低基频，低能量，慢速语速
            elif features['energy_mean'] < 0.05 and features['f0_mean'] < 150 and features['speech_rate'] < 0.3:
                emotion = "sad"
            # 愤怒：高基频，高能量，快速语速
            elif features['energy_mean'] > 0.15 and features['f0_mean'] > 200 and features['speech_rate'] > 0.6:
                emotion = "angry"
            # 焦虑：高基频变化，中等能量
            elif features['f0_std'] > 80 and features['energy_mean'] > 0.08 and features['energy_std'] > 0.05:
                emotion = "anxious"
            # 惊讶：高基频，能量突然增加
            elif features['f0_max'] > 250 and features['energy_max'] > 0.2:
                emotion = "surprised"
            # 平静：中等基频，稳定能量
            else:
                emotion = "calm"
            
            emotion_logger.info(f"识别到情感: {self.emotions.get(emotion, emotion)}")
            return emotion
        except Exception as e:
            emotion_logger.error(f"识别情感失败: {e}")
            return "calm"
    
    def analyze_audio(self, audio_data, sample_rate):
        """分析音频情感"""
        try:
            # 提取特征
            features = self.extract_features(audio_data, sample_rate)
            
            # 识别情感
            emotion = self.recognize_emotion(features)
            
            return emotion, features
        except Exception as e:
            emotion_logger.error(f"分析音频情感失败: {e}")
            return "calm", {}
    
    def analyze_text(self, text):
        """分析文本情感（简化版）"""
        try:
            # 关键词匹配
            positive_words = ["开心", "高兴", "快乐", "兴奋", "喜悦", "满意", "喜欢"]
            negative_words = ["难过", "伤心", "悲伤", "愤怒", "生气", "焦虑", "担心", "害怕"]
            surprised_words = ["惊讶", "震惊", "意外", "没想到"]
            
            positive_count = sum(1 for word in positive_words if word in text)
            negative_count = sum(1 for word in negative_words if word in text)
            surprised_count = sum(1 for word in surprised_words if word in text)
            
            if surprised_count > 0:
                emotion = "surprised"
            elif positive_count > negative_count:
                emotion = "happy"
            elif negative_count > positive_count:
                # 根据具体词语判断是难过还是愤怒
                angry_words = ["愤怒", "生气"]
                angry_count = sum(1 for word in angry_words if word in text)
                if angry_count > 0:
                    emotion = "angry"
                else:
                    emotion = "sad"
            else:
                emotion = "calm"
            
            emotion_logger.info(f"文本情感分析结果: {self.emotions.get(emotion, emotion)}")
            return emotion
        except Exception as e:
            emotion_logger.error(f"分析文本情感失败: {e}")
            return "calm"
