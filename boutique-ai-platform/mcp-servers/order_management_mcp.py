from fastapi import FastAPI, HTTPException
from typing import Dict, List, Optional
import grpc
import asyncio

app = FastAPI(title="Order Management MCP Server")

class OrderManagementMCP:
    def __init__(self):
        self.checkout_service = "checkoutservice:5050"
        self.shipping_service = "shippingservice:50051"
        self.payment_service = "paymentservice:50051"
    
    async def get_order_status(self, order_info: Dict) -> Dict:
        """Aggregate order information from multiple existing services"""
        order_id = order_info.get("order_id")
        
        try:
            # Get order details from CheckoutService
            order_details = await self.get_checkout_details(order_id)
            
            # Get shipping status from ShippingService  
            shipping_status = await self.get_shipping_status(order_id)
            
            # Get payment status from PaymentService
            payment_status = await self.get_payment_status(order_id)
            
            # Combine all information
            comprehensive_status = {
                "order_id": order_id,
                "order_details": order_details,
                "shipping": shipping_status,
                "payment": payment_status,
                "estimated_delivery": self.calculate_delivery_estimate(shipping_status)
            }
            
            return comprehensive_status
            
        except Exception as e:
            raise HTTPException(status_code=500, f"Error fetching order status: {str(e)}")
    
    async def get_checkout_details(self, order_id: str) -> Dict:
        """Read from existing CheckoutService"""
        # Implement gRPC call to existing service
        return {"status": "confirmed", "items": [], "total": "0"}
    
    async def get_shipping_status(self, order_id: str) -> Dict:
        """Read from existing ShippingService"""
        # Implement gRPC call to existing service
        return {"status": "in_transit", "tracking_id": "TRACK123"}
    
    async def get_payment_status(self, order_id: str) -> Dict:
        """Read from existing PaymentService"""
        # Implement gRPC call to existing service
        return {"status": "paid", "method": "credit_card"}
    
    def calculate_delivery_estimate(self, shipping_info: Dict) -> str:
        """AI-enhanced delivery estimation"""
        # Add intelligent delivery prediction logic
        return "2-3 business days"

mcp = OrderManagementMCP()

@app.post("/order_status")
async def get_order_status(order_info: Dict):
    """MCP endpoint for order status queries"""
    return await mcp.get_order_status(order_info)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Order Management MCP"}
