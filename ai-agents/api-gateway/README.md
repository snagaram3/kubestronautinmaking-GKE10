# API Gateway - Frontend Integration Layer

The API Gateway serves as a proxy between users and the Online Boutique frontend while injecting the AI Shopping Assistant widget.

## Features

- **Transparent Proxying**: Forwards all requests to the original frontend
- **AI Widget Injection**: Automatically injects AI assistant into HTML responses
- **Error Handling**: Graceful fallbacks when services are unavailable
- **Widget Testing**: Dedicated test page for widget functionality

## How It Works

1. User requests go to the API Gateway
2. Gateway forwards requests to the original Online Boutique frontend
3. For HTML responses, the AI widget is injected before `</body>`
4. Non-HTML responses pass through unchanged
5. If frontend is unavailable, shows fallback page with widget

## API Endpoints

- `GET /health` - Gateway health check
- `GET /widget-test` - Dedicated widget test page
- `/{path}` - Proxy all other requests to frontend

## Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the gateway
python api_gateway.py