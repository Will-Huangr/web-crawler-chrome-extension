# Gunicorn配置文件
import multiprocessing

# 绑定地址和端口
bind = "0.0.0.0:5000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作进程类型
worker_class = "sync"

# 最大请求数
max_requests = 1000

# 请求超时时间
timeout = 30

# 保持连接时间
keepalive = 2

# 日志配置
loglevel = "info"
accesslog = "logs/access.log"
errorlog = "logs/error.log"

# 进程名称
proc_name = "webcrawler_api"

# 后台运行
daemon = False

# 用户和组
user = "www"
group = "www"

# 预加载应用
preload_app = True

# 重启工作进程
max_requests_jitter = 100

# 优雅重启
graceful_timeout = 30 