class AIChatWidget {
    constructor() {
        this.isOpen = false;
        this.conversationId = 'conv_' + Date.now();
        this.apiEndpoint = '/api/ai-chat';
        this.initialize();
    }
    
    initialize() {
        this.createWidget();
        this.attachEventListeners();
    }
    
    createWidget() {
        const widgetHTML = `
        <div id="ai-chat-widget" style="position:fixed;bottom:20px;right:20px;z-index:10000;font-family:sans-serif;">
            <div id="chat-toggle" style="background:#4285f4;color:white;padding:12px 20px;border-radius:25px;cursor:pointer;">
                💬 AI Assistant
            </div>
            <div id="chat-window" style="display:none;position:absolute;bottom:60px;right:0;width:350px;height:400px;background:white;border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,0.1);display:flex;flex-direction:column;">
                <div style="background:#4285f4;color:white;padding:16px;border-radius:12px 12px 0 0;">
                    <h3 style="margin:0;">AI Shopping Assistant</h3>
                </div>
                <div id="chat-messages" style="flex:1;overflow-y:auto;padding:16px;">
                    <div style="background:#f1f3f4;padding:12px;border-radius:18px;margin-bottom:12px;">
                        Hi! I'm your AI shopping assistant. How can I help you today?
                    </div>
                </div>
                <div style="padding:16px;border-top:1px solid #e0e0e0;">
                    <input type="text" id="chat-input" placeholder="Ask me anything..." style="width:100%;padding:12px;border:1px solid #e0e0e0;border-radius:20px;outline:none;">
                    <button id="chat-send" style="background:#4285f4;color:white;border:none;padding:12px 20px;border-radius:20px;cursor:pointer;margin-top:8px;">Send</button>
                </div>
            </div>
        </div>`;
        
        document.body.insertAdjacentHTML('beforeend', widgetHTML);
    }
    
    attachEventListeners() {
        document.getElementById('chat-toggle').onclick = () => this.toggleChat();
        document.getElementById('chat-send').onclick = () => this.sendMessage();
        document.getElementById('chat-input').onkeypress = (e) => {
            if (e.key === 'Enter') this.sendMessage();
        };
    }
    
    toggleChat() {
        const window = document.getElementById('chat-window');
        this.isOpen = !this.isOpen;
        window.style.display = this.isOpen ? 'flex' : 'none';
    }
    
    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (!message) return;
        
        this.addMessage(message, 'user');
        input.value = '';
        
        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message, conversation_id: this.conversationId})
            });
            const data = await response.json();
            this.addMessage(data.response, 'ai');
        } catch (error) {
            this.addMessage('Sorry, I had trouble processing that.', 'ai');
        }
    }
    
    addMessage(content, type) {
        const messages = document.getElementById('chat-messages');
        const div = document.createElement('div');
        div.style.cssText = `padding:12px;border-radius:18px;margin-bottom:12px;${type === 'user' ? 'background:#4285f4;color:white;margin-left:20%;' : 'background:#f1f3f4;margin-right:20%;'}`;
        div.textContent = content;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new AIChatWidget());
} else {
    new AIChatWidget();
}
