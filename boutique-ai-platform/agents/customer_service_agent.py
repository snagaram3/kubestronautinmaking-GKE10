import asyncio
import json
import os
import logging
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import httpx
import grpc
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import gRPC stubs
sys.path.append('/app/protos')
try:
    import demo_pb2
    import demo_pb2_grpc
    GRPC_AVAILABLE = True
except ImportError as e:
    logger.error(f"gRPC imports failed: {e}")
    GRPC_AVAILABLE = False

# Import Gemini AI
try:
    import google.generativeai as genai
    GOOGLE_AI_KEY = os.getenv('GOOGLE_AI_KEY')
    if GOOGLE_AI_KEY:
        genai.configure(api_key=GOOGLE_AI_KEY)
        GEMINI_AVAILABLE = True
    else:
        GEMINI_AVAILABLE = False
except ImportError:
    GEMINI_AVAILABLE = False

class ChatRequest(BaseModel):
    query: str
    conversation_id: str

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    agent: str = "customer-service"
    intent: str = "general"

class CustomerServiceAgent:
    def __init__(self):
        self.agent_id = "customer-service-agent"
        self.http_client = httpx.AsyncClient()
        
        # gRPC connections
        self.grpc_channels = {}
        self.grpc_stubs = {}
        
        # MCP server endpoints
        self.mcp_servers = {
            "product-catalog": "http://product-catalog-mcp:8080"
        }
        
        # Microservice endpoints
        self.microservices = {
            "productcatalog": "productcatalogservice:3550",
            "cart": "cartservice:7070"
        }
        
    async def initialize_connections(self):
        """Initialize all connections"""
        await self._initialize_grpc_connections()
        await self._test_mcp_connections()
        
    async def _initialize_grpc_connections(self):
        """Initialize direct gRPC connections to microservices"""
        if not GRPC_AVAILABLE:
            return
            
        for service_name, endpoint in self.microservices.items():
            try:
                channel = grpc.aio.insecure_channel(endpoint)
                await asyncio.wait_for(channel.channel_ready(), timeout=5.0)
                
                self.grpc_channels[service_name] = channel
                
                if service_name == "productcatalog":
                    self.grpc_stubs[service_name] = demo_pb2_grpc.ProductCatalogServiceStub(channel)
                elif service_name == "cart":
                    self.grpc_stubs[service_name] = demo_pb2_grpc.CartServiceStub(channel)
                    
                logger.info(f"Connected to {service_name} via gRPC")
            except Exception as e:
                logger.error(f"Failed to connect to {service_name}: {e}")
    
    async def _test_mcp_connections(self):
        """Test MCP server connections"""
        for server_name, base_url in self.mcp_servers.items():
            try:
                response = await self.http_client.get(f"{base_url}/health", timeout=5.0)
                if response.status_code == 200:
                    logger.info(f"MCP server {server_name} is healthy")
                else:
                    logger.warning(f"MCP server {server_name} returned {response.status_code}")
            except Exception as e:
                logger.error(f"Cannot reach MCP server {server_name}: {e}")
    
    async def get_products_direct_grpc(self) -> List[Dict]:
        """Get products directly from productcatalogservice"""
        if "productcatalog" not in self.grpc_stubs:
            logger.warning("ProductCatalog gRPC stub not available")
            return []
            
        try:
            stub = self.grpc_stubs["productcatalog"]
            request = demo_pb2.Empty()
            response = await asyncio.wait_for(stub.ListProducts(request), timeout=10.0)
            
            products = []
            for product in response.products:
                products.append({
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "picture": product.picture,
                    "price": {
                        "currency_code": product.price_usd.currency_code,
                        "units": product.price_usd.units,
                        "nanos": product.price_usd.nanos
                    },
                    "categories": list(product.categories)
                })
            
            logger.info(f"Retrieved {len(products)} products via direct gRPC")
            return products
            
        except Exception as e:
            logger.error(f"Error getting products via gRPC: {e}")
            return []
    
    async def get_products_via_mcp(self) -> List[Dict]:
        """Get products via MCP server"""
        try:
            response = await self.http_client.post(
                f"{self.mcp_servers['product-catalog']}/list_products",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Retrieved products via MCP: {len(data.get('products', []))} items")
                return data.get("products", [])
        except Exception as e:
            logger.error(f"Error getting products via MCP: {e}")
        return []
    
    async def get_all_products(self) -> List[Dict]:
        """Get products using best available method"""
        # Try direct gRPC first
        products = await self.get_products_direct_grpc()
        if products:
            return products
            
        # Fallback to MCP
        products = await self.get_products_via_mcp()
        if products:
            return products
            
        # Final fallback
        return self._get_fallback_products()
    
    def _get_fallback_products(self) -> List[Dict]:
        """Fallback products"""
        return [
            {"id": "OLJCESPC7Z", "name": "Sunglasses", "description": "Stylish sunglasses", 
             "price": {"currency_code": "USD", "units": 19, "nanos": 990000000}},
            {"id": "66VCHSJNUP", "name": "Tank Top", "description": "Cotton tank top",
             "price": {"currency_code": "USD", "units": 18, "nanos": 990000000}},
            {"id": "1YMWWN1N4O", "name": "Watch", "description": "Gold-tone watch",
             "price": {"currency_code": "USD", "units": 109, "nanos": 990000000}}
        ]
    
    async def add_to_cart_direct_grpc(self, user_id: str, product_id: str, quantity: int = 1) -> bool:
        """Add item to cart via direct gRPC"""
        if "cart" not in self.grpc_stubs:
            logger.warning("Cart gRPC stub not available")
            return False
            
        try:
            stub = self.grpc_stubs["cart"]
            cart_item = demo_pb2.CartItem(product_id=product_id, quantity=quantity)
            request = demo_pb2.AddItemRequest(user_id=user_id, item=cart_item)
            
            await asyncio.wait_for(stub.AddItem(request), timeout=5.0)
            logger.info(f"Added {product_id} to cart for {user_id} via gRPC")
            return True
            
        except Exception as e:
            logger.error(f"Error adding to cart via gRPC: {e}")
            return False
    
    async def get_cart_direct_grpc(self, user_id: str) -> Dict:
        """Get cart via direct gRPC"""
        if "cart" not in self.grpc_stubs:
            return {"items": [], "total": 0}
            
        try:
            stub = self.grpc_stubs["cart"]
            request = demo_pb2.GetCartRequest(user_id=user_id)
            response = await asyncio.wait_for(stub.GetCart(request), timeout=5.0)
            
            items = []
            for item in response.items:
                items.append({"product_id": item.product_id, "quantity": item.quantity})
            
            return {"items": items, "total": len(items)}
            
        except Exception as e:
            logger.error(f"Error getting cart via gRPC: {e}")
            return {"items": [], "total": 0}
    
    def classify_intent(self, query: str) -> str:
        """Improved intent classification"""
        query_lower = query.lower().strip()
        
        # Cart management keywords
        cart_keywords = [
            "cart", "add", "buy", "purchase", "show cart", "view cart", 
            "my cart", "what's in my cart", "whats in my cart", "checkout"
        ]
        
        # Product search keywords  
        product_keywords = [
            "product", "find", "search", "show", "recommend", "looking",
            "available", "catalog", "list", "browse"
        ]
        
        # Check for cart intent
        if any(keyword in query_lower for keyword in cart_keywords):
            return "cart_management"
            
        # Check for product search intent
        if any(keyword in query_lower for keyword in product_keywords):
            return "product_search"
        
        # Check if query is just a product name
        products = self._get_fallback_products()  # Quick check with known products
        for product in products:
            if product["name"].lower() in query_lower:
                return "cart_management"  # Assume they want to add it
                
        return "general"
    
    async def handle_query(self, query: str, conversation_id: str) -> Dict:
        """Main query handler"""
        intent = self.classify_intent(query)
        logger.info(f"Query: '{query}' -> Intent: '{intent}'")
        
        if intent == "cart_management":
            if any(word in query.lower() for word in ["add", "buy", "purchase"]) or self._is_product_name(query):
                response = await self._handle_add_to_cart(query, conversation_id)
            elif any(word in query.lower() for word in ["show", "view", "cart"]):
                response = await self._handle_show_cart(conversation_id)
            else:
                response = "I can help you add items to your cart or show your current cart. What would you like to do?"
        elif intent == "product_search":
            response = await self._handle_product_search(query)
        else:
            response = await self._handle_general_query(query)
        
        return {
            "response": response,
            "intent": intent,
            "agent": self.agent_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def _is_product_name(self, query: str) -> bool:
        """Check if query is just a product name"""
        query_lower = query.lower().strip()
        product_names = ["sunglasses", "tank top", "watch", "hairdryer", "loafers"]
        return query_lower in product_names
    
    async def _handle_add_to_cart(self, query: str, conversation_id: str) -> str:
        """Handle add to cart requests"""
        products = await self.get_all_products()
        query_lower = query.lower()
        
        # Find matching product
        matched_product = None
        for product in products:
            product_words = product["name"].lower().split()
            if any(word in query_lower for word in product_words) or product["name"].lower() in query_lower:
                matched_product = product
                break
        
        if matched_product:
            success = await self.add_to_cart_direct_grpc(conversation_id, matched_product["id"], 1)
            if success:
                price = matched_product["price"]["units"] + (matched_product["price"]["nanos"] / 1e9)
                return f"Successfully added {matched_product['name']} (${price:.2f}) to your cart! The item has been added to your actual shopping cart."
            else:
                return f"I found {matched_product['name']} but couldn't add it to your cart. The cart service may be temporarily unavailable."
        else:
            available_products = [p["name"] for p in products[:5]]
            return f"I can add these products to your cart: {', '.join(available_products)}. Which would you like?"
    
    async def _handle_show_cart(self, conversation_id: str) -> str:
        """Handle show cart requests"""
        cart = await self.get_cart_direct_grpc(conversation_id)
        
        if cart["total"] == 0:
            return "Your cart is empty. Would you like to browse our products?"
        
        products = await self.get_all_products()
        product_dict = {p["id"]: p for p in products}
        
        response = f"Your cart contains {cart['total']} items:\n"
        total_cost = 0
        
        for item in cart["items"]:
            if item["product_id"] in product_dict:
                product = product_dict[item["product_id"]]
                price = product["price"]["units"] + (product["price"]["nanos"] / 1e9)
                item_total = price * item["quantity"]
                total_cost += item_total
                response += f"- {product['name']} x{item['quantity']} = ${item_total:.2f}\n"
        
        response += f"\nTotal: ${total_cost:.2f}"
        return response
    
    async def _handle_product_search(self, query: str = "") -> str:
        """Handle product search requests"""
        products = await self.get_all_products()
        
        if not products:
            return "I'm having trouble accessing our product catalog right now. Please try again in a moment."
        
        response = f"Here are our available products ({len(products)} items):\n\n"
        for product in products:
            price = product["price"]["units"] + (product["price"]["nanos"] / 1e9)
            response += f"- **{product['name']}**: ${price:.2f}\n  {product['description']}\n\n"
        
        response += "To add any item to your cart, just say 'add [product name] to cart'!"
        return response
    
    async def _handle_general_query(self, query: str) -> str:
        """Handle general queries"""
        if GEMINI_AVAILABLE:
            try:
                model = genai.GenerativeModel('gemini-pro')
                ai_prompt = f"You are a helpful customer service agent for an online boutique. Respond to: '{query}'. Be helpful and mention you can help with products and cart management."
                ai_response = model.generate_content(ai_prompt)
                return ai_response.text
            except Exception as e:
                logger.error(f"Gemini AI error: {e}")
        
        return "Hello! I'm your customer service assistant. I can help you find products, manage your cart, and answer questions. How can I assist you today?"

# Global agent
agent = CustomerServiceAgent()

# FastAPI app
app = FastAPI(title="Customer Service Agent")

@app.on_event("startup")
async def startup_event():
    await agent.initialize_connections()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "grpc_available": GRPC_AVAILABLE,
        "gemini_available": GEMINI_AVAILABLE
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    try:
        result = await agent.handle_query(chat_request.query, chat_request.conversation_id)
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
