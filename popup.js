// 服务器配置 - 产品经理修改这里就行了！
// 本地测试用这个：http://localhost:5000
// 服务器部署后改成：http://你的域名.com:5000
const SERVER_URL = 'http://localhost:5000';

// 全局变量存储当前内容，用于重试功能
let currentContent = null;

document.addEventListener('DOMContentLoaded', function() {
    const urlInput = document.getElementById('urlInput');
    const crawlBtn = document.getElementById('crawlBtn');
    const crawlCurrentBtn = document.getElementById('crawlCurrentBtn');
    const status = document.getElementById('status');
    const resultContainer = document.getElementById('resultContainer');
    const resultContent = document.getElementById('resultContent');
    const currentUrl = document.getElementById('currentUrl');
    
    // 获取当前页面URL
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        const currentTab = tabs[0];
        currentUrl.textContent = `当前页面: ${currentTab.url}`;
        urlInput.value = currentTab.url;
    });
    
    // 爬取指定URL
    crawlBtn.addEventListener('click', function() {
        const url = urlInput.value.trim();
        if (!url) {
            showStatus('请输入有效的网址', 'error');
            return;
        }
        const formattedUrl = formatUrl(url);
        // 更新输入框显示格式化后的URL
        urlInput.value = formattedUrl;
        crawlWebsite(formattedUrl);
    });
    
    // 爬取当前页面
    crawlCurrentBtn.addEventListener('click', function() {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            const currentTab = tabs[0];
            crawlWebsite(currentTab.url);
        });
    });
    
    // URL格式化函数
    function formatUrl(url) {
        // 如果已经有协议，直接返回
        if (url.startsWith('http://') || url.startsWith('https://')) {
            return url;
        }
        
        // 如果没有协议，默认添加https://
        return 'https://' + url;
    }
    
    // 爬取网站函数
    async function crawlWebsite(url) {
        showStatus('正在爬取中...', 'loading');
        crawlBtn.disabled = true;
        crawlCurrentBtn.disabled = true;
        
        try {
            const response = await fetch(`${SERVER_URL}/crawl`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({url: url})
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                showStatus('爬取成功！', 'success');
                displayResults(data.content);
            } else {
                showStatus(`爬取失败: ${data.error}`, 'error');
            }
        } catch (error) {
            showStatus(`网络错误: ${error.message}`, 'error');
            console.error('爬取错误:', error);
        } finally {
            crawlBtn.disabled = false;
            crawlCurrentBtn.disabled = false;
        }
    }
    
    // 显示状态信息
    function showStatus(message, type) {
        status.textContent = message;
        status.className = `status ${type}`;
        status.style.display = 'block';
        
        if (type === 'success') {
            setTimeout(() => {
                status.style.display = 'none';
            }, 3000);
        }
    }
    
    // 显示爬取结果
    function displayResults(content) {
        const resultContent = document.getElementById('resultContent');
        const summaryStats = document.getElementById('summaryStats');
        const summaryText = document.getElementById('summaryText');
        
        // 存储内容供重试使用
        currentContent = content;
        
        resultContent.innerHTML = '';
        summaryStats.innerHTML = '';
        summaryText.innerHTML = '';
        
        // 设置AI区域的加载状态
        const aiSummaryContent = document.getElementById('aiSummaryContent');
        const seoAdviceContent = document.getElementById('seoAdviceContent');
        aiSummaryContent.innerHTML = '<div class="ai-loading">🤖 正在生成AI摘要...</div>';
        seoAdviceContent.innerHTML = '<div class="ai-loading">🔍 正在生成SEO建议...</div>';
        
        if (!content || content.length === 0) {
            resultContent.innerHTML = '<p>未找到内容</p>';
            summaryStats.innerHTML = '<div class="stat-item"><div class="stat-number">0</div><div class="stat-label">总项目</div></div>';
            summaryText.innerHTML = '未找到任何内容';
            aiSummaryContent.innerHTML = '<div class="ai-error">没有内容可以生成摘要</div>';
            seoAdviceContent.innerHTML = '<div class="ai-error">没有内容可以生成SEO建议</div>';
            resultContainer.style.display = 'block';
            return;
        }
        
        // 生成汇总统计
        const stats = generateSummaryStats(content);
        displaySummaryStats(stats);
        
        // 生成汇总文本
        const summaryTextContent = generateSummaryText(content);
        summaryText.innerHTML = summaryTextContent;
        
        // 显示详细内容
        content.forEach((item, index) => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'content-item';
            
            const typeDiv = document.createElement('div');
            typeDiv.className = 'content-type';
            typeDiv.textContent = `${item.type} (${item.tag})`;
            
            const textDiv = document.createElement('div');
            textDiv.className = 'content-text';
            textDiv.textContent = item.text;
            
            itemDiv.appendChild(typeDiv);
            itemDiv.appendChild(textDiv);
            resultContent.appendChild(itemDiv);
        });
        
        // 调用AI智能摘要
        generateAISummary(content);
        
        // 调用SEO建议
        generateSEOAdvice(content);
        
        resultContainer.style.display = 'block';
    }
    
    // 生成AI智能摘要
    async function generateAISummary(content) {
        const aiSummaryContent = document.getElementById('aiSummaryContent');
        
        try {
            const response = await fetch(`${SERVER_URL}/ai_summary`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    prompt: '请用中文总结以下网页内容，突出关键信息和主要观点，控制在150字以内'
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                aiSummaryContent.innerHTML = `<div>${data.summary}</div>`;
            } else {
                aiSummaryContent.innerHTML = `
                    <div class="ai-error">
                        <div>AI摘要生成失败</div>
                        <button class="retry-btn" onclick="retryAISummary()">🔄 重试</button>
                    </div>
                `;
            }
        } catch (error) {
            console.error('AI摘要错误:', error);
            aiSummaryContent.innerHTML = `
                <div class="ai-error">
                    <div>AI摘要服务暂时不可用</div>
                    <button class="retry-btn" onclick="retryAISummary()">🔄 重试</button>
                </div>
            `;
        }
    }
    
    // 生成SEO建议
    async function generateSEOAdvice(content) {
        const seoAdviceContent = document.getElementById('seoAdviceContent');
        
        try {
            const response = await fetch(`${SERVER_URL}/seo_advice`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    prompt: '作为SEO专家，请基于以下网页内容分析并提供具体的SEO优化建议，包括标题、描述、关键词、内容结构等方面的建议'
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                displaySEOAdvice(data.advice);
            } else {
                seoAdviceContent.innerHTML = `
                    <div class="ai-error">
                        <div>SEO建议生成失败</div>
                        <button class="retry-btn" onclick="retrySEOAdvice()">🔄 重试</button>
                    </div>
                `;
            }
        } catch (error) {
            console.error('SEO建议错误:', error);
            seoAdviceContent.innerHTML = `
                <div class="ai-error">
                    <div>SEO建议服务暂时不可用</div>
                    <button class="retry-btn" onclick="retrySEOAdvice()">🔄 重试</button>
                </div>
            `;
        }
    }
    
    // 重试AI摘要
    function retryAISummary() {
        if (currentContent) {
            const aiSummaryContent = document.getElementById('aiSummaryContent');
            aiSummaryContent.innerHTML = '<div class="ai-loading">🤖 正在重新生成AI摘要...</div>';
            generateAISummary(currentContent);
        }
    }
    
    // 重试SEO建议
    function retrySEOAdvice() {
        if (currentContent) {
            const seoAdviceContent = document.getElementById('seoAdviceContent');
            seoAdviceContent.innerHTML = '<div class="ai-loading">🔍 正在重新生成SEO建议...</div>';
            generateSEOAdvice(currentContent);
        }
    }
    
    // 显示SEO建议
    function displaySEOAdvice(advice) {
        const seoAdviceContent = document.getElementById('seoAdviceContent');
        
        if (typeof advice === 'string') {
            // 如果是字符串，按换行分割成列表
            const items = advice.split('\n').filter(item => item.trim());
            seoAdviceContent.innerHTML = items.map(item => 
                `<div class="seo-item">${item.trim()}</div>`
            ).join('');
        } else if (Array.isArray(advice)) {
            // 如果是数组，直接显示
            seoAdviceContent.innerHTML = advice.map(item => 
                `<div class="seo-item">${item}</div>`
            ).join('');
        } else {
            seoAdviceContent.innerHTML = '<div class="ai-error">SEO建议格式错误</div>';
        }
    }
    
    // 生成汇总统计信息
    function generateSummaryStats(content) {
        const stats = {
            total: content.length,
            byType: {}
        };
        
        content.forEach(item => {
            if (stats.byType[item.type]) {
                stats.byType[item.type]++;
            } else {
                stats.byType[item.type] = 1;
            }
        });
        
        return stats;
    }
    
    // 显示汇总统计
    function displaySummaryStats(stats) {
        const summaryStats = document.getElementById('summaryStats');
        
        // 总项目数
        const totalDiv = document.createElement('div');
        totalDiv.className = 'stat-item';
        totalDiv.innerHTML = `<div class="stat-number">${stats.total}</div><div class="stat-label">总项目</div>`;
        summaryStats.appendChild(totalDiv);
        
        // 各类型统计
        const sortedTypes = Object.keys(stats.byType).sort((a, b) => stats.byType[b] - stats.byType[a]);
        
        sortedTypes.slice(0, 3).forEach(type => {
            const typeDiv = document.createElement('div');
            typeDiv.className = 'stat-item';
            typeDiv.innerHTML = `<div class="stat-number">${stats.byType[type]}</div><div class="stat-label">${type}</div>`;
            summaryStats.appendChild(typeDiv);
        });
    }
    
    // 生成汇总文本
    function generateSummaryText(content) {
        const titleContent = content.find(item => item.type === '页面标题');
        const descContent = content.find(item => item.type === '页面描述');
        const headingCount = content.filter(item => item.type.includes('标题')).length;
        
        let summary = '';
        
        if (titleContent) {
            summary += `<strong>页面标题:</strong> ${titleContent.text}<br>`;
        }
        
        if (descContent) {
            summary += `<strong>页面描述:</strong> ${descContent.text.substring(0, 100)}${descContent.text.length > 100 ? '...' : ''}<br>`;
        }
        
        summary += `<strong>内容统计:</strong> 共找到 ${content.length} 个内容项`;
        
        if (headingCount > 0) {
            summary += `，包含 ${headingCount} 个标题`;
        }
        
        return summary;
    }
}); 