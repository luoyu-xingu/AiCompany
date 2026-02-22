import requests
import json

class DoubaoChatModel:
    def __init__(self):
        # 豆包API配置
        try:
            from app.models.config import settings
            self.api_key = settings.doubao_api_key
            self.model = settings.doubao_model
        except Exception:
            self.api_key = ""
            self.model = "ep-20240919180602-xqx9p"
        
        self.api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        
        # 对话历史
        self.history = []
        
        # 系统提示词
        self.system_prompt = "你是一个智能AI陪伴助手，专注于提供自然、流畅的语音交互体验。请始终以自然、友好的方式与用户交流，确保对话体验流畅自然，如同与真人交流一般。"
    
    def add_to_history(self, role, content):
        """添加对话历史"""
        self.history.append({"role": role, "content": content})
        # 限制历史长度，避免API调用失败
        if len(self.history) > 10:
            self.history = self.history[-10:]
    
    def clear_history(self):
        """清空对话历史"""
        self.history.clear()
    
    def get_response(self, user_input, emotion=None):
        """获取豆包模型的回复"""
        try:
            # 添加用户输入到历史
            self.add_to_history("user", user_input)
            
            # 构建请求数据
            messages = [
                {"role": "system", "content": self.system_prompt}
            ] + self.history
            
            # 如果有情感信息，添加到系统提示中
            if emotion:
                messages[0]["content"] += f"\n用户当前情感状态: {emotion}"
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            # 发送请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(data),
                timeout=30
            )
            
            # 处理响应
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    response_content = result["choices"][0]["message"]["content"]
                    
                    # 添加回复到历史
                    self.add_to_history("assistant", response_content)
                    
                    return response_content
                else:
                    return "抱歉，我没听清楚，能再重复一遍吗？"
            else:
                return "抱歉，我暂时无法回答你的问题，请稍后再试。"
                
        except Exception:
            return "抱歉，我有点问题，稍后再聊好吗？"
    
    def set_system_prompt(self, prompt):
        """设置系统提示词"""
        try:
            self.system_prompt = prompt
            return True
        except Exception:
            return False
    
    def update_api_key(self, api_key):
        """更新API密钥"""
        try:
            self.api_key = api_key
            return True
        except Exception:
            return False
