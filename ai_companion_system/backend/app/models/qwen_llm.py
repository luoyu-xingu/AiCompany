import torch
import threading
import gc
import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["TRANSFORMERS_CACHE"] = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "model_cache")
os.environ["HF_HOME"] = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "model_cache")

class QwenLLMModel:
    def __init__(self, device: str = "cuda", max_memory: Dict = None):
        self._device = device
        self._max_memory = max_memory or {}
        self._model = None
        self._tokenizer = None
        self._lock = threading.Lock()
        self._initialized = False
        self._model_name = "Qwen/Qwen2.5-0.5B-Instruct"
        self._history = []
        self._max_history = 50
        self._system_prompt = "你是一个智能AI陪伴助手，专注于提供自然、流畅的语音交互体验。请始终以自然、友好的方式与用户交流，确保对话体验流畅自然，如同与真人交流一般。回答要简洁明了，适合语音播放。你要记住，你的回答应该充满同理心，能够理解用户的情感状态，并根据用户的情绪调整你的回应方式。"
        
        self._history_file = None
        self._chat_history_file = None
        self._max_history_size = 1 * 1024 * 1024 * 1024
        self._cleanup_size = 512 * 1024 * 1024
        self._ai_name = "L"
        
    def set_history_file(self, file_path: str):
        self._history_file = file_path
        
        log_dir = os.path.dirname(file_path)
        self._chat_history_file = os.path.join(log_dir, "chat_history.json")
        
        self._load_history_from_chat()
        self._check_and_cleanup_history()
    
    def _load_history_from_chat(self):
        if self._chat_history_file and os.path.exists(self._chat_history_file):
            try:
                with open(self._chat_history_file, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                
                self._history = []
                for item in chat_data:
                    sender = item.get("sender", "")
                    message = item.get("message", "")
                    
                    if sender == "远边":
                        self._history.append({
                            "role": "user",
                            "content": message,
                            "timestamp": item.get("timestamp", datetime.now().isoformat())
                        })
                    elif sender == self._ai_name:
                        self._history.append({
                            "role": "assistant",
                            "content": message,
                            "timestamp": item.get("timestamp", datetime.now().isoformat())
                        })
                
                print(f"[Info] 从chat_history.json加载历史记录: {len(self._history)}条")
                return
                
            except Exception as e:
                print(f"[Error] 从chat_history.json加载历史记录失败: {e}")
        
        if self._history_file and os.path.exists(self._history_file):
            try:
                with open(self._history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._history = data.get("history", [])
                    print(f"[Info] 从llm_history.json加载历史记录: {len(self._history)}条")
            except Exception as e:
                print(f"[Error] 加载历史聊天记录失败: {e}")
                self._history = []
    
    def _save_history(self):
        if not self._history_file:
            return
        
        try:
            os.makedirs(os.path.dirname(self._history_file), exist_ok=True)
            
            data = {
                "history": self._history,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self._history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Error] 保存历史聊天记录失败: {e}")
    
    def _get_history_file_size(self) -> int:
        total_size = 0
        
        if self._chat_history_file and os.path.exists(self._chat_history_file):
            try:
                total_size += os.path.getsize(self._chat_history_file)
            except Exception:
                pass
        
        if self._history_file and os.path.exists(self._history_file):
            try:
                total_size += os.path.getsize(self._history_file)
            except Exception:
                pass
        
        return total_size
    
    def _check_and_cleanup_history(self):
        file_size = self._get_history_file_size()
        
        if file_size > self._max_history_size:
            print(f"[Info] 历史记录文件大小: {file_size / (1024*1024):.2f}MB，超过1GB，开始清理...")
            self._cleanup_old_history()
    
    def _cleanup_old_history(self):
        try:
            target_size = self._max_history_size - self._cleanup_size
            
            while self._get_history_file_size() > target_size and len(self._history) > 2:
                if len(self._history) >= 2:
                    self._history.pop(0)
                    self._history.pop(0)
                else:
                    break
                
                self._save_history()
            
            print(f"[Info] 清理完成，当前历史记录: {len(self._history)}条")
            
        except Exception as e:
            print(f"[Error] 清理历史记录失败: {e}")
        
    def initialize(self):
        if self._initialized:
            return True
        
        with self._lock:
            if self._initialized:
                return True
            
            try:
                print(f"[Info] 正在加载LLM模型: {self._model_name}")
                print(f"[Info] 使用镜像站点: {os.environ.get('HF_ENDPOINT', 'default')}")
                
                from transformers import AutoModelForCausalLM, AutoTokenizer
                
                print("[Info] 加载tokenizer...")
                self._tokenizer = AutoTokenizer.from_pretrained(
                    self._model_name,
                    trust_remote_code=True,
                    use_fast=True
                )
                
                print("[Info] 加载模型权重...")
                load_kwargs = {
                    "trust_remote_code": True,
                }
                
                if self._device == "cuda":
                    load_kwargs["torch_dtype"] = torch.float16
                else:
                    load_kwargs["torch_dtype"] = torch.float32
                
                self._model = AutoModelForCausalLM.from_pretrained(
                    self._model_name,
                    **load_kwargs
                )
                
                print(f"[Info] 将模型移动到{self._device}...")
                self._model = self._model.to(self._device)
                
                self._model.eval()
                self._initialized = True
                print(f"[Info] LLM模型加载完成")
                return True
                
            except Exception as e:
                print(f"[Error] LLM模型初始化失败: {e}")
                import traceback
                traceback.print_exc()
                self._initialized = False
                return False
    
    def get_response(self, user_input: str, emotion: str = None) -> str:
        if not self._initialized:
            if not self.initialize():
                return "抱歉，模型暂时无法加载，请稍后再试。"
        
        with self._lock:
            try:
                self._history.append({"role": "user", "content": user_input, "timestamp": datetime.now().isoformat()})
                
                messages = [{"role": "system", "content": self._system_prompt}]
                
                if emotion:
                    emotion_desc = {
                        "happy": "开心",
                        "sad": "难过",
                        "angry": "愤怒",
                        "anxious": "焦虑",
                        "calm": "平静",
                        "surprised": "惊讶"
                    }.get(emotion, emotion)
                    messages[0]["content"] += f"\n用户当前情感状态: {emotion_desc}"
                
                for item in self._history:
                    messages.append({"role": item["role"], "content": item["content"]})
                
                text = self._tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
                
                inputs = self._tokenizer([text], return_tensors="pt")
                
                if self._device == "cuda":
                    inputs = {k: v.cuda() if hasattr(v, 'cuda') else v for k, v in inputs.items()}
                else:
                    inputs = {k: v.to(self._device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    outputs = self._model.generate(
                        **inputs,
                        max_new_tokens=256,
                        do_sample=True,
                        temperature=0.7,
                        top_p=0.9,
                        pad_token_id=self._tokenizer.eos_token_id
                    )
                
                response = self._tokenizer.decode(
                    outputs[0][inputs["input_ids"].shape[1]:],
                    skip_special_tokens=True
                )
                
                self._history.append({"role": "assistant", "content": response, "timestamp": datetime.now().isoformat()})
                
                if len(self._history) > self._max_history * 2:
                    self._history = self._history[-self._max_history * 2:]
                
                self._save_history()
                self._check_and_cleanup_history()
                
                return response.strip()
                
            except Exception as e:
                print(f"[Error] 生成回复失败: {e}")
                return "抱歉，我暂时无法回答，请稍后再试。"
    
    def set_system_prompt(self, prompt: str) -> bool:
        try:
            self._system_prompt = prompt
            return True
        except Exception:
            return False
    
    def set_ai_name(self, ai_name: str) -> bool:
        try:
            self._ai_name = ai_name
            return True
        except Exception:
            return False
    
    def clear_history(self):
        self._history.clear()
        self._save_history()
    
    def get_history(self) -> List[Dict[str, str]]:
        return self._history.copy()
    
    def get_history_stats(self) -> Dict[str, Any]:
        return {
            "count": len(self._history),
            "file_size": self._get_history_file_size(),
            "file_size_mb": self._get_history_file_size() / (1024 * 1024),
            "chat_history_file": self._chat_history_file,
            "llm_history_file": self._history_file
        }
    
    def is_initialized(self) -> bool:
        return self._initialized
    
    def get_device(self) -> str:
        return self._device
    
    def clear_cache(self):
        if self._device == "cuda":
            torch.cuda.empty_cache()
        gc.collect()
    
    def __del__(self):
        if self._model is not None:
            del self._model
        if self._tokenizer is not None:
            del self._tokenizer
        self.clear_cache()
