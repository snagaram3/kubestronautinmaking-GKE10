"""Product Catalog MCP Server - connects to productcatalogservice via gRPC"""

import asyncio
import json
import logging
import sys
import grpc
from typing import Dict, List, Any
import httpx

sys.path.append('/app/protos')
try:
    import demo_pb2
    import demo_pb2_grpc
    GRPC_AVAILABLE = True
except ImportError as e:
    logging.error(f"gRPC imports failed: {e}")
    GRPC_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductCatalogService:
    """Service to handle product catalog operations via gRPC"""
    
    def __init__(self):
        self.grpc_channel = None
        self.product_service = None
        
    async def initialize(self):
        """Initialize gRPC connection"""
        if not GRPC_AVAILABLE:
            logger.warning("gRPC not available, using fallback data")
            return
            
        try:
            self.grpc_channel = grpc.aio.insecure_channel('productcatalogservice:3550')
            self.product_service = demo_pb2_grpc.ProductCatalogServiceStub(self.grpc_channel)
            
            # Test connection
            await asyncio.wait_for(
                self.grpc_channel.channel_ready(),
                timeout=5.0
            )
            logger.info("Connected to productcatalogservice via gRPC")
        except Exception as e:
            logger.error(f"Failed to initialize gRPC connection: {e}")
            self.product_service = None
    
    async def list_products(self) -> Dict[str, Any]:
        """Get all products from the catalog"""
        if not self.product_service:
            return self._get_fallback_products()
            
        try:
            request = demo_pb2.Empty()
            response = await asyncio.wait_for(
                self.product_service.ListProducts(request),
                timeout=10.0
            )
            
            products = []
            for product in response.products:
                products.append({
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "picture": product.picture,
                    "price_usd": {
                        "currency_code": product.price_usd.currency_code,
                        "units": product.price_usd.units,
                        "nanos": product.price_usd.nanos
                    },
                    "categories": list(product.categories)
                })
            
            logger.info(f"Retrieved {len(products)} products via gRPC")
            return {"products": products, "source": "grpc"}
            
        except Exception as e:
            logger.error(f"Error fetching products via gRPC: {e}")
            return self._get_fallback_products()
    
    async def get_product(self, product_id: str) -> Dict[str, Any]:
        """Get specific product by ID"""
        if not self.product_service:
            return self._get_fallback_product(product_id)
            
        try:
            request = demo_pb2.GetProductRequest(id=product_id)
            response = await asyncio.wait_for(
                self.product_service.GetProduct(request),
                timeout=5.0
            )
            
            product = {
                "id": response.id,
                "name": response.name,
                "description": response.description,
                "picture": response.picture,
                "price_usd": {
                    "currency_code": response.price_usd.currency_code,
                    "units": response.price_usd.units,
                    "nanos": response.price_usd.nanos
                },
                "categories": list(response.categories)
            }
            
            return {"product": product, "source": "grpc"}
            
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            return self._get_fallback_product(product_id)
    
    def _get_fallback_products(self) -> Dict[str, Any]:
        """Fallback product data when gRPC is unavailable"""
        products = [
            {
                "id": "OLJCESPC7Z",
                "name": "Sunglasses", 
                "description": "Add a modern touch to your outfits with these sleek aviator sunglasses.",
                "picture": "/static/img/products/sunglasses.jpg",
                "price_usd": {"currency_code": "USD", "units": 19, "nanos": 990000000},
                "categories": ["accessories"]
            },
            {
                "id": "66VCHSJNUP",
                "name": "Tank Top",
                "description": "Perfectly cropped cotton tank, with a scooped neckline.", 
                "picture": "/static/img/products/tank-top.jpg",
                "price_usd": {"currency_code": "USD", "units": 18, "nanos": 990000000},
                "categories": ["clothing"]
            },
            {
                "id": "1YMWWN1N4O",
                "name": "Watch",
                "description": "This gold-tone stainless steel watch will work with most of your outfits.",
                "picture": "/static/img/products/watch.jpg", 
                "price_usd": {"currency_code": "USD", "units": 109, "nanos": 990000000},
                "categories": ["accessories"]
            }
        ]
        return {"products": products, "source": "fallback"}
    
    def _get_fallback_product(self, product_id: str) -> Dict[str, Any]:
        """Get fallback product by ID"""
        fallback_data = self._get_fallback_products()
        for product in fallback_data["products"]:
            if product["id"] == product_id:
                return {"product": product, "source": "fallback"}
        return {"product": None, "source": "fallback"}

# HTTP API Server (similar to reference repo structure)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Product Catalog MCP Server")
catalog_service = ProductCatalogService()

class ProductListRequest(BaseModel):
    pass

class ProductGetRequest(BaseModel):
    product_id: str

@app.on_event("startup")
async def startup_event():
    await catalog_service.initialize()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "product-catalog-mcp", 
        "grpc_available": GRPC_AVAILABLE,
        "grpc_connected": catalog_service.product_service is not None
    }

@app.post("/list_products")
async def list_products():
    """MCP tool: List all products"""
    try:
        result = await catalog_service.list_products()
        return result
    except Exception as e:
        logger.error(f"Error in list_products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_product")
async def get_product(request: ProductGetRequest):
    """MCP tool: Get specific product"""
    try:
        result = await catalog_service.get_product(request.product_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
