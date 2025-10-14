"""
Gunicorn配置文件
Production-ready configuration for the ML carbonation prediction system
"""

import multiprocessing

# 服务器套接字
bind = "0.0.0.0:5002"
backlog = 2048

# Worker进程
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# 重启设置
preload_app = True
reload = False

# 日志记录
accesslog = "/home/user/webapp/logs/access.log"
errorlog = "/home/user/webapp/logs/error.log"
loglevel = "info"
capture_output = True

# 进程命名
proc_name = "ml_carbonation_app"

# 安全设置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 性能优化
preload_app = True
enable_stdio_inheritance = True