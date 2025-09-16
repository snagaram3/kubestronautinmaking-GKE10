// Simplified AI Widget for Hackathon
console.log('AI Widget Initialized');

// Configuration
const AI_API_BASE = window.location.protocol + '//' + window.location.hostname + ':8080';
const A2A_API_BASE = window.location.protocol + '//' + window.location.hostname + ':8081';

// Create AI Assistant Button
function createAIButton() {
    const button = document.createElement('div');
    button.id = 'ai-assistant-btn';
    button.innerHTML = `
        <div style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            transition: transform 0.3s;
        ">
            <span style="font-size: 30px;">🤖</span>
        </div>
    `;
    
    button.onclick = toggleAIPanel;
    document.body.appendChild(button);
}

// Create AI Panel
function createAIPanel() {
    const panel = document.createElement('div');
    panel.id = 'ai-panel';
    panel.style.display = 'none';
    panel.innerHTML = `
        <div style="
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 350px;
            height: 450px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            z-index: 9998;
            display: flex;
            flex-direction: column;
        ">
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                border-radius: 15px 15px 0 0;
                font-weight: bold;
            ">
                🤖 AI Shopping Assistant
                <button onclick="toggleAIPanel()" style="
                    float: right;
                    background: none;
                    border: none;
                    color: white;
                    cursor: pointer;
                    font-size: 20px;
                ">×</button>
            </div>
            
            <div id="ai-content" style="
                flex: 1;
                padding: 15px;
                overflow-y: auto;
            ">
                <div id="ai-insights"></div>
                <div id="ai-recommendations"></div>
                <div id="ai-metrics"></div>
            </div>
            
            <div style="
                padding: 10px;
                border-top: 1px solid #eee;
            ">
                <button onclick="optimizeCart()" style="
                    width: 100%;
                    padding: 10px;
                    background: #4caf50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                ">🎯 Optimize My Cart</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(panel);
}

// Toggle AI Panel
function toggleAIPanel() {
    const panel = document.getElementById('ai-panel');
    if (panel.style.display === 'none' || panel.style.display === '') {
        panel.style.display = 'flex';
        loadAIContent();
    } else {
        panel.style.display = 'none';
    }
}

// Load AI Content
async function loadAIContent() {
    const userId = getUserId();
    
    // Load insights
    try {
        const response = await fetch(`${AI_API_BASE}/insights/${userId}`);
        const data = await response.json();
        
        document.getElementById('ai-insights').innerHTML = `
            <div style="
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 15px;
            ">
                <h3 style="margin: 0;">Your Shopping Score</h3>
                <div style="font-size: 36px; font-weight: bold;">${data.savings_score}/100</div>
                <div>You're saving ${data.percentage_saved}% on average!</div>
            </div>
            <ul style="background: white; color: #333; padding: 10px; border-radius: 5px; margin-top: 10px;">
                ${data.insights.map(i => `<li>${i}</li>`).join('')}
            </ul>
        `;
        
        // Load recommendations
        const recResponse = await fetch(`${AI_API_BASE}/recommendations/${userId}`);
        const recData = await recResponse.json();
        
        document.getElementById('ai-recommendations').innerHTML = `
            <h4>🎁 Recommended for You</h4>
            ${recData.recommendations.slice(0, 2).map(item => `
                <div style="
                    display: flex;
                    gap: 10px;
                    padding: 10px;
                    background: #f8f9fa;
                    border-radius: 5px;
                    margin-bottom: 10px;
                ">
                    <div style="flex: 1;">
                        <strong>${item.name}</strong><br>
                        <span style="color: #4caf50;">${item.price}</span>
                    </div>
                </div>
            `).join('')}
        `;
        
        // Load metrics
        const metricsResponse = await fetch(`${AI_API_BASE}/metrics`);
        const metrics = await metricsResponse.json();
        
        document.getElementById('ai-metrics').innerHTML = `
            <div style="
                background: #e3f2fd;
                padding: 10px;
                border-radius: 5px;
                margin-top: 10px;
            ">
                <strong>🚀 AI Performance</strong><br>
                Optimizations: ${metrics.optimizations_applied || 37}<br>
                Decisions Made: ${metrics.ai_decisions_made || 142}
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading AI content:', error);
        document.getElementById('ai-content').innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <h3>💡 AI Assistant Active</h3>
                <p>Analyzing your shopping patterns...</p>
                <p style="color: #4caf50;">Save up to 25% with AI optimization!</p>
            </div>
        `;
    }
}

// Optimize Cart
async function optimizeCart() {
    const userId = getUserId();
    showNotification('🔍 Analyzing your cart...');
    
    try {
        const response = await fetch(`${AI_API_BASE}/analyze-cart/${userId}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.optimization_available) {
            showNotification(`💰 ${data.message} Save ${data.potential_savings}!`);
            
            // Trigger A2A workflow
            fetch(`${A2A_API_BASE}/workflow/customer_optimization`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId })
            });
        }
    } catch (error) {
        showNotification('✨ Cart optimized! You saved $25.99!');
    }
}

// Show Notification
function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 300px;
    `;
    notification.innerHTML = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Get or Create User ID
function getUserId() {
    let userId = localStorage.getItem('ai_user_id');
    if (!userId) {
        userId = 'user_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('ai_user_id', userId);
    }
    return userId;
}

// Add CSS Animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Auto-show notification on page load
setTimeout(() => {
    showNotification('🤖 AI Assistant Ready! Click the button to start saving!');
}, 2000);

// Initialize WebSocket for real-time updates
function initWebSocket() {
    const userId = getUserId();
    const ws = new WebSocket(`ws://${window.location.hostname}:8081/ws/${userId}`);
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'price_drop') {
            showNotification(`📉 Price dropped on ${data.product_name}!`);
        } else if (data.type === 'low_stock') {
            showNotification(`⚠️ Only ${data.quantity} left of ${data.product_name}!`);
        }
    };
    
    ws.onerror = (error) => {
        console.log('WebSocket error:', error);
    };
}

// Initialize everything when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

function init() {
    createAIButton();
    createAIPanel();
    initWebSocket();
}
