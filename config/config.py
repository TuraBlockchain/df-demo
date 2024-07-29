import os

# 从环境变量中获取数据库配置
DATABASE_NAME = os.getenv('DATABASE_NAME', '')
DATABASE_USER = os.getenv('DATABASE_USER', '')
DATABASE_PASS = os.getenv('DATABASE_PASS', '')
DATABASE_HOST = os.getenv('DATABASE_HOST', '')
DATABASE_PORT = os.getenv('DATABASE_PORT', '')


