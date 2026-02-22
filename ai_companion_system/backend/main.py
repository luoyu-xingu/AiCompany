from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import audio, chat, config
from app.utils.logger import app_logger
from app.models.config import settings

# 创建FastAPI应用
app = FastAPI(
    title="AI Companion System API",
    description="AI陪伴系统API，支持语音交互、打断回复、情感分析等功能",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(config.router, prefix="/api/config", tags=["config"])

# 根路径
@app.get("/")
def read_root():
    app_logger.info("API根路径被访问")
    return {"message": "AI Companion System API", "version": "1.0.0"}

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
