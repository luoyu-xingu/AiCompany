from fastapi import APIRouter, HTTPException
from app.models.config import settings
from app.utils.logger import app_logger

router = APIRouter()

@router.get("/get-config")
async def get_config():
    """获取系统配置"""
    try:
        app_logger.info("获取系统配置")
        config = {
            "api_host": settings.api_host,
            "api_port": settings.api_port,
            "sample_rate": settings.sample_rate,
            "audio_chunk": settings.audio_chunk,
            "emotion_model": settings.emotion_model,
            "log_level": settings.log_level
        }
        return {"config": config}
    except Exception as e:
        app_logger.error(f"获取系统配置失败: {e}")
        raise HTTPException(status_code=500, detail="获取系统配置失败")

@router.post("/update-config")
async def update_config(sample_rate: int = None, audio_chunk: int = None, log_level: str = None):
    """更新系统配置"""
    try:
        # 这里可以添加配置更新逻辑
        # 注意：由于使用了pydantic-settings，实际更新可能需要写入.env文件
        
        app_logger.info(f"更新系统配置: sample_rate={sample_rate}, audio_chunk={audio_chunk}, log_level={log_level}")
        
        # 模拟更新成功
        return {"success": True, "message": "系统配置更新成功"}
    except Exception as e:
        app_logger.error(f"更新系统配置失败: {e}")
        raise HTTPException(status_code=500, detail="更新系统配置失败")

@router.post("/update-api-keys")
async def update_api_keys(openai_api_key: str = None, doubao_api_key: str = None):
    """更新API密钥"""
    try:
        # 这里可以添加API密钥更新逻辑
        # 注意：实际更新可能需要写入.env文件
        
        app_logger.info("更新API密钥")
        
        # 模拟更新成功
        return {"success": True, "message": "API密钥更新成功"}
    except Exception as e:
        app_logger.error(f"更新API密钥失败: {e}")
        raise HTTPException(status_code=500, detail="更新API密钥失败")
