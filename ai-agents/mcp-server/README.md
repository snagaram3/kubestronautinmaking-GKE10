# MCP Server - AI Shopping Assistant

The MCP (Model Control Protocol) Server provides AI-powered shopping insights, cart optimization, and personalized recommendations for the Online Boutique application.

## Features

- **Cart Optimization**: Analyzes cart contents and suggests optimizations
- **Personalized Recommendations**: AI-powered product suggestions
- **Shopping Insights**: User behavior analysis and savings tracking
- **Smart Deals**: AI-negotiated bundles and discounts
- **Chat Assistant**: Interactive AI shopping assistant

## API Endpoints

- `GET /health` - Health check
- `GET /insights/{user_id}` - Get shopping insights
- `POST /analyze-cart/{user_id}` - Analyze and optimize cart
- `GET /recommendations/{user_id}` - Get product recommendations
- `GET /smart-deals/{user_id}` - Get AI-negotiated deals
- `POST /chat` - Chat with AI assistant
- `GET /metrics` - System metrics

## Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_api_key_here"

# Run the server
python mcp_server.py

# Build image
docker build -t mcp-server .

# Run container
docker run -p 8080:8080 -e GEMINI_API_KEY="your_key" mcp-server