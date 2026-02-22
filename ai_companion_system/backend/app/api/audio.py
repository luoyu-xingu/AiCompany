from fastapi import APIRouter, HTTPException
import numpy as np
from app.core.asr import SpeechRecognizer
from app.core.tts import TextToSpeech
from app.core.emotion import EmotionAnalyzer
from app.core.voice_adjuster import VoiceAdjuster
from app.utils.logger import audio_logger

router = APIRouter()

# 初始化模块
asr = SpeechRecognizer()
tts = TextToSpeech()
emotion_analyzer = EmotionAnalyzer()
voice_adjuster = VoiceAdjuster()

@router.post("/recognize")
async def recognize_speech():
    """语音识别"""
    try:
        audio_logger.info("开始语音识别")
        text = asr.recognize_from_microphone()
        if not text:
            raise HTTPException(status_code=400, detail="无法识别语音")
        return {"text": text}
    except HTTPException:
        raise
    except Exception as e:
        audio_logger.error(f"语音识别失败: {e}")
        raise HTTPException(status_code=500, detail="语音识别失败")

@router.post("/synthesize")
async def synthesize_speech(text: str, emotion: str = "calm"):
    """语音合成"""
    try:
        if not text:
            raise HTTPException(status_code=400, detail="文本不能为空")
        
        # 根据情感调整声音参数
        voice_params = voice_adjuster.adjust_voice_by_emotion(emotion)
        voice_adjuster.set_voice_parameters(tts, voice_params)
        
        audio_logger.info(f"开始语音合成: {text[:50]}...")
        success = tts.speak(text)
        if not success:
            raise HTTPException(status_code=500, detail="语音合成失败")
        
        return {"success": True, "message": "语音合成成功"}
    except HTTPException:
        raise
    except Exception as e:
        audio_logger.error(f"语音合成失败: {e}")
        raise HTTPException(status_code=500, detail="语音合成失败")

@router.post("/analyze-emotion")
async def analyze_emotion(audio_data: list, sample_rate: int):
    """分析音频情感"""
    try:
        if not audio_data:
            raise HTTPException(status_code=400, detail="音频数据不能为空")
        
        # 转换音频数据
        audio_array = np.array(audio_data, dtype=np.float32)
        
        audio_logger.info("开始情感分析")
        emotion, features = emotion_analyzer.analyze_audio(audio_array, sample_rate)
        
        return {"emotion": emotion, "features": features}
    except HTTPException:
        raise
    except Exception as e:
        audio_logger.error(f"情感分析失败: {e}")
        raise HTTPException(status_code=500, detail="情感分析失败")

@router.post("/adjust-voice")
async def adjust_voice(emotion: str, speech_rate: float = 1.0):
    """调整声音参数"""
    try:
        audio_logger.info(f"调整声音参数: 情感={emotion}, 语速={speech_rate}")
        
        # 综合调整声音参数
        voice_params = voice_adjuster.adjust_voice_combined(emotion, speech_rate)
        success = voice_adjuster.set_voice_parameters(tts, voice_params)
        
        if not success:
            raise HTTPException(status_code=500, detail="调整声音参数失败")
        
        return {"success": True, "params": voice_params}
    except HTTPException:
        raise
    except Exception as e:
        audio_logger.error(f"调整声音参数失败: {e}")
        raise HTTPException(status_code=500, detail="调整声音参数失败")
