// 内容脚本 - 在网页中运行
console.log('网页爬虫助手内容脚本已加载');

// 监听来自popup的消息
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'getCurrentPageContent') {
        const content = extractPageContent();
        sendResponse({content: content});
    }
});

// 提取页面内容
function extractPageContent() {
    const content = [];
    
    // 提取标题
    const title = document.title;
    if (title) {
        content.push({
            type: '页面标题',
            tag: 'title',
            text: title
        });
    }
    
    // 提取描述
    const description = document.querySelector('meta[name="description"]');
    if (description) {
        content.push({
            type: '页面描述',
            tag: 'meta',
            text: description.getAttribute('content')
        });
    }
    
    // 提取所有标题
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    headings.forEach(heading => {
        if (heading.textContent.trim()) {
            content.push({
                type: '标题',
                tag: heading.tagName.toLowerCase(),
                text: heading.textContent.trim()
            });
        }
    });
    
    // 提取段落
    const paragraphs = document.querySelectorAll('p');
    paragraphs.forEach(p => {
        if (p.textContent.trim() && p.textContent.trim().length > 10) {
            content.push({
                type: '段落',
                tag: 'p',
                text: p.textContent.trim()
            });
        }
    });
    
    // 提取链接
    const links = document.querySelectorAll('a[href]');
    links.forEach(link => {
        if (link.textContent.trim() && link.href) {
            content.push({
                type: '链接',
                tag: 'a',
                text: `${link.textContent.trim()} (${link.href})`
            });
        }
    });
    
    return content;
} 