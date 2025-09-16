# System Architecture

## Overview

The Online Boutique AI Enhancement adds three AI components to the existing Google Cloud microservices demo:

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │───▶│   API Gateway   │───▶│Online Boutique │
└─────────────────┘    └─────────────────┘    │   Frontend      │
│              └─────────────────┘
│
┌───────▼───────┐
│  AI Widget    │
│  (Injected)   │
└───────┬───────┘
│
┌───────────▼───────────┐
│                       │
┌───────▼──────┐        ┌───────▼──────┐
│  MCP Server  │◀──────▶│A2A Orchestrator│
│              │        │              │
└──────────────┘        └──────────────┘

## Components

### API Gateway
- **Purpose**: Transparent proxy with AI widget injection
- **Technology**: FastAPI, httpx
- **Responsibilities**:
  - Forward requests to original frontend
  - Inject AI widget into HTML responses
  - Handle fallbacks when services are unavailable

### MCP Server
- **Purpose**: AI-powered shopping assistance
- **Technology**: FastAPI, Google Gemini AI
- **Responsibilities**:
  - Cart optimization analysis
  - Personalized recommendations
  - Shopping insights generation
  - AI chat assistance

### A2A Orchestrator
- **Purpose**: Multi-agent workflow coordination
- **Technology**: FastAPI, WebSockets, Gemini AI
- **Responsibilities**:
  - Agent-to-agent communication
  - Workflow execution and tracking
  - Real-time event broadcasting
  - System metrics collection

## Data Flow

1. **User Request**: Browser → API Gateway
2. **Proxy**: API Gateway → Online Boutique Frontend
3. **Enhancement**: API Gateway injects AI widget
4. **AI Interaction**: Widget → MCP Server (insights, optimization)
5. **Workflow Trigger**: MCP Server → A2A Orchestrator (complex operations)
6. **Real-time Updates**: A2A Orchestrator → Widget (WebSocket)

## Security Considerations

- API keys stored in Kubernetes secrets
- CORS enabled for development (restrict in production)
- Health checks and resource limits configured
- No sensitive data stored in containers

## Scalability

- Horizontal pod autoscaling supported
- Stateless design enables easy scaling
- LoadBalancer services for external access
- GKE Autopilot handles node scaling