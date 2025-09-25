"""A2A Network for agent-to-agent and MCP communication"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
import httpx

logger = logging.getLogger(__name__)

class A2ANetwork:
    """Agent-to-Agent network with MCP server communication"""
    
    def __init__(self):
        self.agents = {}
        self.mcp_servers = {}
        self.http_client = httpx.AsyncClient()
        
    async def register_agent(self, agent_id: str, agent_instance):
        """Register an agent in the network"""
        self.agents[agent_id] = agent_instance
        logger.info(f"Registered agent: {agent_id}")
    
    async def register_mcp_server(self, server_name: str, base_url: str):
        """Register an MCP server endpoint"""
        self.mcp_servers[server_name] = base_url
        logger.info(f"Registered MCP server: {server_name} at {base_url}")
    
    async def call_mcp_tool(self, server_name: str, tool_name: str, arguments: Dict = None) -> Optional[Dict]:
        """Call a tool on an MCP server via HTTP"""
        if server_name not in self.mcp_servers:
            logger.error(f"MCP server {server_name} not registered")
            return None
        
        base_url = self.mcp_servers[server_name]
        url = f"{base_url}/{tool_name}"
        
        try:
            # Make HTTP request to MCP server
            if arguments:
                response = await self.http_client.post(url, json=arguments)
            else:
                response = await self.http_client.post(url)
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Successfully called {tool_name} on {server_name}")
            return result
            
        except httpx.RequestError as e:
            logger.error(f"Network error calling {tool_name} on {server_name}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {tool_name} on {server_name}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling {tool_name} on {server_name}: {e}")
            return None
    
    async def agent_communication(self, from_agent: str, to_agent: str, message: Dict) -> Dict:
        """Direct agent-to-agent communication"""
        if to_agent not in self.agents:
            return {"error": f"Agent {to_agent} not found"}
        
        target_agent = self.agents[to_agent]
        if hasattr(target_agent, 'handle_a2a_message'):
            try:
                return await target_agent.handle_a2a_message(from_agent, message)
            except Exception as e:
                return {"error": f"Error in A2A communication: {e}"}
        else:
            return {"error": f"Agent {to_agent} does not support A2A communication"}
    
    async def broadcast_message(self, from_agent: str, message: Dict) -> Dict:
        """Broadcast message to all registered agents"""
        results = {}
        for agent_id, agent in self.agents.items():
            if agent_id != from_agent and hasattr(agent, 'handle_a2a_message'):
                try:
                    result = await agent.handle_a2a_message(from_agent, message)
                    results[agent_id] = result
                except Exception as e:
                    results[agent_id] = {"error": str(e)}
        return results
    
    async def health_check(self) -> Dict:
        """Check health of all registered MCP servers"""
        health_status = {}
        
        for server_name, base_url in self.mcp_servers.items():
            try:
                response = await self.http_client.get(f"{base_url}/health", timeout=5.0)
                if response.status_code == 200:
                    health_status[server_name] = {"status": "healthy", "details": response.json()}
                else:
                    health_status[server_name] = {"status": "unhealthy", "status_code": response.status_code}
            except Exception as e:
                health_status[server_name] = {"status": "unreachable", "error": str(e)}
        
        return health_status
    
    async def shutdown(self):
        """Clean shutdown"""
        await self.http_client.aclose()
        self.agents.clear()
        self.mcp_servers.clear()

# Global A2A network instance
a2a_network = A2ANetwork()

# Auto-register known MCP servers
async def initialize_mcp_connections():
    """Initialize connections to known MCP servers"""
    await a2a_network.register_mcp_server("product-catalog-mcp", "http://product-catalog-mcp:8080")
    # Add other MCP servers as needed
    logger.info("Initialized MCP server connections")
