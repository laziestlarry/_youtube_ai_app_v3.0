# Shopier API Workflows (PAT-Only)

Base URL: `https://api.shopier.com/v1/`  
Auth: `Authorization: Bearer ${SHOPIER_PERSONAL_ACCESS_TOKEN}`

Reference: `https://dash.readme.com/api/v1/api-registry/j3dkh16m5ushkhl`

## Core Operations

### Add Product (API)
Use `POST /products` with `type: digital`, `media`, `priceData`, and `shippingPayer`.

### Export Product List (API)
Use `GET /products` with paging (`limit`, `page`) to export product IDs and URLs.

### Batch Import from Catalog (Script)
Script: `python3 scripts/shopier_catalog_import.py --env-file .env.shopier`
Price overrides: `docs/commerce/shopier_price_overrides.json`
TRY rounding: for prices >= 1000, the importer snaps the last three digits to a 500-900 band and ends with `99` (disable with `--no-psych-round`).
Stock: digital products default to `stockQuantity=9999` unless you pass `--default-stock` or define `stock_quantity` per SKU.

### Export to CSV (Script)
Script: `python3 scripts/shopier_catalog_export.py --env-file .env.shopier`

## Notes
- The Shopier REST API uses PAT (Bearer token) for all management operations.
- Product checkout URLs are returned in the `url` field of product responses.
- Use the `docs/commerce/shopier_product_map.json` file to map internal SKUs to Shopier product URLs.
- Some shops only support TRY; use `--currency TRY` (and optionally `--fx-rate`) during import.
