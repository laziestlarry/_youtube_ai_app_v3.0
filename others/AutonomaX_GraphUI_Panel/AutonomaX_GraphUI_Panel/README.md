
# AutonomaX Graph UI — Execution Panel

Adds a right-side panel so you can: 
- Paste or load sample JSON inputs
- Create products (`POST /products`)
- Log KPIs (`POST /observe`)
- Push to Shopify/Etsy using your existing endpoints

## Run
```bash
cd AutonomaX_GraphUI_Panel
python3 -m http.server 9901
# open http://localhost:9901
```
## Configure
Edit `data/endpoints.json`:
- `base_url` → FastAPI base (e.g., http://127.0.0.1:8000)
- `auth.bearer_token` → token from `POST /auth/token` (tenant-scoped)
- Shopify/Etsy credentials as applicable

The panel buttons call:
- `/products`
- `/observe`
- `/channels/shopify/push`
- `/channels/etsy/push`
