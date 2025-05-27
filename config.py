import os

# DeepSeek API 配置
DEEPSEEK_API_KEY = "写key"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 邮件配置
SENDER_EMAIL = "写发件邮箱"
SENDER_PASSWORD = "写授权码"
RECIPIENTS = ["写收件邮箱"]

# 缓存配置
CACHE_DIR = "cache"
MAX_CACHE_AGE_DAYS = 1

# API 请求头
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
}

# 项目数量
NUM_PROJECTS = 10
