import httpx
from typing import Dict, Any, List, Optional
from loguru import logger
import asyncio
from backend.config.enhanced_settings import get_settings

class ShopifyService:
    """
    Unified Shopify Service for AutonomaX.
    Combines Admin API (product management) and Storefront API (public data) capabilities.
    """
    
    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        self.payment_settings = self.settings.payment
        
        # Admin API Config
        self.admin_token = self.payment_settings.shopify_admin_token
        self.shop_domain = self.payment_settings.shopify_shop_domain
        self.api_version = self.payment_settings.shopify_api_version
        self.admin_endpoint = f"https://{self.shop_domain}/admin/api/{self.api_version}/graphql.json" if self.admin_token and self.shop_domain else None
        
        # Storefront API Config
        self.storefront_token = self.payment_settings.shopify_storefront_token
        self.storefront_endpoint = f"https://{self.shop_domain}/api/{self.api_version}/graphql.json" if self.storefront_token and self.shop_domain else None
        
        self.is_configured = self.admin_endpoint is not None or self.storefront_endpoint is not None
        
        if not self.is_configured:
            logger.warning("Shopify Service initialized without full credentials (Dry-run mode)")

    async def _post_admin(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Post a GraphQL query to the Admin API."""
        if not self.admin_endpoint:
            raise RuntimeError("Shopify Admin API not configured")
            
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.admin_token,
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                self.admin_endpoint,
                json={"query": query, "variables": variables or {}},
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                logger.error(f"Shopify Admin API error: {data['errors']}")
                raise RuntimeError(f"Shopify Admin error: {data['errors']}")
                
            return data.get("data", {})

    async def _post_storefront(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Post a GraphQL query to the Storefront API."""
        if not self.storefront_endpoint:
            raise RuntimeError("Shopify Storefront API not configured")
            
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Storefront-Access-Token": self.storefront_token,
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                self.storefront_endpoint,
                json={"query": query, "variables": variables or {}},
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                logger.error(f"Shopify Storefront API error: {data['errors']}")
                raise RuntimeError(f"Shopify Storefront error: {data['errors']}")
                
            return data.get("data", {})

    def _build_media_inputs(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        media_inputs = []
        for url in payload.get("images") or []:
            if not url:
                continue
            media_inputs.append(
                {
                    "originalSource": url,
                    "mediaContentType": "IMAGE",
                    "alt": payload.get("title") or "Product image",
                }
            )
        return media_inputs

    async def create_product(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new product in Shopify.
        Payload keys: title, description, price, sku, status (ACTIVE/DRAFT), images (list of URLs)
        """
        if not self.admin_endpoint:
            logger.info(f"[DRY-RUN] Create Product: {payload.get('title')}")
            return {"id": "mock_id", "title": payload.get("title")}

        create_mutation = """
        mutation productCreate($product: ProductCreateInput!, $media: [CreateMediaInput!]) {
          productCreate(product: $product, media: $media) {
            product {
              id
              title
              status
              onlineStoreUrl
              variants(first: 1) {
                edges {
                  node {
                    id
                    title
                  }
                }
              }
            }
            userErrors {
              field
              message
            }
          }
        }
        """

        product_input = {
            "title": payload.get("title"),
            "descriptionHtml": payload.get("description", ""),
            "status": payload.get("status", "ACTIVE").upper(),
            "productType": payload.get("type") or None,
            "vendor": payload.get("vendor") or None,
            "tags": payload.get("tags") or None,
            "productOptions": [
                {
                    "name": "Title",
                    "values": [{"name": "Default"}],
                }
            ],
        }
        product_input = {k: v for k, v in product_input.items() if v}

        media_inputs = self._build_media_inputs(payload)

        result = await self._post_admin(
            create_mutation,
            {"product": product_input, "media": media_inputs if media_inputs else None},
        )
        create_result = result.get("productCreate", {})

        if create_result.get("userErrors"):
            logger.error(f"Shopify Product Creation Errors: {create_result['userErrors']}")
            return {"errors": create_result["userErrors"]}

        product = create_result.get("product", {})
        variant_edges = product.get("variants", {}).get("edges", [])
        if not variant_edges:
            return product

        variant_id = variant_edges[0]["node"]["id"]
        update_mutation = """
        mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
          productVariantsBulkUpdate(productId: $productId, variants: $variants) {
            product { id }
            userErrors { field message }
          }
        }
        """

        sku = payload.get("sku") or f"auto-{payload.get('title', 'product')[:10]}"
        variant_input = {
            "id": variant_id,
            "price": str(payload.get("price", 0)),
            "inventoryItem": {
                "sku": sku,
                "requiresShipping": False,
            },
        }

        update_result = await self._post_admin(
            update_mutation,
            {"productId": product.get("id"), "variants": [variant_input]},
        )
        update_payload = update_result.get("productVariantsBulkUpdate", {})
        if update_payload.get("userErrors"):
            logger.error(f"Shopify Variant Update Errors: {update_payload['userErrors']}")
            return {"errors": update_payload["userErrors"], "product": product}

        return product

    async def update_product(
        self,
        product: Dict[str, Any],
        payload: Dict[str, Any],
        update_images: bool = False
    ) -> Dict[str, Any]:
        """Update product fields/variants by SKU."""
        if not self.admin_endpoint:
            logger.info(f"[DRY-RUN] Update Product: {payload.get('title')}")
            return {"id": product.get("id"), "title": payload.get("title")}

        product_id = product.get("id")
        if not product_id:
            return {"errors": [{"field": "id", "message": "Missing product id"}]}

        update_mutation = """
        mutation productUpdate($input: ProductInput!) {
          productUpdate(input: $input) {
            product {
              id
              title
              status
              onlineStoreUrl
            }
            userErrors {
              field
              message
            }
          }
        }
        """

        product_input = {
            "id": product_id,
            "title": payload.get("title"),
            "descriptionHtml": payload.get("description", ""),
            "status": payload.get("status", "ACTIVE").upper(),
            "productType": payload.get("type") or None,
            "vendor": payload.get("vendor") or None,
            "tags": payload.get("tags") or None,
        }
        product_input = {k: v for k, v in product_input.items() if v}

        update_result = await self._post_admin(update_mutation, {"input": product_input})
        update_payload = update_result.get("productUpdate", {})
        if update_payload.get("userErrors"):
            logger.error(f"Shopify Product Update Errors: {update_payload['userErrors']}")
            return {"errors": update_payload["userErrors"], "product": product}

        variant_edges = product.get("variants", {}).get("edges", [])
        variant_id = None
        desired_sku = payload.get("sku")
        if desired_sku:
            for edge in variant_edges:
                if edge.get("node", {}).get("sku") == desired_sku:
                    variant_id = edge["node"]["id"]
                    break
        if not variant_id and variant_edges:
            variant_id = variant_edges[0]["node"]["id"]

        if variant_id:
            variant_update = """
            mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
              productVariantsBulkUpdate(productId: $productId, variants: $variants) {
                product { id }
                userErrors { field message }
              }
            }
            """
            variant_input = {
                "id": variant_id,
                "price": str(payload.get("price", 0)),
                "inventoryItem": {
                    "sku": desired_sku or "",
                    "requiresShipping": False,
                },
            }
            variant_result = await self._post_admin(
                variant_update,
                {"productId": product_id, "variants": [variant_input]},
            )
            variant_payload = variant_result.get("productVariantsBulkUpdate", {})
            if variant_payload.get("userErrors"):
                logger.error(f"Shopify Variant Update Errors: {variant_payload['userErrors']}")
                return {"errors": variant_payload["userErrors"], "product": product}

        if update_images:
            media_inputs = self._build_media_inputs(payload)
            if media_inputs:
                media_mutation = """
                mutation productCreateMedia($productId: ID!, $media: [CreateMediaInput!]!) {
                  productCreateMedia(productId: $productId, media: $media) {
                    media {
                      alt
                      status
                    }
                    mediaUserErrors {
                      field
                      message
                    }
                  }
                }
                """
                media_result = await self._post_admin(
                    media_mutation,
                    {"productId": product_id, "media": media_inputs},
                )
                media_payload = media_result.get("productCreateMedia", {})
                if media_payload.get("mediaUserErrors"):
                    logger.error(f"Shopify Media Update Errors: {media_payload['mediaUserErrors']}")
                    return {"errors": media_payload["mediaUserErrors"], "product": product}

        return update_payload.get("product", {}) or product

    async def upsert_product(
        self,
        payload: Dict[str, Any],
        update_images: bool = False
    ) -> Dict[str, Any]:
        """Create product if missing or update existing by SKU."""
        sku = payload.get("sku")
        existing = await self.find_product_by_sku(sku) if sku else None
        if existing:
            return await self.update_product(existing, payload, update_images=update_images)
        return await self.create_product(payload)

    async def get_storefront_info(self) -> Dict[str, Any]:
        """Fetch general shop information from the Storefront API."""
        query = """
        {
          shop {
            name
            description
            moneyFormat
          }
        }
        """
        return await self._post_storefront(query)

    async def list_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List products via Storefront API."""
        query = """
        query($first: Int!) {
          products(first: $first) {
            edges {
              node {
                id
                title
                description
                onlineStoreUrl
                featuredImage {
                  url
                  altText
                }
              }
            }
          }
        }
        """
        data = await self._post_storefront(query, {"first": limit})
        products = data.get("products", {}).get("edges", [])
        return [p["node"] for p in products]

    async def find_product_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Find a product via Admin API search by SKU."""
        if not self.admin_endpoint:
            return None
        if not sku:
            return None

        query = """
        query($query: String!) {
          products(first: 1, query: $query) {
            edges {
              node {
                id
                title
                handle
                variants(first: 5) {
                  edges {
                    node {
                      id
                      sku
                    }
                  }
                }
              }
            }
          }
        }
        """
        data = await self._post_admin(query, {"query": f"sku:{sku}"})
        edges = data.get("products", {}).get("edges", [])
        if not edges:
            return None
        return edges[0]["node"]

# Global instance
shopify_service = ShopifyService()
