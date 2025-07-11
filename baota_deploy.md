# 宝塔面板部署指南

## 1. 环境准备

### 1.1 安装Python环境
1. 登录宝塔面板
2. 进入"软件商店"
3. 搜索并安装"Python项目管理器"
4. 安装Python 3.8或更高版本

### 1.2 创建网站
1. 在宝塔面板点击"网站"
2. 点击"添加站点"
3. 输入域名（如：crawler.yourdomain.com）
4. 选择目录（如：/www/wwwroot/crawler）
5. 不需要创建数据库
6. 点击"提交"

## 2. 上传项目文件

### 2.1 上传代码
1. 将项目文件上传到网站根目录
2. 文件结构应该如下：
```
/www/wwwroot/crawler/
├── server.py
├── requirements.txt
├── gunicorn_config.py
├── deploy.sh
└── logs/
```

### 2.2 创建日志目录
```bash
mkdir -p /www/wwwroot/crawler/logs
chmod 755 /www/wwwroot/crawler/logs
```

## 3. 配置Python环境

### 3.1 创建虚拟环境
```bash
cd /www/wwwroot/crawler
python3 -m venv venv
source venv/bin/activate
```

### 3.2 安装依赖
```bash
pip install -r requirements.txt
pip install gunicorn
```

## 4. 配置Gunicorn

### 4.1 测试运行
```bash
cd /www/wwwroot/crawler
source venv/bin/activate
gunicorn -c gunicorn_config.py server:app
```

### 4.2 创建启动脚本
创建文件 `/www/wwwroot/crawler/start.sh`：
```bash
#!/bin/bash
cd /www/wwwroot/crawler
source venv/bin/activate
gunicorn -c gunicorn_config.py server:app
```

设置执行权限：
```bash
chmod +x /www/wwwroot/crawler/start.sh
```

## 5. 配置Nginx反向代理

### 5.1 修改网站配置
1. 在宝塔面板点击网站名称后的"设置"
2. 点击"配置文件"
3. 替换server配置为：

```nginx
server {
    listen 80;
    server_name crawler.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300;
        proxy_read_timeout 300;
        proxy_send_timeout 300;
    }
}
```

### 5.2 重启Nginx
```bash
nginx -t
nginx -s reload
```

## 6. 创建系统服务

### 6.1 创建服务文件
创建文件 `/etc/systemd/system/webcrawler.service`：
```ini
[Unit]
Description=Web Crawler API Service
After=network.target

[Service]
Type=exec
User=www
Group=www
WorkingDirectory=/www/wwwroot/crawler
ExecStart=/www/wwwroot/crawler/venv/bin/gunicorn -c gunicorn_config.py server:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 6.2 启动服务
```bash
systemctl daemon-reload
systemctl enable webcrawler
systemctl start webcrawler
systemctl status webcrawler
```

## 7. 防火墙配置

### 7.1 开放端口
1. 在宝塔面板点击"安全"
2. 添加端口规则：端口5000，备注"爬虫API"
3. 如果使用域名访问，确保80端口已开放

### 7.2 配置SSL（可选）
1. 在网站设置中点击"SSL"
2. 选择"Let's Encrypt"免费证书
3. 点击"申请"

## 8. 测试部署

### 8.1 检查服务状态
```bash
curl http://your-domain.com/health
```

应该返回：
```json
{"status": "ok", "message": "服务正常运行"}
```

### 8.2 测试爬取功能
```bash
curl -X POST http://your-domain.com/crawl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## 9. 更新浏览器插件配置

修改 `popup.js` 中的服务器地址：
```javascript
const SERVER_URL = 'http://your-domain.com'; // 替换为你的域名
```

## 10. 监控和维护

### 10.1 查看日志
```bash
# 查看访问日志
tail -f /www/wwwroot/crawler/logs/access.log

# 查看错误日志
tail -f /www/wwwroot/crawler/logs/error.log

# 查看系统服务日志
journalctl -u webcrawler -f
```

### 10.2 重启服务
```bash
systemctl restart webcrawler
```

## 11. 常见问题

### 11.1 端口占用
```bash
# 查看端口占用
netstat -tlnp | grep 5000

# 杀死占用进程
kill -9 进程ID
```

### 11.2 权限问题
```bash
# 修改文件权限
chown -R www:www /www/wwwroot/crawler
chmod -R 755 /www/wwwroot/crawler
```

### 11.3 依赖问题
```bash
# 重新安装依赖
cd /www/wwwroot/crawler
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
``` 