# 配置说明

## 环境变量配置

### 1. DeepSeek API配置

为了使用AI智能摘要和SEO建议功能，您需要配置DeepSeek API密钥：

```bash
# 设置环境变量
export DEEPSEEK_API_KEY="your_deepseek_api_key_here"
```

### 2. 获取DeepSeek API密钥

1. 访问 [DeepSeek 官网](https://platform.deepseek.com/)
2. 注册并登录账户
3. 在控制台中创建API密钥
4. 复制您的API密钥

### 3. 配置方式

#### 方式1：直接设置环境变量
```bash
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxx"
```

#### 方式2：创建.env文件
在项目根目录创建 `.env` 文件：
```
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxx
```

#### 方式3：宝塔面板配置
在宝塔面板的Python项目管理中，添加环境变量：
- 变量名: `DEEPSEEK_API_KEY`
- 变量值: `your_deepseek_api_key_here`

### 4. 验证配置

启动服务后，如果环境变量未配置，日志中会显示警告：
```
WARNING: 未找到DEEPSEEK_API_KEY环境变量，AI功能将不可用
```

## 功能说明

### AI智能摘要
- 使用DeepSeek Chat模型
- 自动总结网页内容
- 突出关键信息和主要观点
- 控制在150字以内

### SEO优化建议
- 使用DeepSeek Reasoner模型
- 分析页面标题、描述、关键词
- 评估内容结构和链接情况
- 提供具体的SEO优化建议

## 费用说明

- DeepSeek API按使用量收费
- 建议设置合理的使用限制
- 可以通过prompt参数控制输出长度以节省费用 