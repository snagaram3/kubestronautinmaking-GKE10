from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import asyncio
from typing import Dict

class ChatRequest(BaseModel):
    message: str
    conversation_id: str

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

app = FastAPI(title="AI Chat API Gateway")

class ChatGateway:
    def __init__(self):
        self.customer_service_endpoint = "http://customer-service-agent:8080"
        
    async def process_chat_message(self, request: ChatRequest) -> ChatResponse:
        """Process incoming chat message and route to appropriate agent"""
        
        try:
            # Send to Customer Service Agent (primary orchestrator)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.customer_service_endpoint}/chat",
                    json={
                        "query": request.message,
                        "conversation_id": request.conversation_id
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return ChatResponse(
                        response=result["response"],
                        conversation_id=request.conversation_id
                    )
                else:
                    raise HTTPException(status_code=500, detail="Agent processing failed")
                    
        except Exception as e:
            # Fallback response
            return ChatResponse(
                response="I'm sorry, I'm having trouble processing your request right now. Please try again or contact customer support.",
                conversation_id=request.conversation_id
            )

gateway = ChatGateway()

@app.post("/api/ai-chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for frontend widget"""
    return await gateway.process_chat_message(request)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Chat API Gateway"}

# Serve static files for chat widget
from fastapi.staticfiles import StaticFiles
app.mount("/static/ai-chat", StaticFiles(directory="frontend-widget/src"), name="ai-chat")
