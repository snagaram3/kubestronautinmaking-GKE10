import os
import asyncio
from typing import Optional
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn

# Initialize FastAPI
app = FastAPI(
    title="AI Gateway - Frontend Integration Layer", 
    description="Proxies requests to Online Boutique while injecting AI widget",
    version="2.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
FRONTEND_SERVICE_URL = os.environ.get("FRONTEND_URL", "http://frontend.default.svc.cluster.local")
MCP_SERVICE_URL = os.environ.get("MCP_URL", "http://mcp-server.ai-agents.svc.cluster.local:8080")
A2A_SERVICE_URL = os.environ.get("A2A_URL", "http://a2a-orchestrator.ai-agents.svc.cluster.local:8081")

# AI Widget injection HTML
AI_WIDGET_HTML = """
<!-- AI Shopping Assistant Widget -->
<div id="ai-assistant-container">
    <div id="ai-assistant-btn" onclick="toggleAIPanel()" style="
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        transition: all 0.3s;
    ">
        <span style="font-size: 28px;">🤖</span>
    </div>

    <div id="ai-panel" style="
        display: none;
        position: fixed;
        bottom: 90px;
        right: 20px;
        width: 380px;
        height: 500px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        z-index: 9998;
        overflow: hidden;
    ">
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <span>🤖 AI Shopping Assistant</span>
            <button onclick="toggleAIPanel()" style="
                background: rgba(255, 255, 255, 0.2);
                border: none;
                color: white;
                cursor: pointer;
                font-size: 18px;
                width: 28px;
                height: 28px;
                border-radius: 50%;
            ">×</button>
        </div>
        
        <div style="padding: 20px;">
            <div style="
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
            ">
                <h3 style="margin: 0;">Your Shopping Score</h3>
                <div style="font-size: 36px; font-weight: bold;">87/100</div>
                <div>You're saving 23% on average!</div>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h4 style="margin: 0 0 10px 0;">💡 AI Insights</h4>
                <ul style="margin: 0; padding-left: 20px; font-size: 14px;">
                    <li>Bundle items for 15% discount</li>
                    <li>Free shipping with 2 more items</li>
                    <li>Price drop alert active</li>
                </ul>
            </div>
            
            <div style="background: #e8f5e9; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h4 style="margin: 0 0 10px 0;">🎁 Recommendations</h4>
                <div style="font-size: 14px; color: #666;">
                    <div>• Vintage Camera Lens - $49.99</div>
                    <div>• Retro Film Pack - $19.99</div>
                </div>
            </div>
            
            <button onclick="optimizeCart()" style="
                width: 100%;
                padding: 12px;
                background: #4caf50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
            ">🎯 Optimize My Cart</button>
        </div>
    </div>
</div>

<script>
let panelOpen = false;

function toggleAIPanel() {
    const panel = document.getElementById('ai-panel');
    const btn = document.getElementById('ai-assistant-btn');
    
    if (!panelOpen) {
        panel.style.display = 'block';
        panelOpen = true;
        loadAIData();
    } else {
        panel.style.display = 'none';
        panelOpen = false;
    }
}

function optimizeCart() {
    showNotification('🔍 AI is analyzing your cart...');
    setTimeout(() => {
        showNotification('💰 Bundle deal found! You saved $25.99!');
    }, 2000);
}

async function loadAIData() {
    try {
        const response = await fetch('/api/insights/demo_user');
        console.log('AI data loaded');
    } catch (error) {
        console.log('Using default AI data');
    }
}

function showNotification(message) {
    const notif = document.createElement('div');
    notif.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    notif.textContent = message;
    document.body.appendChild(notif);
    setTimeout(() => notif.remove(), 3000);
}

// Add CSS animation
const style = document.createElement('style');
style.textContent = '@keyframes slideIn{from{transform:translateX(100%);opacity:0;}to{transform:translateX(0);opacity:1;}}';
document.head.appendChild(style);

// Show welcome message
setTimeout(() => {
    showNotification('🤖 AI Assistant ready! Click the purple button to start saving!');
}, 2000);
</script>
</body>"""

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "frontend_url": FRONTEND_SERVICE_URL,
        "mcp_url": MCP_SERVICE_URL,
        "a2a_url": A2A_SERVICE_URL
    }

@app.get("/widget-test")
async def widget_test():
    """Test page for the AI widget"""
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Widget Test</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 40px; background: #f0f0f0; }}
            .test-card {{ background: white; padding: 30px; border-radius: 10px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="test-card">
            <h1>🤖 AI Widget Test Page</h1>
            <p>This page tests the AI Shopping Assistant widget functionality.</p>
            <p><strong>Look for the purple AI button in the bottom right corner!</strong></p>
        </div>
        
        <div class="test-card">
            <h2>Test Features:</h2>
            <ul>
                <li>Click the AI assistant button</li>
                <li>View your shopping score</li>
                <li>Check AI insights</li>
                <li>Try cart optimization</li>
            </ul>
        </div>
        
        <div class="test-card">
            <h2>Connected Services:</h2>
            <p>MCP Server: {MCP_SERVICE_URL}</p>
            <p>A2A Orchestrator: {A2A_SERVICE_URL}</p>
            <p>Frontend: {FRONTEND_SERVICE_URL}</p>
        </div>
        
        {AI_WIDGET_HTML}
    </body>
    </html>
    """)

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_frontend(request: Request, path: str = ""):
    """Proxy requests to frontend with AI widget injection"""
    
    # Handle favicon
    if path == "favicon.ico":
        return Response(status_code=404)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Build target URL
            url = f"{FRONTEND_SERVICE_URL}/{path}"
            if request.url.query:
                url += f"?{request.url.query}"
            
            # Prepare headers
            headers = {
                k: v for k, v in request.headers.items() 
                if k.lower() not in ['host', 'content-length']
            }
            
            # Make request
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=await request.body() if request.method in ["POST", "PUT", "PATCH"] else None,
                follow_redirects=True
            )
            
            # Check if HTML response
            content_type = response.headers.get("content-type", "")
            
            if "text/html" in content_type:
                content = response.text
                
                # Inject widget before closing body tag
                if "</body>" in content:
                    content = content.replace("</body>", AI_WIDGET_HTML)
                    print(f"✅ AI Widget injected into {path}")
                else:
                    content = content + AI_WIDGET_HTML
                    print(f"✅ AI Widget appended to {path}")
                
                return HTMLResponse(
                    content=content,
                    status_code=response.status_code
                )
            
            # Non-HTML responses pass through
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=content_type
            )
            
        except httpx.ConnectError as e:
            print(f"Connection error to frontend: {e}")
            return HTMLResponse(
                f"""
                <html>
                <head><title>Online Boutique - AI Enhanced</title></head>
                <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                    <h1>🛍️ Online Boutique</h1>
                    <h2>AI-Enhanced Shopping Experience</h2>
                    <p>Main store is loading...</p>
                    <p>Frontend: {FRONTEND_SERVICE_URL}</p>
                    <p>Error: {str(e)}</p>
                    {AI_WIDGET_HTML}
                </body>
                </html>
                """,
                status_code=503
            )
        except Exception as e:
            print(f"Proxy error: {e}")
            return HTMLResponse(
                f"""
                <html>
                <body style="padding: 40px; text-align: center;">
                    <h1>Online Boutique - AI Enhanced</h1>
                    <p>Service temporarily unavailable</p>
                    <p>Error: {str(e)}</p>
                    {AI_WIDGET_HTML}
                </body>
                </html>
                """,
                status_code=500
            )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8090))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )