# Marketing Assets Output

Generated files from `scripts/prepare_marketing_assets.py` will appear here.

- `index.json`: full catalog manifest
- `channel_shopify.csv`: Shopify upload template
- `channel_etsy.csv`: Etsy upload template
- `channel_fiverr.csv`: Fiverr upload template
- `channel_amazon.csv`: Amazon listing brief
- `channel_gumroad.csv`: Gumroad listing brief
- `channel_shopier.csv`: Shopier checkout sheet

Each SKU can have its own folder with listing images and a short promo clip or guide.

Run:
```bash
python3 scripts/prepare_marketing_assets.py \
  --catalog docs/commerce/product_catalog.json \
  --output marketing_assets \
  --backend-url https://your-backend-domain
```
