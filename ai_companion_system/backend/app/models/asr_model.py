import torch
import threading
import gc
import os
from typing import Optional, Dict, Any
import numpy as np

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["TRANSFORMERS_CACHE"] = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "model_cache")
os.environ["HF_HOME"] = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "model_cache")

class QwenASRModel:
    def __init__(self, device: str = "cuda", max_memory: Dict = None):
        self._device = device
        self._max_memory = max_memory or {}
        self._model = None
        self._processor = None
        self._tokenizer = None
        self._lock = threading.Lock()
        self._initialized = False
        self._model_name = "openai/whisper-tiny"
        
    def initialize(self):
        if self._initialized:
            return True
        
        with self._lock:
            if self._initialized:
                return True
            
            try:
                print(f"[Info] 正在加载ASR模型: {self._model_name}")
                print(f"[Info] 使用镜像站点: {os.environ.get('HF_ENDPOINT', 'default')}")
                
                from transformers import WhisperProcessor, WhisperForConditionalGeneration
                
                print("[Info] 加载processor...")
                self._processor = WhisperProcessor.from_pretrained(self._model_name)
                
                print("[Info] 加载模型权重...")
                self._model = WhisperForConditionalGeneration.from_pretrained(
                    self._model_name,
                    torch_dtype=torch.float32  # 保持为float32类型，避免类型不匹配
                )
                
                print(f"[Info] 将模型移动到{self._device}...")
                self._model = self._model.to(self._device)
                self._model.eval()
                self._initialized = True
                print(f"[Info] ASR模型加载完成")
                return True
                
            except Exception as e:
                print(f"[Error] ASR模型初始化失败: {e}")
                import traceback
                traceback.print_exc()
                self._initialized = False
                return False
    
    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        if not self._initialized:
            if not self.initialize():
                return ""
        
        with self._lock:
            try:
                if isinstance(audio_data, np.ndarray):
                    if audio_data.dtype == np.int16:
                        audio_data = audio_data.astype(np.float32) / 32768.0
                    audio_tensor = audio_data
                else:
                    audio_tensor = audio_data
                
                inputs = self._processor(
                    audio_tensor,
                    sampling_rate=sample_rate,
                    return_tensors="pt"
                )
                
                if self._device == "cuda":
                    inputs = {k: v.cuda() if hasattr(v, 'cuda') else v for k, v in inputs.items()}
                else:
                    inputs = {k: v.to(self._device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    # 对于Whisper模型，使用language和task参数而不是forced_decoder_ids
                    # 避免重复创建ForceTokensLogitsProcessor
                    predicted_ids = self._model.generate(
                        **inputs,
                        language="chinese",
                        task="transcribe"
                    )
                
                result = self._processor.batch_decode(
                    predicted_ids,
                    skip_special_tokens=True
                )[0]
                
                return result.strip()
                
            except Exception as e:
                print(f"[Error] 语音识别失败: {e}")
                return ""
    
    def transcribe_file(self, audio_file: str) -> str:
        try:
            import librosa
            audio_data, sample_rate = librosa.load(audio_file, sr=16000)
            return self.transcribe(audio_data, sample_rate)
        except Exception as e:
            print(f"[Error] 音频文件识别失败: {e}")
            return ""
    
    def is_initialized(self) -> bool:
        return self._initialized
    
    def get_device(self) -> str:
        return self._device
    
    def clear_cache(self):
        if self._device == "cuda":
            torch.cuda.empty_cache()
        gc.collect()
    
    def unload(self, cleanup: bool = True):
        if self._model is not None:
            del self._model
            self._model = None
        if self._processor is not None:
            del self._processor
            self._processor = None
        if self._tokenizer is not None:
            del self._tokenizer
            self._tokenizer = None
        if cleanup:
            self.clear_cache()
        self._initialized = False
    
    def __del__(self):
        self.unload(cleanup=True)
