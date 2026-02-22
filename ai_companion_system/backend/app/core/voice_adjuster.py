from app.utils.logger import audio_logger

class VoiceAdjuster:
    def __init__(self):
        # 情感对应的声音参数
        self.emotion_voice_params = {
            "happy": {
                "speed": 1.1,
                "pitch": 1.1,
                "volume": 1.0,
                "style": "energetic"
            },
            "sad": {
                "speed": 0.9,
                "pitch": 0.9,
                "volume": 0.9,
                "style": "gentle"
            },
            "angry": {
                "speed": 1.0,
                "pitch": 1.0,
                "volume": 1.0,
                "style": "calm"
            },
            "anxious": {
                "speed": 1.0,
                "pitch": 1.0,
                "volume": 1.0,
                "style": "reassuring"
            },
            "calm": {
                "speed": 1.0,
                "pitch": 1.0,
                "volume": 1.0,
                "style": "friendly"
            },
            "surprised": {
                "speed": 1.1,
                "pitch": 1.1,
                "volume": 1.0,
                "style": "energetic"
            }
        }
        
        # 语速映射
        self.speech_rate_mapping = {
            "slow": 0.8,
            "normal": 1.0,
            "fast": 1.2
        }
        
        audio_logger.info("声音调节器初始化成功")
    
    def adjust_voice_by_emotion(self, emotion):
        """根据情感调整声音参数"""
        try:
            # 获取对应情感的参数，如果没有则使用默认参数
            params = self.emotion_voice_params.get(emotion, self.emotion_voice_params["calm"])
            audio_logger.info(f"根据情感 {emotion} 调整声音参数: {params}")
            return params
        except Exception as e:
            audio_logger.error(f"根据情感调整声音参数失败: {e}")
            return self.emotion_voice_params["calm"]
    
    def adjust_voice_by_speech_rate(self, user_speech_rate):
        """根据用户语速调整声音参数"""
        try:
            # 根据用户语速选择合适的AI语速
            if user_speech_rate < 2:
                speed = self.speech_rate_mapping["slow"]
            elif user_speech_rate > 3:
                speed = self.speech_rate_mapping["fast"]
            else:
                speed = self.speech_rate_mapping["normal"]
            
            params = {
                "speed": speed,
                "pitch": 1.0,
                "volume": 1.0,
                "style": "friendly"
            }
            
            audio_logger.info(f"根据用户语速 {user_speech_rate:.2f} 字符/秒 调整声音参数: {params}")
            return params
        except Exception as e:
            audio_logger.error(f"根据语速调整声音参数失败: {e}")
            return {"speed": 1.0, "pitch": 1.0, "volume": 1.0, "style": "friendly"}
    
    def adjust_voice_combined(self, emotion, user_speech_rate):
        """综合情感和语速调整声音参数"""
        try:
            # 获取情感对应的参数
            emotion_params = self.adjust_voice_by_emotion(emotion)
            
            # 获取语速对应的参数
            speech_rate_params = self.adjust_voice_by_speech_rate(user_speech_rate)
            
            # 综合调整，优先考虑情感，然后调整语速
            combined_params = {
                "speed": speech_rate_params["speed"],
                "pitch": emotion_params["pitch"],
                "volume": emotion_params["volume"],
                "style": emotion_params["style"]
            }
            
            audio_logger.info(f"综合调整声音参数: {combined_params}")
            return combined_params
        except Exception as e:
            audio_logger.error(f"综合调整声音参数失败: {e}")
            return {"speed": 1.0, "pitch": 1.0, "volume": 1.0, "style": "friendly"}
    
    def set_voice_parameters(self, tts_engine, params):
        """设置TTS引擎的声音参数"""
        try:
            if not tts_engine:
                audio_logger.error("TTS引擎未初始化")
                return False
            
            # 设置参数
            success = tts_engine.set_parameters(
                speed=params.get("speed", 1.0),
                pitch=params.get("pitch", 1.0),
                volume=params.get("volume", 1.0)
                # style参数可能需要额外处理，取决于TTS引擎的支持情况
            )
            
            if success:
                audio_logger.info(f"成功设置声音参数: {params}")
            else:
                audio_logger.error("设置声音参数失败")
            
            return success
        except Exception as e:
            audio_logger.error(f"设置声音参数失败: {e}")
            return False
