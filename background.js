// 后台脚本
console.log('网页爬虫助手后台脚本已加载');

// 监听插件安装
chrome.runtime.onInstalled.addListener(function() {
    console.log('网页爬虫助手插件已安装');
});

// 监听来自content script的消息
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    console.log('收到消息:', request);
    return true; // 保持消息通道开放
}); 