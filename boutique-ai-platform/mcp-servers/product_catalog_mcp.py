from fastapi import FastAPI, HTTPException
from typing import Dict, List, Optional
import grpc
import asyncio
import json

# Import generated gRPC stubs for ProductCatalogService
# Note: These would be generated from the existing .proto files
# import product_catalog_pb2
# import product_catalog_pb2_grpc

app = FastAPI(title="Product Catalog MCP Server")

class ProductCatalogMCP:
    def __init__(self):
        self.service_endpoint = "productcatalogservice:3550"
        
    async def get_products(self, filters: Dict = None) -> List[Dict]:
        """Read products from existing ProductCatalogService"""
        try:
            # Connect to existing microservice via gRPC
            async with grpc.aio.insecure_channel(self.service_endpoint) as channel:
                stub = product_catalog_pb2_grpc.ProductCatalogServiceStub(channel)
                
                # Call existing ListProducts method
                request = product_catalog_pb2.Empty()
                response = await stub.ListProducts(request)
                
                # Convert to JSON-friendly format
                products = []
                for product in response.products:
                    products.append({
                        "id": product.id,
                        "name": product.name,
                        "description": product.description,
                        "picture": product.picture,
                        "price": {
                            "currency_code": product.price_usd.currency_code,
                            "units": product.price_usd.units,
                            "nanos": product.price_usd.nanos
                        },
                        "categories": list(product.categories)
                    })
                
                # Apply AI-based filtering if provided
                if filters:
                    products = self.apply_ai_filters(products, filters)
                
                return products
                
        except Exception as e:
            raise HTTPException(status_code=500, f"Error fetching products: {str(e)}")
    
    def apply_ai_filters(self, products: List[Dict], filters: Dict) -> List[Dict]:
        """Apply intelligent filtering based on AI-extracted preferences"""
        # Implement smart filtering logic
        filtered = products
        
        if "category" in filters:
            category = filters["category"].lower()
            filtered = [p for p in filtered if category in [c.lower() for c in p["categories"]]]
        
        if "price_range" in filters and filters["price_range"] == "under_100":
            filtered = [p for p in filtered if p["price"]["units"] < 100]
        
        return filtered

# Initialize MCP instance
mcp = ProductCatalogMCP()

@app.post("/search")
async def search_products(filters: Dict = None):
    """MCP endpoint for AI agents to search products"""
    return await mcp.get_products(filters)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Product Catalog MCP"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
