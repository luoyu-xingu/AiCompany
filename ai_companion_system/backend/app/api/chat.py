from fastapi import APIRouter, HTTPException
from app.core.chat import ChatManager

router = APIRouter()

# 初始化对话管理器
chat_manager = ChatManager()

@router.post("/get-response")
async def get_response(user_input: str, emotion: str = "calm"):
    """获取对话回复"""
    try:
        if not user_input:
            raise HTTPException(status_code=400, detail="用户输入不能为空")
        
        response = chat_manager.get_response(user_input, emotion)
        
        return {"response": response}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="获取对话回复失败")

@router.post("/set-model")
async def set_model(model_name: str):
    """设置对话模型"""
    try:
        if model_name not in ["local", "doubao"]:
            raise HTTPException(status_code=400, detail="无效的模型名称")
        
        success = chat_manager.set_model(model_name)
        if not success:
            raise HTTPException(status_code=500, detail="设置模型失败")
        
        return {"success": True, "message": f"已切换到{model_name}模型"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="设置模型失败")

@router.post("/clear-history")
async def clear_history():
    """清空对话历史"""
    try:
        success = chat_manager.clear_history()
        if not success:
            raise HTTPException(status_code=500, detail="清空对话历史失败")
        
        return {"success": True, "message": "对话历史已清空"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="清空对话历史失败")

@router.post("/update-local-model")
async def update_local_model(templates: dict = None, keywords: dict = None):
    """更新本地模型"""
    try:
        success = chat_manager.update_local_model(templates, keywords)
        if not success:
            raise HTTPException(status_code=500, detail="更新本地模型失败")
        
        return {"success": True, "message": "本地模型已更新"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="更新本地模型失败")
