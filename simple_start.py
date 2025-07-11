#!/usr/bin/env python3
"""
宝塔面板专用启动文件
产品经理友好版本，无需复杂配置
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入主应用
from server import app

# 宝塔面板会自动处理端口和进程管理
if __name__ == '__main__':
    # 生产环境运行
    app.run(host='0.0.0.0', port=5000, debug=False)
else:
    # WSGI应用对象，宝塔会自动识别
    application = app 