# A2A Orchestrator - Multi-Agent Workflow Engine

The A2A (Agent-to-Agent) Orchestrator manages multi-agent workflows for complex AI operations in the Online Boutique application.

## Features

- **Multi-Agent Coordination**: Manages pricing, inventory, customer, and fraud agents
- **Workflow Orchestration**: Executes predefined and custom workflows
- **Real-time Communication**: WebSocket support for live updates
- **Agent Simulation**: Simulates intelligent agent behaviors
- **Workflow History**: Tracks and analyzes workflow executions

## Available Agents

- **Pricing Agent**: Dynamic pricing and discount optimization
- **Inventory Agent**: Stock management and demand forecasting
- **Customer Agent**: Profile analysis and behavior prediction
- **Fraud Agent**: Risk assessment and transaction monitoring
- **Personalization Agent**: Content curation and recommendations

## Workflow Templates

- `customer_optimization`: Complete customer experience enhancement
- `fraud_detection`: Multi-layer fraud analysis
- `inventory_optimization`: Smart inventory management
- `price_adjustment`: Dynamic pricing optimization

## API Endpoints

- `GET /status` - System status and agent metrics
- `GET /workflows` - Available workflow templates
- `POST /workflow/{name}` - Execute a workflow
- `GET /agents` - List all agents and stats
- `POST /simulate-event` - Simulate system events
- `WS /ws/{user_id}` - WebSocket for real-time updates

## Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_api_key_here"

# Run the orchestrator
python a2a_orchestrator.py