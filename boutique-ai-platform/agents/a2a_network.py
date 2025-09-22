from fastapi import FastAPI, WebSocket, HTTPException
from typing import Dict, List, Set
import asyncio
import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class AgentMessage:
    id: str
    content: str
    sender_agent: str
    target_agent: str
    conversation_id: str
    timestamp: str
    message_type: str = "request"

class A2ANetwork:
    def __init__(self):
        self.registered_agents: Dict[str, WebSocket] = {}
        self.message_history: List[AgentMessage] = []
        
    async def register_agent(self, agent_id: str, websocket: WebSocket):
        """Register an agent with the A2A network"""
        await websocket.accept()
        self.registered_agents[agent_id] = websocket
        print(f"Agent {agent_id} registered with A2A network")
        
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                message_data = json.loads(data)
                await self.route_message(message_data)
        except Exception as e:
            print(f"Agent {agent_id} disconnected: {e}")
        finally:
            if agent_id in self.registered_agents:
                del self.registered_agents[agent_id]
    
    async def route_message(self, message_data: Dict):
        """Route message between agents"""
        message = AgentMessage(**message_data)
        self.message_history.append(message)
        
        target_agent = message.target_agent
        if target_agent in self.registered_agents:
            target_socket = self.registered_agents[target_agent]
            await target_socket.send_text(json.dumps(asdict(message)))
        else:
            print(f"Target agent {target_agent} not found")
    
    async def send_message(self, sender: str, target: str, content: str, conversation_id: str) -> str:
        """Send message and wait for response"""
        message_id = str(uuid.uuid4())
        message = AgentMessage(
            id=message_id,
            content=content,
            sender_agent=sender,
            target_agent=target,
            conversation_id=conversation_id,
            timestamp=datetime.now().isoformat()
        )
        
        if target in self.registered_agents:
            target_socket = self.registered_agents[target]
            await target_socket.send_text(json.dumps(asdict(message)))
            
            # Wait for response (simplified - in production, use proper async handling)
            return f"Response from {target}"
        else:
            raise HTTPException(status_code=404, detail=f"Agent {target} not available")

app = FastAPI(title="A2A Communication Network")
a2a_network = A2ANetwork()

@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for agent registration"""
    await a2a_network.register_agent(agent_id, websocket)

@app.post("/send_message")
async def send_message(
    sender: str,
    target: str,
    content: str,
    conversation_id: str
):
    """HTTP endpoint for sending messages between agents"""
    return await a2a_network.send_message(sender, target, content, conversation_id)

@app.get("/agents")
async def list_agents():
    """List all registered agents"""
    return {"registered_agents": list(a2a_network.registered_agents.keys())}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "A2A Network"}
