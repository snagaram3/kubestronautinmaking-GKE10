(function() {
    if (document.getElementById('ai-chat-widget')) return;
    const script = document.createElement('script');
    script.src = '/static/ai-chat/chat-widget.js';
    script.async = true;
    document.head.appendChild(script);
})();
