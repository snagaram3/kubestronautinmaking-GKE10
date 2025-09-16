# API Documentation

## MCP Server API

Base URL: `http://<mcp-ip>:8080`

### Endpoints

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "ai_model": "gemini-1.5-flash"
}
