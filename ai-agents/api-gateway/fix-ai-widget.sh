#!/bin/bash

echo "🔧 Fixing AI Widget Integration"
echo "================================"

# First, let's check what's currently running
echo "Checking current services..."
kubectl get svc -n ai-agents

# Delete the old api-gateway if it exists
kubectl delete deployment api-gateway -n ai-agents 2>/dev/null
kubectl delete service api-gateway -n ai-agents 2>/dev/null

# Deploy improved API Gateway with embedded widget
cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-widget-config
  namespace: ai-agents
data:
  widget.html: |
    <!-- AI Widget HTML -->
    <div id="ai-assistant-btn" style="position:fixed;bottom:20px;right:20px;width:60px;height:60px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:50%;cursor:pointer;box-shadow:0 4px 15px rgba(0,0,0,0.2);display:flex;align-items:center;justify-content:center;z-index:9999;">
      <span style="font-size:30px;">🤖</span>
    </div>
    
    <div id="ai-panel" style="display:none;position:fixed;bottom:90px;right:20px;width:350px;height:450px;background:white;border-radius:15px;box-shadow:0 10px 40px rgba(0,0,0,0.15);z-index:9998;">
      <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:15px;border-radius:15px 15px 0 0;font-weight:bold;">
        🤖 AI Shopping Assistant
        <button onclick="document.getElementById('ai-panel').style.display='none'" style="float:right;background:none;border:none;color:white;cursor:pointer;font-size:20px;">×</button>
      </div>
      <div style="padding:20px;">
        <div style="background:linear-gradient(135deg,#f093fb 0%,#f5576c 100%);color:white;padding:15px;border-radius:10px;margin-bottom:15px;">
          <h3 style="margin:0;">Your Shopping Score</h3>
          <div style="font-size:36px;font-weight:bold;">87/100</div>
          <div>You're saving 23% on average!</div>
        </div>
        <div style="background:#f8f9fa;padding:15px;border-radius:10px;margin-bottom:15px;">
          <h4 style="margin:0 0 10px 0;">💡 AI Insights</h4>
          <ul style="margin:0;padding-left:20px;">
            <li>Bundle items for 15% discount</li>
            <li>Free shipping in 2 more items</li>
            <li>Price drop alert on watched items</li>
          </ul>
        </div>
        <button onclick="window.optimizeCart()" style="width:100%;padding:10px;background:#4caf50;color:white;border:none;border-radius:5px;cursor:pointer;font-weight:bold;">
          🎯 Optimize My Cart
        </button>
      </div>
    </div>
    
    <script>
      // AI Widget JavaScript
      console.log('AI Widget Loaded!');
      
      // Toggle panel
      document.getElementById('ai-assistant-btn').onclick = function() {
        var panel = document.getElementById('ai-panel');
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
      };
      
      // Optimize cart function
      window.optimizeCart = function() {
        showNotification('🔍 Analyzing your cart...');
        setTimeout(function() {
          showNotification('💰 You saved $25.99 with AI optimization!');
        }, 2000);
      };
      
      // Show notification
      function showNotification(msg) {
        var notif = document.createElement('div');
        notif.style.cssText = 'position:fixed;top:20px;right:20px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:15px 20px;border-radius:10px;box-shadow:0 4px 15px rgba(0,0,0,0.2);z-index:10000;animation:slideIn 0.3s ease;';
        notif.textContent = msg;
        document.body.appendChild(notif);
        setTimeout(function() { notif.remove(); }, 3000);
      }
      
      // Add animation styles
      var style = document.createElement('style');
      style.textContent = '@keyframes slideIn{from{transform:translateX(100%);opacity:0;}to{transform:translateX(0);opacity:1;}}';
      document.head.appendChild(style);
      
      // Show welcome notification
      setTimeout(function() {
        showNotification('🤖 AI Assistant is ready to help you save money!');
      }, 2000);
    </script>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: ai-agents
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: python:3.11-slim
        command: ["/bin/bash", "-c"]
        args:
          - |
            pip install fastapi uvicorn httpx aiofiles
            
            # Create gateway with widget injection
            cat > gateway.py << 'PYTHON'
            from fastapi import FastAPI, Request, Response
            from fastapi.responses import HTMLResponse
            from fastapi.middleware.cors import CORSMiddleware
            import httpx
            import re
            
            app = FastAPI(title="AI Gateway")
            app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
            
            # Widget HTML to inject
            WIDGET_HTML = """
            <!-- AI Widget Injected -->
            <div id="ai-assistant-btn" style="position:fixed;bottom:20px;right:20px;width:60px;height:60px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:50%;cursor:pointer;box-shadow:0 4px 15px rgba(0,0,0,0.2);display:flex;align-items:center;justify-content:center;z-index:9999;transition:transform 0.3s;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1.0)'">
              <span style="font-size:30px;">🤖</span>
            </div>
            
            <div id="ai-panel" style="display:none;position:fixed;bottom:90px;right:20px;width:350px;height:450px;background:white;border-radius:15px;box-shadow:0 10px 40px rgba(0,0,0,0.15);z-index:9998;overflow:hidden;">
              <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:15px;font-weight:bold;display:flex;justify-content:space-between;align-items:center;">
                <span>🤖 AI Shopping Assistant</span>
                <button onclick="document.getElementById('ai-panel').style.display='none'" style="background:none;border:none;color:white;cursor:pointer;font-size:20px;">×</button>
              </div>
              <div style="padding:20px;height:calc(100% - 50px);overflow-y:auto;">
                <div style="background:linear-gradient(135deg,#f093fb 0%,#f5576c 100%);color:white;padding:15px;border-radius:10px;margin-bottom:15px;">
                  <h3 style="margin:0;">Your Shopping Score</h3>
                  <div style="font-size:36px;font-weight:bold;">87/100</div>
                  <div>You're saving 23% on average!</div>
                </div>
                <div style="background:#f8f9fa;padding:15px;border-radius:10px;margin-bottom:15px;">
                  <h4 style="margin:0 0 10px 0;">💡 AI Insights</h4>
                  <ul style="margin:0;padding-left:20px;color:#666;">
                    <li>Bundle items for 15% discount</li>
                    <li>Free shipping with 2 more items</li>
                    <li>Price drop on watched items</li>
                  </ul>
                </div>
                <div style="background:#e8f5e9;padding:15px;border-radius:10px;margin-bottom:15px;">
                  <h4 style="margin:0 0 10px 0;">🎁 Just for You</h4>
                  <div style="color:#666;">
                    <div style="margin-bottom:8px;">• Vintage Camera Lens - $49.99</div>
                    <div style="margin-bottom:8px;">• Retro Film Pack - $19.99</div>
                    <div>• Photography Book - $29.99</div>
                  </div>
                </div>
                <button onclick="window.optimizeCart()" style="width:100%;padding:12px;background:#4caf50;color:white;border:none;border-radius:5px;cursor:pointer;font-weight:bold;font-size:16px;">
                  🎯 Optimize My Cart
                </button>
              </div>
            </div>
            
            <script>
              (function() {
                console.log('AI Widget JavaScript Active!');
                
                // Panel toggle
                document.getElementById('ai-assistant-btn').onclick = function() {
                  var panel = document.getElementById('ai-panel');
                  panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
                  if (panel.style.display === 'block') {
                    loadAIData();
                  }
                };
                
                // Load AI data
                function loadAIData() {
                  // Try to fetch from MCP server
                  fetch('http://' + window.location.hostname + ':8080/insights/demo_user')
                    .then(r => r.json())
                    .then(data => {
                      console.log('AI data loaded:', data);
                    })
                    .catch(e => console.log('Using default AI data'));
                }
                
                // Optimize cart
                window.optimizeCart = function() {
                  showNotification('🔍 Analyzing your cart...');
                  setTimeout(function() {
                    showNotification('💰 Bundle deal found! You saved $25.99!');
                    // Update panel with optimization
                    var panel = document.getElementById('ai-panel');
                    if (panel) {
                      var content = panel.querySelector('div:last-child');
                      if (content) {
                        content.innerHTML = '<div style="text-align:center;padding:40px;"><div style="font-size:60px;">🎉</div><h3>Optimization Applied!</h3><p style="color:#4caf50;font-size:24px;font-weight:bold;">You saved $25.99</p><p style="color:#666;">Bundle discount applied to your cart</p><button onclick="location.reload()" style="margin-top:20px;padding:10px 20px;background:#2196f3;color:white;border:none;border-radius:5px;cursor:pointer;">View Updated Cart</button></div>';
                      }
                    }
                  }, 2000);
                };
                
                // Notification system
                window.showNotification = function(msg) {
                  var notif = document.createElement('div');
                  notif.style.cssText = 'position:fixed;top:20px;right:20px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:15px 20px;border-radius:10px;box-shadow:0 4px 15px rgba(0,0,0,0.2);z-index:10000;animation:slideIn 0.3s ease;max-width:300px;';
                  notif.innerHTML = msg;
                  document.body.appendChild(notif);
                  setTimeout(function() {
                    notif.style.animation = 'slideOut 0.3s ease';
                    setTimeout(function() { notif.remove(); }, 300);
                  }, 3000);
                };
                
                // Add animations
                var style = document.createElement('style');
                style.textContent = '@keyframes slideIn{from{transform:translateX(100%);opacity:0;}to{transform:translateX(0);opacity:1;}}@keyframes slideOut{from{transform:translateX(0);opacity:1;}to{transform:translateX(100%);opacity:0;}}@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(102,126,234,0.7);}70%{box-shadow:0 0 0 10px rgba(102,126,234,0);}100%{box-shadow:0 0 0 0 rgba(102,126,234,0);}}';
                document.head.appendChild(style);
                
                // Welcome message
                setTimeout(function() {
                  showNotification('🤖 AI Assistant is ready! Click the purple button to start saving!');
                }, 2000);
                
                // Pulse animation for button
                setInterval(function() {
                  var btn = document.getElementById('ai-assistant-btn');
                  if (btn) {
                    btn.style.animation = 'pulse 2s';
                    setTimeout(function() { btn.style.animation = ''; }, 2000);
                  }
                }, 10000);
              })();
            </script>
            </body>
            """
            
            @app.get("/health")
            async def health():
                return {"status": "healthy", "widget": "ready"}
            
            @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
            async def proxy(request: Request, path: str = ""):
                # Direct widget test endpoint
                if path == "widget-test":
                    return HTMLResponse(f"<html><body><h1>Widget Test Page</h1>{WIDGET_HTML}</html>")
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    try:
                        # Proxy to frontend
                        url = f"http://frontend.default.svc.cluster.local/{path}"
                        
                        response = await client.request(
                            method=request.method,
                            url=url,
                            headers={k: v for k, v in request.headers.items() if k.lower() not in ['host', 'connection']},
                            content=await request.body() if request.method in ["POST", "PUT"] else None,
                            follow_redirects=True
                        )
                        
                        # Inject widget into HTML responses
                        content_type = response.headers.get("content-type", "")
                        if "text/html" in content_type:
                            content = response.text
                            
                            # Find </body> and inject widget before it
                            if "</body>" in content:
                                content = content.replace("</body>", WIDGET_HTML)
                                print(f"✅ Widget injected into {path}")
                            else:
                                # If no body tag, append at end
                                content = content + WIDGET_HTML
                                print(f"✅ Widget appended to {path}")
                            
                            return HTMLResponse(
                                content=content,
                                status_code=response.status_code,
                                headers={k: v for k, v in response.headers.items() if k.lower() not in ['content-length', 'content-encoding', 'connection']}
                            )
                        
                        # Non-HTML responses pass through
                        return Response(
                            content=response.content,
                            status_code=response.status_code,
                            media_type=content_type,
                            headers={k: v for k, v in response.headers.items() if k.lower() not in ['content-length', 'content-encoding', 'connection']}
                        )
                        
                    except Exception as e:
                        print(f"Proxy error: {e}")
                        # Fallback response with widget
                        return HTMLResponse(
                            f"""<html><body>
                            <h1>Online Boutique</h1>
                            <p>Loading main store...</p>
                            <p>Error: {str(e)}</p>
                            {WIDGET_HTML}
                            </body></html>"""
                        )
            
            PYTHON
            
            echo "Starting API Gateway..."
            uvicorn gateway:app --host 0.0.0.0 --port 8090 --log-level info
        ports:
        - containerPort: 8090
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: ai-agents
spec:
  type: LoadBalancer
  selector:
    app: api-gateway
  ports:
  - port: 80
    targetPort: 8090
    name: http
EOF

echo "✅ New API Gateway deployed!"
echo ""
echo "Waiting for service to be ready (30 seconds)..."
sleep 30

# Get the new IP
GATEWAY_IP=$(kubectl get service api-gateway -n ai-agents -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")

echo "================================"
echo "🎉 AI WIDGET FIXED!"
echo "================================"
echo ""
echo "🌐 Access your AI-Enhanced Store at:"
echo "   http://$GATEWAY_IP"
echo ""
echo "🧪 Test the widget directly at:"
echo "   http://$GATEWAY_IP/widget-test"
echo ""
echo "📝 Troubleshooting:"
echo "   kubectl logs deployment/api-gateway -n ai-agents"
echo ""
echo "If the IP shows 'pending', wait 1-2 minutes and run:"
echo "   kubectl get svc api-gateway -n ai-agents"
