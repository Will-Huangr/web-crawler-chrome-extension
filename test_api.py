#!/usr/bin/env python3
"""
API测试脚本
用于测试网页爬虫API的功能
"""

import requests
import json
import time

def test_health():
    """测试健康检查接口"""
    try:
        response = requests.get('http://localhost:5000/health')
        print("🔍 健康检查测试:")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_crawl(url):
    """测试爬取功能"""
    try:
        data = {'url': url}
        response = requests.post(
            'http://localhost:5000/crawl',
            headers={'Content-Type': 'application/json'},
            json=data
        )
        
        print(f"\n🕷️ 爬取测试 - {url}:")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ 爬取成功，共获取 {len(result['content'])} 项内容")
                
                # 显示前5项内容
                print("\n📄 内容预览:")
                for i, item in enumerate(result['content'][:5]):
                    print(f"{i+1}. [{item['type']}] {item['text'][:100]}...")
                    
                if len(result['content']) > 5:
                    print(f"... 还有 {len(result['content']) - 5} 项内容")
            else:
                print(f"❌ 爬取失败: {result['error']}")
        else:
            print(f"❌ 请求失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 爬取测试失败: {e}")

def main():
    """主函数"""
    print("🚀 开始API测试...")
    
    # 测试健康检查
    if not test_health():
        print("❌ 服务器未运行，请先启动服务器")
        return
    
    # 测试爬取功能
    test_urls = [
        'https://example.com',
        'https://httpbin.org/html',
        'https://news.ycombinator.com'
    ]
    
    for url in test_urls:
        test_crawl(url)
        time.sleep(1)  # 避免请求过快
    
    print("\n✅ 测试完成！")

if __name__ == '__main__':
    main() 