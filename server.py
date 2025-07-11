import os
import json
import logging
from datetime import datetime
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse

app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DeepSeek API配置
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

if not DEEPSEEK_API_KEY:
    logger.warning("未找到DEEPSEEK_API_KEY环境变量，AI功能将不可用")

# 爬虫配置
class WebCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def crawl_website(self, url):
        """爬取网站内容"""
        try:
            logger.info(f"开始爬取: {url}")
            
            # 发送请求
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除script和style标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            content = []
            
            # 提取标题
            title = soup.find('title')
            if title:
                content.append({
                    'type': '页面标题',
                    'tag': 'title',
                    'text': title.get_text().strip()
                })
            
            # 提取描述
            description = soup.find('meta', attrs={'name': 'description'})
            if description:
                content.append({
                    'type': '页面描述',
                    'tag': 'meta',
                    'text': description.get('content', '').strip()
                })
            
            # 提取关键词
            keywords = soup.find('meta', attrs={'name': 'keywords'})
            if keywords:
                content.append({
                    'type': '关键词',
                    'tag': 'meta',
                    'text': keywords.get('content', '').strip()
                })
            
            # 提取所有标题
            for i in range(1, 7):
                headings = soup.find_all(f'h{i}')
                for heading in headings:
                    text = heading.get_text().strip()
                    if text:
                        content.append({
                            'type': f'标题{i}',
                            'tag': f'h{i}',
                            'text': text
                        })
            
            # 提取段落
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 10:  # 过滤太短的段落
                    content.append({
                        'type': '段落',
                        'tag': 'p',
                        'text': text
                    })
            
            # 提取列表项
            list_items = soup.find_all('li')
            for li in list_items:
                text = li.get_text().strip()
                if text and len(text) > 5:
                    content.append({
                        'type': '列表项',
                        'tag': 'li',
                        'text': text
                    })
            
            # 提取链接
            links = soup.find_all('a', href=True)
            for link in links:
                text = link.get_text().strip()
                href = link.get('href')
                if text and href:
                    # 转换为绝对URL
                    absolute_url = urljoin(url, href)
                    content.append({
                        'type': '链接',
                        'tag': 'a',
                        'text': f"{text} -> {absolute_url}"
                    })
            
            # 提取图片
            images = soup.find_all('img', src=True)
            for img in images:
                alt = img.get('alt', '')
                src = img.get('src')
                if src:
                    absolute_url = urljoin(url, src)
                    content.append({
                        'type': '图片',
                        'tag': 'img',
                        'text': f"{alt} -> {absolute_url}" if alt else absolute_url
                    })
            
            # 提取表格内容
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for i, row in enumerate(rows):
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_text = ' | '.join([cell.get_text().strip() for cell in cells])
                        if row_text:
                            content.append({
                                'type': '表格行',
                                'tag': 'tr',
                                'text': row_text
                            })
            
            logger.info(f"爬取完成，共提取 {len(content)} 项内容")
            return content
            
        except requests.RequestException as e:
            logger.error(f"请求错误: {e}")
            raise Exception(f"请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"爬取错误: {e}")
            raise Exception(f"爬取失败: {str(e)}")

crawler = WebCrawler()

@app.route('/crawl', methods=['POST'])
def crawl():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': '请提供有效的URL'})
        
        # 验证URL格式
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return jsonify({'success': False, 'error': 'URL格式不正确'})
        
        # 爬取内容
        content = crawler.crawl_website(url)
        
        return jsonify({
            'success': True,
            'content': content,
            'url': url,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"API错误: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': '服务正常运行'})

# AI智能摘要接口
@app.route('/ai_summary', methods=['POST'])
def ai_summary():
    try:
        if not DEEPSEEK_API_KEY:
            return jsonify({'success': False, 'error': 'DeepSeek API密钥未配置'})
        
        data = request.get_json()
        content = data.get('content', [])
        prompt = data.get('prompt', '请用中文总结以下网页内容，突出关键信息和主要观点，控制在150字以内')
        
        if not content:
            return jsonify({'success': False, 'error': '内容为空'})
        
        # 提取文本内容
        text_content = []
        for item in content:
            if 'text' in item and item['text'].strip():
                text_content.append(f"{item['type']}: {item['text']}")
        
        if not text_content:
            return jsonify({'success': False, 'error': '没有找到有效的文本内容'})
        
        # 限制内容长度，避免token过多
        combined_text = '\n'.join(text_content)[:4000]
        
        # 调用DeepSeek Chat API
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {
                    'role': 'system',
                    'content': prompt
                },
                {
                    'role': 'user',
                    'content': combined_text
                }
            ],
            'temperature': 0.7,
            'max_tokens': 300
        }
        
        response = requests.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result['choices'][0]['message']['content']
            
            logger.info(f"AI摘要生成成功")
            return jsonify({
                'success': True,
                'summary': summary.strip()
            })
        else:
            logger.error(f"DeepSeek API错误: {response.status_code} - {response.text}")
            return jsonify({'success': False, 'error': 'AI摘要生成失败'})
            
    except Exception as e:
        logger.error(f"AI摘要错误: {e}")
        return jsonify({'success': False, 'error': str(e)})

# SEO建议接口
@app.route('/seo_advice', methods=['POST'])
def seo_advice():
    try:
        if not DEEPSEEK_API_KEY:
            return jsonify({'success': False, 'error': 'DeepSeek API密钥未配置'})
        
        data = request.get_json()
        content = data.get('content', [])
        prompt = data.get('prompt', '作为SEO专家，请基于以下网页内容分析并提供具体的SEO优化建议，包括标题、描述、关键词、内容结构等方面的建议')
        
        if not content:
            return jsonify({'success': False, 'error': '内容为空'})
        
        # 提取关键SEO信息
        seo_data = {
            'title': '',
            'description': '',
            'keywords': '',
            'headings': [],
            'content_length': 0,
            'links': 0,
            'images': 0
        }
        
        for item in content:
            if item['type'] == '页面标题':
                seo_data['title'] = item['text']
            elif item['type'] == '页面描述':
                seo_data['description'] = item['text']
            elif item['type'] == '关键词':
                seo_data['keywords'] = item['text']
            elif '标题' in item['type']:
                seo_data['headings'].append(item['text'])
            elif item['type'] == '段落':
                seo_data['content_length'] += len(item['text'])
            elif item['type'] == '链接':
                seo_data['links'] += 1
            elif item['type'] == '图片':
                seo_data['images'] += 1
        
        # 构建分析内容
        analysis_content = f"""
        页面标题: {seo_data['title']}
        页面描述: {seo_data['description']}
        关键词: {seo_data['keywords']}
        标题数量: {len(seo_data['headings'])}
        内容长度: {seo_data['content_length']}字
        链接数量: {seo_data['links']}
        图片数量: {seo_data['images']}
        
        标题列表:
        {' '.join(seo_data['headings'][:10])}
        """
        
        # 调用DeepSeek Reasoner API
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'deepseek-reasoner',
            'messages': [
                {
                    'role': 'system',
                    'content': prompt
                },
                {
                    'role': 'user',
                    'content': analysis_content
                }
            ],
            'temperature': 0.3,
            'max_tokens': 500
        }
        
        response = requests.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            advice = result['choices'][0]['message']['content']
            
            logger.info(f"SEO建议生成成功")
            return jsonify({
                'success': True,
                'advice': advice.strip()
            })
        else:
            logger.error(f"DeepSeek API错误: {response.status_code} - {response.text}")
            return jsonify({'success': False, 'error': 'SEO建议生成失败'})
            
    except Exception as e:
        logger.error(f"SEO建议错误: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/', methods=['GET'])
def index():
    return '''
    <h1>网页爬虫API服务</h1>
    <p>服务正在运行中...</p>
    <h3>API端点：</h3>
    <ul>
        <li>POST /crawl - 爬取网页内容</li>
        <li>POST /ai_summary - AI智能摘要</li>
        <li>POST /seo_advice - SEO优化建议</li>
        <li>GET /health - 健康检查</li>
    </ul>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 