import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# Initialize FastAPI
app = FastAPI(
    title="A2A Orchestrator - Multi-Agent Workflow Engine",
    description="Orchestrates agent-to-agent communication for complex AI operations",
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
    print("Warning: GEMINI_API_KEY not set, using simplified agent responses")

# WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Agent simulation classes
class SimpleAgent:
    def __init__(self, name: str, role: str, capabilities: List[str]):
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.message_count = 0
        self.success_rate = 0.9
        self.average_response_time = 0.5
        self.last_activity = datetime.now()
    
    async def process(self, task: str, context: Dict = None) -> Dict:
        """Simulate agent processing with role-specific behavior"""
        self.message_count += 1
        self.last_activity = datetime.now()
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        if self.role == "pricing":
            return self._process_pricing(task, context)
        elif self.role == "inventory":
            return self._process_inventory(task, context)
        elif self.role == "customer":
            return self._process_customer(task, context)
        elif self.role == "fraud":
            return self._process_fraud(task, context)
        elif self.role == "personalization":
            return self._process_personalization(task, context)
        else:
            return {
                "agent": self.name,
                "action": "generic_process",
                "result": f"Processed {task}",
                "confidence": 0.8,
                "processing_time": 0.5
            }
    
    def _process_pricing(self, task: str, context: Dict) -> Dict:
        import random
        
        discount_scenarios = [
            {"discount": 15, "reason": "Competitor price matching", "confidence": 0.87},
            {"discount": 20, "reason": "Volume discount eligible", "confidence": 0.92},
            {"discount": 10, "reason": "Loyalty tier bonus", "confidence": 0.95},
            {"discount": 25, "reason": "Bundle optimization", "confidence": 0.89}
        ]
        
        scenario = random.choice(discount_scenarios)
        
        return {
            "agent": self.name,
            "action": "price_optimization",
            "result": f"Optimized pricing for {task}",
            "discount_percentage": scenario["discount"],
            "optimization_reason": scenario["reason"],
            "confidence": scenario["confidence"],
            "estimated_savings": random.uniform(15.0, 75.0),
            "price_valid_until": datetime.now().timestamp() + 3600
        }
    
    def _process_inventory(self, task: str, context: Dict) -> Dict:
        import random
        
        return {
            "agent": self.name,
            "action": "inventory_analysis",
            "result": f"Inventory analyzed for {task}",
            "stock_level": random.randint(5, 150),
            "reorder_needed": random.choice([True, False]),
            "demand_forecast": random.uniform(0.3, 1.8),
            "availability_score": random.uniform(0.7, 1.0),
            "recommended_action": random.choice([
                "maintain_current_stock",
                "increase_inventory",
                "reduce_inventory",
                "create_backorder"
            ])
        }
    
    def _process_customer(self, task: str, context: Dict) -> Dict:
        import random
        
        segments = ["premium", "regular", "new_customer", "at_risk", "loyal"]
        behaviors = ["price_sensitive", "quality_focused", "convenience_oriented", "brand_loyal"]
        
        return {
            "agent": self.name,
            "action": "customer_analysis",
            "result": f"Customer profile analyzed for {task}",
            "segment": random.choice(segments),
            "behavior_pattern": random.choice(behaviors),
            "lifetime_value": random.randint(500, 5000),
            "churn_risk": random.uniform(0.1, 0.4),
            "recommended_engagement": random.choice([
                "send_personalized_offer",
                "schedule_follow_up",
                "provide_loyalty_rewards",
                "offer_premium_upgrade"
            ])
        }
    
    def _process_fraud(self, task: str, context: Dict) -> Dict:
        import random
        
        return {
            "agent": self.name,
            "action": "fraud_assessment",
            "result": f"Security analysis for {task}",
            "risk_score": random.uniform(0.1, 0.9),
            "risk_factors": random.sample([
                "unusual_location",
                "high_velocity_transactions",
                "new_payment_method",
                "suspicious_device",
                "velocity_anomaly"
            ], 2),
            "recommendation": random.choice([
                "approve_transaction",
                "request_additional_verification",
                "flag_for_manual_review",
                "decline_transaction"
            ]),
            "confidence": random.uniform(0.8, 0.95)
        }
    
    def _process_personalization(self, task: str, context: Dict) -> Dict:
        import random
        
        return {
            "agent": self.name,
            "action": "personalization_engine",
            "result": f"Personalization generated for {task}",
            "recommendation_strength": random.uniform(0.6, 0.95),
            "content_type": random.choice([
                "product_recommendations",
                "content_curation",
                "pricing_personalization",
                "experience_optimization"
            ]),
            "target_segments": random.sample([
                "high_value_customers",
                "frequent_buyers",
                "seasonal_shoppers",
                "mobile_users"
            ], 2),
            "expected_engagement_lift": random.uniform(0.15, 0.45)
        }

# Initialize agents with enhanced capabilities
agents = {
    "pricing_agent": SimpleAgent(
        "pricing_agent", 
        "pricing", 
        ["dynamic_pricing", "competitor_analysis", "discount_optimization"]
    ),
    "inventory_agent": SimpleAgent(
        "inventory_agent", 
        "inventory", 
        ["stock_management", "demand_forecasting", "supply_optimization"]
    ),
    "customer_agent": SimpleAgent(
        "customer_agent", 
        "customer", 
        ["profile_analysis", "behavior_prediction", "segmentation"]
    ),
    "fraud_agent": SimpleAgent(
        "fraud_agent", 
        "fraud", 
        ["risk_assessment", "transaction_monitoring", "pattern_detection"]
    ),
    "personalization_agent": SimpleAgent(
        "personalization_agent", 
        "personalization", 
        ["content_curation", "recommendation_engine", "experience_optimization"]
    )
}

# Workflow tracking
workflow_history = []
workflow_templates = {
    "customer_optimization": {
        "name": "Customer Experience Optimization",
        "description": "Comprehensive customer analysis and experience enhancement",
        "agents": ["customer_agent", "personalization_agent", "pricing_agent"],
        "steps": ["analyze_customer", "generate_recommendations", "optimize_pricing"]
    },
    "fraud_detection": {
        "name": "Fraud Detection and Prevention",
        "description": "Multi-layer fraud analysis and risk assessment",
        "agents": ["fraud_agent", "customer_agent"],
        "steps": ["assess_risk", "analyze_behavior", "make_decision"]
    },
    "inventory_optimization": {
        "name": "Inventory Management Optimization",
        "description": "Smart inventory management and demand forecasting",
        "agents": ["inventory_agent", "pricing_agent"],
        "steps": ["analyze_stock", "forecast_demand", "optimize_pricing"]
    },
    "price_adjustment": {
        "name": "Dynamic Price Adjustment",
        "description": "Real-time pricing optimization based on market conditions",
        "agents": ["pricing_agent", "inventory_agent", "customer_agent"],
        "steps": ["analyze_market", "assess_inventory", "segment_customers", "set_prices"]
    }
}

# Request models
class WorkflowRequest(BaseModel):
    user_id: Optional[str] = None
    parameters: Dict = {}
    priority: str = "normal"

class AgentMessage(BaseModel):
    from_agent: str
    to_agent: str
    message_type: str
    payload: Dict
    correlation_id: str

@app.get("/")
async def root():
    return {
        "service": "A2A Orchestrator",
        "status": "operational",
        "version": "1.0.0",
        "active_agents": list(agents.keys()),
        "available_workflows": list(workflow_templates.keys())
    }

@app.get("/status")
async def get_status():
    """Get comprehensive system status"""
    return {
        "system_status": "operational",
        "active_agents": len(agents),
        "active_connections": len(active_connections),
        "total_workflows_executed": len(workflow_history),
        "agents": {
            name: {
                "status": "active",
                "messages_processed": agent.message_count,
                "success_rate": agent.success_rate,
                "avg_response_time": agent.average_response_time,
                "last_activity": agent.last_activity.isoformat(),
                "capabilities": agent.capabilities
            }
            for name, agent in agents.items()
        },
        "workflow_templates": workflow_templates,
        "ai_model_available": bool(model)
    }

@app.get("/workflows")
async def list_workflows():
    """List available workflow templates"""
    return {
        "templates": workflow_templates,
        "custom_workflows_supported": True,
        "execution_history": len(workflow_history)
    }

@app.post("/workflow/{workflow_name}")
async def execute_workflow(workflow_name: str, request: WorkflowRequest = WorkflowRequest()):
    """Execute a predefined or custom workflow"""
    
    if workflow_name not in workflow_templates:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_name}' not found")
    
    template = workflow_templates[workflow_name]
    workflow_id = f"{workflow_name}_{datetime.now().timestamp()}"
    results = []
    
    try:
        # Execute workflow based on template
        for i, agent_name in enumerate(template["agents"]):
            if agent_name not in agents:
                continue
                
            agent = agents[agent_name]
            step_context = {
                "workflow_id": workflow_id,
                "step": i + 1,
                "total_steps": len(template["agents"]),
                "user_id": request.user_id,
                "parameters": request.parameters,
                "previous_results": results
            }
            
            # Execute agent processing
            result = await agent.process(f"{workflow_name}_step_{i+1}", step_context)
            results.append(result)
            
            # Broadcast progress to WebSocket clients
            await broadcast_update({
                "type": "workflow_progress",
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "agent": agent_name,
                "step": i + 1,
                "total_steps": len(template["agents"]),
                "status": "completed",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Small delay between agents for realism
            await asyncio.sleep(0.2)
        
        # Generate workflow summary
        summary = await generate_workflow_summary(workflow_name, results)
        
        # Store in history
        workflow_record = {
            "id": workflow_id,
            "name": workflow_name,
            "template": template,
            "timestamp": datetime.now().isoformat(),
            "user_id": request.user_id,
            "parameters": request.parameters,
            "results": results,
            "summary": summary,
            "status": "completed",
            "duration": len(template["agents"]) * 0.2  # Approximate duration
        }
        
        workflow_history.append(workflow_record)
        
        # Broadcast completion
        await broadcast_update({
            "type": "workflow_completed",
            "workflow_id": workflow_id,
            "summary": summary,
            "total_agents": len(results),
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "template": template,
            "agents_involved": len(results),
            "summary": summary,
            "results": results,
            "execution_time": len(template["agents"]) * 0.2
        }
        
    except Exception as e:
        # Handle workflow errors
        error_record = {
            "id": workflow_id,
            "name": workflow_name,
            "timestamp": datetime.now().isoformat(),
            "status": "failed",
            "error": str(e),
            "partial_results": results
        }
        workflow_history.append(error_record)
        
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

async def generate_workflow_summary(workflow_name: str, results: List[Dict]) -> str:
    """Generate AI-powered workflow summary"""
    
    if model:
        try:
            prompt = f"""
            Summarize this workflow execution in one clear sentence:
            Workflow: {workflow_name}
            Results: {json.dumps(results, indent=2)[:500]}...
            
            Focus on the key outcomes and benefits. Keep it under 100 characters.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()[:100]
        except Exception as e:
            print(f"Summary generation error: {e}")
    
    # Fallback summaries
    fallback_summaries = {
        "customer_optimization": f"Customer optimization completed with {len(results)} agent insights",
        "fraud_detection": f"Fraud assessment completed with risk analysis from {len(results)} agents",
        "inventory_optimization": f"Inventory optimized using {len(results)} intelligent agents",
        "price_adjustment": f"Dynamic pricing updated with insights from {len(results)} agents"
    }
    
    return fallback_summaries.get(workflow_name, f"Workflow {workflow_name} completed successfully with {len(results)} agent actions")

@app.post("/agent-message")
async def send_agent_message(message: AgentMessage):
    """Send message between agents"""
    
    if message.from_agent not in agents or message.to_agent not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Simulate agent-to-agent communication
    from_agent = agents[message.from_agent]
    to_agent = agents[message.to_agent]
    
    # Process the message
    response = await to_agent.process(
        f"message_from_{message.from_agent}",
        {
            "message_type": message.message_type,
            "payload": message.payload,
            "correlation_id": message.correlation_id
        }
    )
    
    # Broadcast the communication
    await broadcast_update({
        "type": "agent_communication",
        "from_agent": message.from_agent,
        "to_agent": message.to_agent,
        "message_type": message.message_type,
        "correlation_id": message.correlation_id,
        "response": response,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "status": "message_delivered",
        "correlation_id": message.correlation_id,
        "response": response
    }

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket for real-time workflow updates"""
    await websocket.accept()
    active_connections[user_id] = websocket
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to A2A Orchestrator",
            "user_id": user_id,
            "available_workflows": list(workflow_templates.keys()),
            "active_agents": list(agents.keys()),
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                
                if data == "ping":
                    await websocket.send_text("pong")
                elif data.startswith("execute:"):
                    # Quick workflow execution via WebSocket
                    workflow_name = data.split(":", 1)[1]
                    if workflow_name in workflow_templates:
                        await websocket.send_json({
                            "type": "workflow_started",
                            "workflow_name": workflow_name,
                            "message": f"Starting {workflow_name}..."
                        })
                        # Note: Full execution would happen via HTTP endpoint
                else:
                    # Echo unknown commands
                    await websocket.send_json({
                        "type": "echo",
                        "message": f"Received: {data}",
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except asyncio.TimeoutError:
                # Send periodic heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                    "active_workflows": len([w for w in workflow_history if w.get("status") == "running"])
                })
    
    except WebSocketDisconnect:
        if user_id in active_connections:
            del active_connections[user_id]
        print(f"WebSocket disconnected: {user_id}")

async def broadcast_update(message: dict):
    """Broadcast update to all connected WebSocket clients"""
    if not active_connections:
        return
        
    disconnected = []
    for user_id, connection in active_connections.items():
        try:
            await connection.send_json(message)
        except:
            disconnected.append(user_id)
    
    # Clean up disconnected clients
    for user_id in disconnected:
        active_connections.pop(user_id, None)

@app.get("/agents")
async def list_agents():
    """List all agents and their detailed stats"""
    return {
        "agents": [
            {
                "name": agent.name,
                "role": agent.role,
                "capabilities": agent.capabilities,
                "messages_processed": agent.message_count,
                "success_rate": agent.success_rate,
                "avg_response_time": agent.average_response_time,
                "last_activity": agent.last_activity.isoformat(),
                "status": "active"
            }
            for agent in agents.values()
        ],
        "total_agents": len(agents),
        "total_capabilities": sum(len(agent.capabilities) for agent in agents.values())
    }

@app.get("/workflow-history")
async def get_workflow_history(limit: int = 10):
    """Get recent workflow execution history"""
    return {
        "workflows": workflow_history[-limit:],
        "total_executions": len(workflow_history),
        "success_rate": len([w for w in workflow_history if w.get("status") == "completed"]) / max(len(workflow_history), 1)
    }

@app.post("/simulate-event")
async def simulate_event(event_type: str, parameters: Dict = {}):
    """Simulate various system events for demonstration"""
    
    events = {
        "price_drop": {
            "type": "price_drop",
            "product_name": parameters.get("product", "Vintage Camera"),
            "old_price": 149.99,
            "new_price": 119.99,
            "discount": 20
        },
        "low_stock": {
            "type": "low_stock",
            "product_name": parameters.get("product", "Hipster Beanie"),
            "quantity": 3,
            "reorder_threshold": 5
        },
        "fraud_alert": {
            "type": "fraud_alert",
            "transaction_id": f"txn_{datetime.now().timestamp()}",
            "risk_score": 0.87,
            "risk_factors": ["unusual_location", "high_velocity"]
        },
        "customer_segment_update": {
            "type": "customer_segment_update",
            "user_id": parameters.get("user_id", "user_12345"),
            "old_segment": "regular",
            "new_segment": "premium",
            "trigger": "purchase_threshold_reached"
        }
    }
    
    if event_type not in events:
        raise HTTPException(status_code=400, detail=f"Unknown event type: {event_type}")
    
    event = events[event_type]
    event["timestamp"] = datetime.now().isoformat()
    event["simulation"] = True
    
    # Broadcast event to all connected clients
    await broadcast_update(event)
    
    return {
        "status": "event_simulated",
        "event": event,
        "broadcasted_to": len(active_connections)
    }

@app.get("/metrics")
async def get_metrics():
    """Get comprehensive system metrics"""
    return {
        "workflow_metrics": {
            "total_executions": len(workflow_history),
            "successful_executions": len([w for w in workflow_history if w.get("status") == "completed"]),
            "failed_executions": len([w for w in workflow_history if w.get("status") == "failed"]),
            "success_rate": len([w for w in workflow_history if w.get("status") == "completed"]) / max(len(workflow_history), 1)
        },
        "agent_metrics": {
            "total_agents": len(agents),
            "total_messages_processed": sum(agent.message_count for agent in agents.values()),
            "average_success_rate": sum(agent.success_rate for agent in agents.values()) / len(agents),
            "most_active_agent": max(agents.values(), key=lambda a: a.message_count).name if agents else None
        },
        "system_metrics": {
            "active_websocket_connections": len(active_connections),
            "uptime": "operational",
            "ai_model_available": bool(model),
            "memory_usage": "normal"
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8081))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )