# 网页爬虫浏览器插件

一个完整的网页爬虫解决方案，包含浏览器插件前端和Python后端服务，可以快速爬取网页内容并分段展示。
<img width="436" height="537" alt="image" src="https://github.com/user-attachments/assets/3f9c7b2f-cebc-46b1-9ff4-ad8b29a95da5" />
<img width="460" height="593" alt="image" src="https://github.com/user-attachments/assets/d9ee9691-3b5f-4740-b0d3-ed034956bb79" />


## 🚀 功能特点

- **浏览器插件**：方便的Chrome扩展，支持一键爬取
- **智能解析**：自动识别页面标题、段落、链接、图片等内容
- **分段显示**：按内容类型分类展示爬取结果
- **AI智能摘要**：使用DeepSeek Chat模型自动生成内容摘要
- **SEO优化建议**：基于DeepSeek Reasoner模型提供专业SEO建议
- **内容汇总**：智能统计和分析爬取的内容
- **实时状态**：显示爬取进度和结果状态
- **跨域支持**：支持爬取任意网站内容
- **服务器部署**：完整的后端API服务，支持宝塔面板部署

## 📁 项目结构

```
├── 浏览器插件文件
│   ├── manifest.json          # 插件配置文件
│   ├── popup.html            # 插件弹窗界面
│   ├── popup.js              # 插件主要逻辑
│   ├── content.js            # 内容脚本
│   └── background.js         # 后台脚本
├── 后端服务
│   ├── server.py             # Flask API服务器
│   ├── requirements.txt      # Python依赖
│   └── gunicorn_config.py    # 生产环境配置
├── 部署文件
│   ├── deploy.sh             # 自动部署脚本
│   ├── baota_deploy.md       # 宝塔部署指南
│   └── install_chrome_extension.md  # 插件安装指南
└── README.md                 # 项目说明
```

## 🛠️ 快速开始

### 1. 环境变量配置

**配置DeepSeek API密钥（AI功能必需）：**

#### 方式1：使用.env文件（推荐）
```bash
# 复制模板文件
cp .env.example .env

# 编辑.env文件，填入你的API密钥
nano .env
```

在.env文件中配置：
```
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
```

#### 方式2：直接设置环境变量
```bash
export DEEPSEEK_API_KEY="your_deepseek_api_key_here"
```

详细配置说明请参考 [CONFIG.md](CONFIG.md)

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 启动后端服务
```bash
python server.py
```

### 4. 安装浏览器插件
1. 打开Chrome浏览器
2. 访问 `chrome://extensions/`
3. 开启"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择项目文件夹

### 5. 配置服务器地址
在 `popup.js` 中修改服务器地址：
```javascript
const SERVER_URL = 'http://your-server-domain.com:5000';
```

## 🖥️ 使用方法

1. **爬取当前页面**：点击"爬取当前页面"按钮
2. **指定URL爬取**：在输入框中输入目标网址，点击"开始爬取"
3. **查看结果**：爬取完成后，内容会分段显示在结果区域

## 📊 支持的内容类型

- 📝 页面标题和描述
- 🔖 各级标题 (H1-H6)
- 📄 段落内容
- 📋 列表项
- 🔗 链接
- 🖼️ 图片
- 📊 表格内容
- 🏷️ 关键词

## 🌐 部署指南

### 本地开发
```bash
# 克隆项目
git clone https://github.com/Will-Huangr/web-crawler-chrome-extension.git

# 进入项目目录
cd web-crawler-chrome-extension

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填入你的DeepSeek API密钥

# 运行服务器
python server.py
```

### 宝塔面板部署
详见 [宝塔部署指南](baota_deploy.md)

### 生产环境部署
```bash
# 使用Gunicorn启动
gunicorn -c gunicorn_config.py server:app

# 或使用部署脚本
bash deploy.sh
```

## 🔧 API接口

### POST /crawl
爬取网页内容

**请求体：**
```json
{
  "url": "https://example.com"
}
```

**响应：**
```json
{
  "success": true,
  "content": [
    {
      "type": "页面标题",
      "tag": "title",
      "text": "示例页面"
    }
  ],
  "url": "https://example.com",
  "timestamp": 1234567890
}
```

### POST /ai_summary
AI智能摘要

**请求体：**
```json
{
  "content": [
    {
      "type": "页面标题",
      "tag": "title",
      "text": "示例页面"
    }
  ],
  "prompt": "请用中文总结以下网页内容，突出关键信息和主要观点，控制在150字以内"
}
```

**响应：**
```json
{
  "success": true,
  "summary": "这是一个关于示例页面的智能摘要..."
}
```

### POST /seo_advice
SEO优化建议

**请求体：**
```json
{
  "content": [
    {
      "type": "页面标题",
      "tag": "title",
      "text": "示例页面"
    }
  ],
  "prompt": "作为SEO专家，请基于以下网页内容分析并提供具体的SEO优化建议"
}
```

**响应：**
```json
{
  "success": true,
  "advice": "1. 标题长度建议优化...\n2. 描述内容需要完善...\n3. 建议添加更多关键词..."
}
```

### GET /health
健康检查

**响应：**
```json
{
  "status": "ok",
  "message": "服务正常运行"
}
```

## 🛡️ 安全说明

- 服务器端已配置CORS策略
- 支持HTTPS部署
- 请求超时保护
- 用户代理伪装

## 📋 依赖要求

### 后端依赖
- Python 3.8+
- Flask 2.3.3
- Flask-CORS 4.0.0
- requests 2.31.0
- beautifulsoup4 4.12.2
- lxml 4.9.3

### 浏览器支持
- Chrome 88+
- Edge 88+
- Firefox（需要适配）

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目。

## 📄 许可证

本项目采用 MIT 许可证。

## 🔍 故障排除

### 常见问题
1. **插件无法加载**：检查manifest.json格式
2. **无法爬取内容**：确认服务器地址和网络连接
3. **跨域问题**：检查CORS配置

### 调试方法
1. 查看浏览器控制台日志
2. 检查服务器日志
3. 使用curl测试API接口

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- [提交Issue](https://github.com/Will-Huangr/web-crawler-chrome-extension/issues)
- [查看项目](https://github.com/Will-Huangr/web-crawler-chrome-extension) 
