# Kubernetes Manifests

This directory contains all Kubernetes deployment manifests for the AI components.

## Files

- `namespace.yaml`: Creates the ai-agents namespace
- `secrets.yaml`: Template for secrets (populated by script)
- `mcp-server.yaml`: MCP Server deployment and service
- `a2a-orchestrator.yaml`: A2A Orchestrator deployment and service
- `api-gateway.yaml`: API Gateway deployment and service

## Deployment
```bash
# Apply all manifests
kubectl apply -f k8s/

# Or apply individually
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mcp-server.yaml
kubectl apply -f k8s/a2a-orchestrator.yaml
kubectl apply -f k8s/api-gateway.yaml

# Check pod status
kubectl get pods -n ai-agents

# View logs
kubectl logs -f deployment/mcp-server -n ai-agents
kubectl logs -f deployment/a2a-orchestrator -n ai-agents
kubectl logs -f deployment/api-gateway -n ai-agents

# Check services
kubectl get services -n ai-agents