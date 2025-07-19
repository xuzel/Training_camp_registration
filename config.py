"""
应用配置文件
"""

import os
from typing import Optional


class Settings:
    """应用配置类"""

    # 基础配置
    APP_NAME: str = "训练营报名系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # 数据库配置（预留）
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # 邮件配置（预留）
    MAIL_SERVER: Optional[str] = os.getenv("MAIL_SERVER")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME: Optional[str] = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: Optional[str] = os.getenv("MAIL_PASSWORD")

    # 管理员配置
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

    def __init__(self):
        # 确保上传目录存在
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)


# 创建设置实例
settings = Settings()

# 导出常用配置
APP_NAME = settings.APP_NAME
DEBUG = settings.DEBUG
SECRET_KEY = settings.SECRET_KEY