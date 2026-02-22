import logging
import os

# 默认日志目录
DEFAULT_LOG_DIR = 'logs'

# 当前日志目录
current_log_dir = DEFAULT_LOG_DIR

def setup_logger(name, log_file, level=logging.INFO):
    """设置日志记录器"""
    # 简化日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    
    # 清除现有处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    logger.setLevel(level)
    logger.addHandler(file_handler)
    
    return logger

def set_log_directory(log_dir):
    """设置日志目录"""
    global current_log_dir
    current_log_dir = log_dir
    
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    
    # 重新初始化日志记录器
    initialize_loggers(log_dir)

def initialize_loggers(log_dir=DEFAULT_LOG_DIR):
    """初始化日志记录器"""
    global app_logger, audio_logger, chat_logger, emotion_logger
    
    # 应用日志
    app_logger = setup_logger('app', os.path.join(log_dir, 'app.log'))
    
    # 音频日志
    audio_logger = setup_logger('audio', os.path.join(log_dir, 'audio.log'))
    
    # 对话日志
    chat_logger = setup_logger('chat', os.path.join(log_dir, 'chat.log'))
    
    # 情感分析日志
    emotion_logger = setup_logger('emotion', os.path.join(log_dir, 'emotion.log'))

# 初始化默认日志记录器
initialize_loggers()
