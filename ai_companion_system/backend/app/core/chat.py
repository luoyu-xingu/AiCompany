from .doubao_chat import DoubaoChatModel
import random

class LocalChatModel:
    def __init__(self):
        # 初始化对话模板
        self.templates = {
            "greeting": [
                "你好！很高兴见到你，今天过得怎么样？",
                "嗨！有什么我可以帮忙的吗？",
                "你好，最近怎么样呀？"
            ],
            "farewell": [
                "再见！祝你有愉快的一天！",
                "拜拜，期待下次和你聊天！",
                "再见，有需要随时告诉我！"
            ],
            "thanks": [
                "不客气，能帮到你我很开心！",
                "没关系，这是我应该做的。",
                "不用谢，随时可以问我！"
            ],
            "weather": [
                "今天天气看起来不错呢！",
                "最近天气变化挺大的，注意增减衣物哦。",
                "天气真的很重要，影响我们的心情呢。"
            ],
            "hobby": [
                "你的爱好听起来很有趣！",
                "我也很喜欢类似的活动呢。",
                "爱好可以丰富我们的生活，真不错！"
            ],
            "default": [
                "我理解你的意思。",
                "这是个有趣的话题。",
                "我不太确定，我们可以换个话题聊聊。",
                "能再详细说说吗？"
            ]
        }
        
        # 关键词匹配
        self.keywords = {
            "greeting": ["你好", "嗨", "哈喽", "早上好", "下午好", "晚上好"],
            "farewell": ["再见", "拜拜", "下次见", "晚安"],
            "thanks": ["谢谢", "多谢", "感谢", "麻烦了"],
            "weather": ["天气", "晴天", "下雨", "下雪", "温度"],
            "hobby": ["爱好", "喜欢", "兴趣", "娱乐"]
        }
        
        # 对话历史
        self.history = []
    
    def add_to_history(self, role, content):
        """添加对话历史"""
        self.history.append({"role": role, "content": content})
        # 限制历史长度，避免内存占用过大
        if len(self.history) > 20:
            self.history = self.history[-20:]
    
    def clear_history(self):
        """清空对话历史"""
        self.history.clear()
    
    def get_response(self, user_input):
        """获取本地模型的回复"""
        try:
            # 添加用户输入到历史
            self.add_to_history("user", user_input)
            
            # 匹配关键词
            intent = self._match_intent(user_input)
            
            # 根据意图生成回复
            response = self._generate_response(intent, user_input)
            
            # 添加回复到历史
            self.add_to_history("assistant", response)
            
            return response
        except Exception:
            return "抱歉，我有点问题，稍后再聊好吗？"
    
    def _match_intent(self, user_input):
        """匹配用户意图"""
        user_input_lower = user_input.lower()
        
        for intent, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in user_input_lower:
                    return intent
        
        return "default"
    
    def _generate_response(self, intent, user_input):
        """根据意图生成回复"""
        if intent in self.templates:
            return random.choice(self.templates[intent])
        else:
            return random.choice(self.templates["default"])
    
    def update_templates(self, templates):
        """更新对话模板，用于用户自定义训练"""
        try:
            self.templates.update(templates)
            return True
        except Exception:
            return False
    
    def update_keywords(self, keywords):
        """更新关键词，用于用户自定义训练"""
        try:
            self.keywords.update(keywords)
            return True
        except Exception:
            return False

class ChatManager:
    def __init__(self):
        # 初始化本地模型
        self.local_model = LocalChatModel()
        # 初始化豆包API模型
        try:
            self.doubao_model = DoubaoChatModel()
        except Exception:
            self.doubao_model = None
        # 当前使用的模型
        self.current_model = "local"
    
    def set_model(self, model_name):
        """设置当前使用的模型"""
        if model_name in ["local", "doubao"]:
            self.current_model = model_name
            return True
        else:
            return False
    
    def get_response(self, user_input, emotion=None):
        """获取对话回复"""
        try:
            if self.current_model == "local":
                return self.local_model.get_response(user_input)
            elif self.current_model == "doubao" and self.doubao_model:
                return self.doubao_model.get_response(user_input, emotion)
            else:
                return "抱歉，模型暂时不可用，请稍后再试。"
        except Exception:
            return "抱歉，我有点问题，稍后再聊好吗？"
    
    def clear_history(self):
        """清空对话历史"""
        try:
            self.local_model.clear_history()
            if self.doubao_model:
                self.doubao_model.clear_history()
            return True
        except Exception:
            return False
    
    def update_local_model(self, templates=None, keywords=None):
        """更新本地模型"""
        success = True
        if templates:
            success = success and self.local_model.update_templates(templates)
        if keywords:
            success = success and self.local_model.update_keywords(keywords)
        return success
