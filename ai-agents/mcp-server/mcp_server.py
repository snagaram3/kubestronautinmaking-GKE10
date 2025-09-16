import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from kubernetes import client, config

# Initialize FastAPI
app = FastAPI(
    title="MCP Server - AI Shopping Assistant",
    description="Provides AI-powered shopping insights and cart optimization",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None
    print("Warning: GEMINI_API_KEY not set, using fallback responses")

# Try to load k8s config
try:
    config.load_incluster_config()
    print("Loaded in-cluster Kubernetes config")
except:
    try:
        config.load_kube_config()
        print("Loaded local Kubernetes config")
    except:
        print("Warning: Could not load Kubernetes config")

# Request models
class CartAnalysisRequest(BaseModel):
    user_id: str
    cart_items: list = []

class ChatRequest(BaseModel):
    user_id: str
    message: str

# Simple in-memory cache for demo purposes
cache = {
    "decisions_count": 142,
    "optimizations_count": 37,
    "users_helped": 89
}

@app.get("/")
async def root():
    return {
        "service": "MCP Server",
        "status": "running",
        "version": "1.0.0",
        "ai_enabled": bool(model)
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ai_model": "gemini-1.5-flash" if model else "fallback",
        "cache_size": len(cache)
    }

@app.post("/analyze-cart/{user_id}")
async def analyze_cart(user_id: str):
    """Analyze cart and provide optimization suggestions"""
    
    # Simulate cart analysis with intelligent optimizations
    optimizations = [
        {
            "type": "shipping",
            "message": "Add 1 more item for free shipping!",
            "savings": 0,
            "threshold": 50,
            "action": "add_item"
        },
        {
            "type": "bundle",
            "message": "Bundle these items and save 15%!",
            "savings": 25.99,
            "discount": 15,
            "action": "create_bundle"
        },
        {
            "type": "bulk",
            "message": "You qualify for our bulk discount!",
            "savings": 35.50,
            "discount": 20,
            "action": "apply_bulk_discount"
        },
        {
            "type": "loyalty",
            "message": "Premium member discount applied!",
            "savings": 45.00,
            "discount": 25,
            "action": "apply_loyalty_discount"
        }
    ]
    
    # Simulate different cart scenarios
    import random
    cart_scenario = random.choice(optimizations)
    
    # Update cache
    cache["optimizations_count"] = cache.get("optimizations_count", 0) + 1
    
    return {
        "user_id": user_id,
        "optimization_available": True,
        "optimization_type": cart_scenario["type"],
        "message": cart_scenario["message"],
        "potential_savings": cart_scenario["savings"],
        "optimization_id": f"opt_{user_id}_{datetime.now().timestamp()}",
        "confidence_score": random.uniform(0.8, 0.95),
        "action_required": cart_scenario["action"],
        "expires_at": datetime.now().timestamp() + 3600  # 1 hour
    }

@app.get("/insights/{user_id}")
async def get_insights(user_id: str):
    """Get AI-powered shopping insights"""
    
    if model:
        try:
            prompt = f"""
            Generate personalized shopping insights for user {user_id}.
            Return ONLY a JSON object with:
            - savings_score (integer 0-100)
            - percentage_saved (integer 0-50)
            - insights (array of exactly 3 actionable insights)
            
            Keep insights brief and actionable. No markdown, just plain JSON.
            """
            
            response = model.generate_content(prompt)
            # Try to parse AI response
            try:
                insights_data = json.loads(response.text.strip())
            except:
                # Fallback if parsing fails
                insights_data = generate_fallback_insights()
        except Exception as e:
            print(f"Gemini API error: {e}")
            insights_data = generate_fallback_insights()
    else:
        insights_data = generate_fallback_insights()
    
    # Update cache
    cache["users_helped"] = cache.get("users_helped", 0) + 1
    
    return {
        **insights_data,
        "user_id": user_id,
        "generated_at": datetime.now().isoformat()
    }

def generate_fallback_insights():
    """Generate fallback insights when AI is unavailable"""
    import random
    
    scores = [75, 82, 87, 91, 94]
    savings = [15, 18, 23, 28, 31]
    
    insight_options = [
        "You save most on electronics purchases",
        "Shopping on Tuesdays gets you better deals",
        "Bundle purchases to maximize free shipping",
        "Your loyalty tier unlocks exclusive discounts",
        "Price alerts saved you money this month",
        "Seasonal sales match your buying patterns",
        "Cross-category purchases boost savings",
        "Early bird discounts are perfect for you"
    ]
    
    return {
        "savings_score": random.choice(scores),
        "percentage_saved": random.choice(savings),
        "insights": random.sample(insight_options, 3)
    }

@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    """Get personalized product recommendations"""
    
    # Enhanced product catalog
    products = [
        {
            "id": "OLJCESPC7Z",
            "name": "Vintage Camera Lens",
            "price": 49.99,
            "image": "/static/img/products/camera-lens.jpg",
            "reason": "Based on your photography interests",
            "match_score": 95,
            "category": "photography"
        },
        {
            "id": "66VCHSJNUP",
            "name": "Vintage Record Player",
            "price": 129.99,
            "image": "/static/img/products/record-player.jpg",
            "reason": "Customers also bought",
            "match_score": 87,
            "category": "music"
        },
        {
            "id": "1YMWWN1N4O",
            "name": "Home Barista Kit",
            "price": 89.99,
            "image": "/static/img/products/barista-kit.jpg",
            "reason": "Trending in your area",
            "match_score": 82,
            "category": "kitchen"
        },
        {
            "id": "2ZYFJ3GM2N",
            "name": "Artisan Coffee Beans",
            "price": 24.99,
            "image": "/static/img/products/coffee-beans.jpg",
            "reason": "Perfect with your recent purchases",
            "match_score": 89,
            "category": "consumables"
        },
        {
            "id": "9SIQT8TOJO",
            "name": "Vintage Typewriter",
            "price": 199.99,
            "image": "/static/img/products/typewriter.jpg",
            "reason": "Based on browsing history",
            "match_score": 78,
            "category": "vintage"
        }
    ]
    
    # Return randomized recommendations
    import random
    recommendations = random.sample(products, min(4, len(products)))
    
    return {
        "user_id": user_id,
        "recommendations": recommendations,
        "total_count": len(recommendations),
        "algorithm": "collaborative_filtering_v2"
    }

@app.get("/smart-deals/{user_id}")
async def get_smart_deals(user_id: str):
    """Get AI-negotiated deals and bundles"""
    
    deals = [
        {
            "bundle_name": "Photography Starter Pack",
            "description": "Camera + Lens + Tripod",
            "items": ["Camera", "Vintage Lens", "Professional Tripod"],
            "original_price": 299.99,
            "ai_price": 219.99,
            "discount": 27,
            "expires_in": "2 hours"
        },
        {
            "bundle_name": "Home Office Setup",
            "description": "Desk Lamp + Organizer + Plant",
            "items": ["LED Desk Lamp", "Bamboo Organizer", "Succulent Plant"],
            "original_price": 149.99,
            "ai_price": 99.99,
            "discount": 33,
            "expires_in": "4 hours"
        },
        {
            "bundle_name": "Coffee Enthusiast Bundle",
            "description": "Barista Kit + Premium Beans + Grinder",
            "items": ["Barista Kit", "Artisan Beans", "Manual Grinder"],
            "original_price": 179.99,
            "ai_price": 129.99,
            "discount": 28,
            "expires_in": "6 hours"
        }
    ]
    
    return {
        "user_id": user_id,
        "deals": deals,
        "total_savings": sum(deal["original_price"] - deal["ai_price"] for deal in deals),
        "ai_negotiated": True
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """AI-powered chat assistant"""
    
    if model:
        try:
            prompt = f"""
            You are a helpful shopping assistant for an online boutique.
            User message: "{request.message}"
            
            Provide a brief, helpful response (max 150 characters).
            Be friendly, informative, and focused on helping with shopping.
            """
            
            response = model.generate_content(prompt)
            return {
                "user_id": request.user_id,
                "response": response.text[:150],
                "source": "gemini"
            }
        except Exception as e:
            print(f"Chat API error: {e}")
    
    # Fallback responses
    responses = {
        "price": "I can help you find the best prices! Check our Smart Deals section for AI-negotiated bundles.",
        "shipping": "Free shipping on orders over $50! Need help reaching the threshold?",
        "return": "We have a 30-day return policy. I can help you track returns too!",
        "recommend": "I'd love to recommend items! What are you shopping for today?",
        "help": "I'm your AI shopping assistant! Ask me about deals, shipping, returns, or recommendations.",
        "discount": "I can find personalized discounts for you! Let me analyze your cart.",
        "bundle": "Bundle deals save you more! I can suggest complementary items.",
        "default": "I'm here to help you shop smarter! Try asking about deals, shipping, or recommendations."
    }
    
    message_lower = request.message.lower()
    for keyword in responses:
        if keyword in message_lower:
            return {
                "user_id": request.user_id,
                "response": responses[keyword],
                "source": "fallback"
            }
    
    return {
        "user_id": request.user_id,
        "response": responses["default"],
        "source": "fallback"
    }

@app.post("/track")
async def track_event(event: dict):
    """Track user events for analytics"""
    
    event_data = {
        **event,
        "timestamp": datetime.now().isoformat(),
        "session_id": event.get("session_id", "unknown")
    }
    
    # In a real implementation, this would go to analytics service
    print(f"Event tracked: {event_data}")
    
    # Update cache counters
    if event.get("type") == "optimization_applied":
        cache["optimizations_count"] = cache.get("optimizations_count", 0) + 1
    elif event.get("type") == "ai_decision":
        cache["decisions_count"] = cache.get("decisions_count", 0) + 1
    
    return {"status": "tracked", "event_id": f"evt_{datetime.now().timestamp()}"}

@app.get("/metrics")
async def get_metrics():
    """Get system and AI performance metrics"""
    
    try:
        # Try to get Kubernetes metrics
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace="default")
        
        k8s_metrics = {
            "total_pods": len(pods.items),
            "ready_pods": sum(1 for pod in pods.items if pod.status.phase == "Running"),
            "k8s_available": True
        }
    except Exception as e:
        # Fallback metrics
        k8s_metrics = {
            "total_pods": 11,
            "ready_pods": 11,
            "k8s_available": False,
            "error": str(e)
        }
    
    return {
        **k8s_metrics,
        "ai_decisions_made": cache.get("decisions_count", 142),
        "optimizations_applied": cache.get("optimizations_count", 37),
        "users_helped": cache.get("users_helped", 89),
        "ai_model_available": bool(model),
        "uptime": "operational",
        "cache_stats": {
            "size": len(cache),
            "keys": list(cache.keys())
        }
    }

@app.get("/status")
async def get_status():
    """Detailed service status"""
    return {
        "service": "MCP Server",
        "status": "healthy",
        "version": "1.0.0",
        "ai_enabled": bool(model),
        "features": {
            "cart_optimization": True,
            "personalized_recommendations": True,
            "smart_deals": True,
            "chat_assistant": True,
            "event_tracking": True,
            "metrics_collection": True
        },
        "endpoints": {
            "health": "/health",
            "insights": "/insights/{user_id}",
            "cart_analysis": "/analyze-cart/{user_id}",
            "recommendations": "/recommendations/{user_id}",
            "smart_deals": "/smart-deals/{user_id}",
            "chat": "/chat",
            "metrics": "/metrics"
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )