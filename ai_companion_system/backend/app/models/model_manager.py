import torch
import threading
import gc
from typing import Optional, Dict, Any
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

class ModelManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        self._asr_model = None
        self._llm_model = None
        self._asr_lock = threading.Lock()
        self._llm_lock = threading.Lock()
        self._device = self._get_device()
        self._max_memory = self._get_max_memory()
        self._log_path = None
        self._prompt = "你是一个智能AI助手，帮助用户回答问题"
        self._ai_name = "L"
        
        print(f"[Info] 设备检测: {self._device}")
        if self._device == "cuda":
            print(f"[Info] GPU: {torch.cuda.get_device_name(0)}")
            print(f"[Info] 显存: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f}GB")
    
    def set_log_path(self, log_path: str):
        self._log_path = log_path
        if self._llm_model and self._log_path:
            history_file = os.path.join(self._log_path, "llm_history.json")
            self._llm_model.set_history_file(history_file)
    
    def set_prompt(self, prompt: str):
        self._prompt = prompt
        if self._llm_model:
            self._llm_model.set_system_prompt(prompt)
    
    def set_ai_name(self, ai_name: str):
        self._ai_name = ai_name
        if self._llm_model:
            self._llm_model.set_ai_name(ai_name)
    
    def _get_device(self) -> str:
        if torch.cuda.is_available():
            print("[Info] CUDA可用，使用GPU")
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("[Info] MPS可用，使用Apple GPU")
            return "mps"
        print("[Info] 使用CPU")
        return "cpu"
    
    def _get_max_memory(self) -> Dict[str, str]:
        if self._device == "cuda":
            total_memory = torch.cuda.get_device_properties(0).total_memory
            safe_memory = int(total_memory * 0.7)
            max_mem_gb = safe_memory // (1024**3)
            print(f"[Info] 最大显存限制: {max_mem_gb}GB")
            return {0: f"{max_mem_gb}GB"}
        return {}
    
    def get_device(self) -> str:
        return self._device
    
    def clear_cache(self):
        if self._device == "cuda":
            torch.cuda.empty_cache()
        gc.collect()
    
    def load_asr_model(self, model_path: str = None):
        with self._asr_lock:
            if self._asr_model is not None:
                print("[Info] ASR模型已存在，返回现有实例")
                return self._asr_model
            
            try:
                print("[Info] 开始加载ASR模型...")
                self.clear_cache()
                from app.models.asr_model import QwenASRModel
                print("[Info] 创建ASR模型实例...")
                self._asr_model = QwenASRModel(
                    device=self._device,
                    max_memory=self._max_memory
                )
                print("[Info] 初始化ASR模型...")
                self._asr_model.initialize()
                print("[Info] ASR模型加载完成")
                return self._asr_model
            except Exception as e:
                print(f"[Error] 创建ASR模型失败: {e}")
                import traceback
                traceback.print_exc()
                return None
    
    def initialize_asr_model(self):
        with self._asr_lock:
            if self._asr_model is None:
                print("[Error] ASR模型未创建，请先调用load_asr_model")
                return False
            
            try:
                return self._asr_model.initialize()
            except Exception as e:
                print(f"[Error] 初始化ASR模型失败: {e}")
                return False
    
    def load_llm_model(self, model_path: str = None):
        with self._llm_lock:
            if self._llm_model is not None:
                print("[Info] LLM模型已存在，返回现有实例")
                return self._llm_model
            
            try:
                print("[Info] 开始加载LLM模型...")
                self.clear_cache()
                from app.models.qwen_llm import QwenLLMModel
                print("[Info] 创建LLM模型实例...")
                self._llm_model = QwenLLMModel(
                    device=self._device,
                    max_memory=self._max_memory
                )
                
                if self._log_path:
                    history_file = os.path.join(self._log_path, "llm_history.json")
                    self._llm_model.set_history_file(history_file)
                
                self._llm_model.set_ai_name(self._ai_name)
                self._llm_model.set_system_prompt(self._prompt)
                
                print("[Info] 初始化LLM模型...")
                self._llm_model.initialize()
                print("[Info] LLM模型加载完成")
                return self._llm_model
            except Exception as e:
                print(f"[Error] 创建LLM模型失败: {e}")
                import traceback
                traceback.print_exc()
                return None
    
    def initialize_llm_model(self):
        with self._llm_lock:
            if self._llm_model is None:
                print("[Error] LLM模型未创建，请先调用load_llm_model")
                return False
            
            try:
                return self._llm_model.initialize()
            except Exception as e:
                print(f"[Error] 初始化LLM模型失败: {e}")
                return False
    
    def get_asr_model(self):
        with self._asr_lock:
            return self._asr_model
    
    def get_llm_model(self):
        with self._llm_lock:
            return self._llm_model
    
    def unload_asr_model(self):
        with self._asr_lock:
            if self._asr_model is not None:
                del self._asr_model
                self._asr_model = None
                self.clear_cache()
    
    def unload_llm_model(self):
        with self._llm_lock:
            if self._llm_model is not None:
                del self._llm_model
                self._llm_model = None
                self.clear_cache()
    
    def unload_all_models(self):
        self.unload_asr_model()
        self.unload_llm_model()
    
    def get_memory_usage(self) -> Dict[str, Any]:
        result = {
            "device": self._device,
            "asr_loaded": self._asr_model is not None,
            "llm_loaded": self._llm_model is not None
        }
        
        if self._device == "cuda":
            result["gpu_memory_allocated"] = torch.cuda.memory_allocated(0) / (1024**3)
            result["gpu_memory_reserved"] = torch.cuda.memory_reserved(0) / (1024**3)
            result["gpu_memory_total"] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        
        if self._llm_model:
            result["llm_history"] = self._llm_model.get_history_stats()
        
        return result

model_manager = ModelManager()
