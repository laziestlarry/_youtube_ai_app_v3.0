import asyncio
import json
import os
import sys
from html import escape

# Add project root to path
sys.path.append(os.getcwd())

INPUT_FILE = "docs/commerce/product_catalog.json"
OUTPUT_FILE = "static/store.html"
SHOPIER_MAP_FILE = os.getenv("SHOPIER_PRODUCT_MAP", "docs/commerce/shopier_product_map.json")
SHOPIER_PRICE_FILE = os.getenv(
    "SHOPIER_PRICE_OVERRIDES",
    "docs/commerce/shopier_price_overrides.json",
)


def _format_price(value: float) -> str:
    if value >= 1000:
        return f"${value:,.0f}"
    return f"${value:,.2f}".rstrip("0").rstrip(".")


def _delay_from_id(value) -> float:
    try:
        return (int(value) % 8) * 0.06
    except Exception:
        return 0.0


def _currency_symbol(code: str) -> str:
    if code.upper() == "EUR":
        return "€"
    if code.upper() == "TRY":
        return "TL"
    return "$"


def _format_price_for_currency(value: float, currency: str) -> str:
    currency_upper = currency.upper()
    if currency_upper == "TRY":
        amount = int(round(value))
        formatted = f"{amount:,}".replace(",", ".")
        return f"{formatted} TL"
    symbol = _currency_symbol(currency_upper)
    if value >= 1000:
        formatted = f"{value:,.0f}"
    else:
        formatted = f"{value:,.2f}".rstrip("0").rstrip(".")
    return f"{symbol}{formatted}"


def _normalize_image_url(url: str) -> str:
    if not url:
        return "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80"
    if url.startswith("http"):
        return url
    return f"/{url.lstrip('/')}"


def _format_price_range(price: dict) -> tuple[str, float, str, bool]:
    min_price = price.get("min") or price.get("max") or 0
    max_price = price.get("max") or min_price
    currency = price.get("currency", "USD")
    is_range = bool(min_price and max_price and min_price != max_price)
    if min_price and max_price and min_price != max_price:
        label = f"{_format_price_for_currency(min_price, currency)}-{_format_price_for_currency(max_price, currency)}"
    else:
        label = _format_price_for_currency(min_price, currency) if min_price else _format_price_for_currency(0, currency)
    return label, float(min_price), currency, is_range


def _cta_label(product: dict, is_range: bool) -> str:
    if product.get("cta_label"):
        return str(product["cta_label"])
    product_type = (product.get("type") or "digital").lower()
    if product_type in {"consulting", "training"} and is_range:
        return "Başvur"
    if product_type == "subscription":
        return "Abone Ol"
    if product_type == "service":
        return "Projeyi Başlat"
    return "Satın Al"


def _product_type_label(product_type: str) -> str:
    mapping = {
        "digital": "Dijital",
        "consulting": "Danışmanlık",
        "training": "Eğitim",
        "subscription": "Abonelik",
        "service": "Hizmet",
    }
    return mapping.get(product_type.lower(), product_type.title())


def _delivery_label(product: dict) -> str:
    if product.get("delivery"):
        return str(product["delivery"])
    product_type = (product.get("type") or "digital").lower()
    if product_type == "consulting":
        return "24-48 saat içinde keşif görüşmesi"
    if product_type == "training":
        return "24 saat içinde eğitim daveti"
    if product_type == "subscription":
        return "Erişim hemen aktif"
    if product_type == "service":
        return "48 saat içinde kickoff"
    return "Anında dijital teslimat"


def _checkout_button(product: dict, amount: float, currency: str, title: str, sku: str, cta_label: str) -> str:
    external_url = product.get("shopier_url") or product.get("checkout_url")
    if external_url:
        return f'<a href="{external_url}" class="btn-primary" target="_blank" rel="noopener">{cta_label}</a>'
    return (
        f'<a href="#" class="btn-primary shopier-pay" '
        f'data-sku="{sku}" data-price="{amount}" data-currency="{currency}" '
        f'data-title="{title}">{cta_label}</a>'
    )


def generate_product_card(product: dict, index: int) -> str:
    """Generates HTML for a single product card."""
    title = escape(product.get("title", "Untitled"))
    description = escape(product.get("short_description", "") or product.get("long_description", ""))
    image_url = _normalize_image_url(product.get("image_url"))
    price_label, amount, currency, is_range = _format_price_range(product.get("price", {}))
    product_type = escape(_product_type_label(product.get("type", "digital")))
    sku = escape(product.get("sku", f"SKU-{index}"))
    cta_label = _cta_label(product, is_range)
    delivery = escape(_delivery_label(product))
    delay = _delay_from_id(index)

    if is_range:
        price_label = f"Başlangıç {price_label}"

    checkout_button = _checkout_button(product, amount, currency, title, sku, cta_label)

    return f"""
    <article class="product-card reveal" style="animation-delay: {delay:.2f}s">
        <div class="product-media">
            <img src="{image_url}" alt="{title}" loading="lazy">
        </div>
        <div class="product-body">
            <div class="product-badges">
                <span class="badge">{product_type}</span>
                <span class="badge badge-soft">Shopier Hazır</span>
            </div>
            <h3 class="product-title">{title}</h3>
            <p class="product-copy">{description[:180]}...</p>
            <p class="feature-meta">{delivery}</p>
            <div class="product-footer">
                <span class="price">{price_label}</span>
                {checkout_button}
            </div>
        </div>
    </article>
    """


def generate_feature_card(product: dict, index: int) -> str:
    title = escape(product.get("title", "Untitled"))
    description = escape(product.get("short_description", "") or product.get("long_description", ""))
    image_url = _normalize_image_url(product.get("image_url"))
    price_label, amount, currency, is_range = _format_price_range(product.get("price", {}))
    product_type = escape(_product_type_label(product.get("type", "digital")))
    sku = escape(product.get("sku", f"SKU-{index}"))
    cta_label = _cta_label(product, is_range)
    delivery = escape(_delivery_label(product))

    if is_range:
        price_label = f"Başlangıç {price_label}"

    checkout_button = _checkout_button(product, amount, currency, title, sku, cta_label)

    return f"""
    <div class="feature-card">
      <div class="feature-media">
        <img src="{image_url}" alt="{title}" loading="lazy">
      </div>
      <div class="feature-body">
        <div class="product-badges">
          <span class="badge">{product_type}</span>
          <span class="badge badge-soft">Öne Çıkan</span>
        </div>
        <h3 class="text-xl font-semibold mt-3">{title}</h3>
        <p class="text-slate-400 mt-3">{description[:160]}...</p>
        <p class="feature-meta">{delivery}</p>
        <div class="product-footer">
          <span class="price">{price_label}</span>
          {checkout_button}
        </div>
      </div>
    </div>
    """


async def deploy():
    print(f"Building storefront from {INPUT_FILE}...")

    if not os.path.exists("static"):
        os.makedirs("static")

    products_html = ""

    with open(INPUT_FILE, "r", encoding="utf-8") as handle:
        catalog = json.load(handle)
        products = [
            product for product in catalog.get("products", [])
            if "shopier" in (product.get("channels") or [])
        ]

    shopier_map = {}
    if os.path.exists(SHOPIER_MAP_FILE):
        try:
            with open(SHOPIER_MAP_FILE, "r", encoding="utf-8") as handle:
                shopier_map = json.load(handle)
        except Exception:
            shopier_map = {}

    shopier_prices = {}
    if os.path.exists(SHOPIER_PRICE_FILE):
        try:
            with open(SHOPIER_PRICE_FILE, "r", encoding="utf-8") as handle:
                shopier_prices = json.load(handle)
        except Exception:
            shopier_prices = {}

    for product in products:
        sku = product.get("sku")
        if not sku:
            continue
        mapped = shopier_map.get(sku, {})
        if isinstance(mapped, dict) and mapped.get("url"):
            product["shopier_url"] = mapped["url"]
        override = shopier_prices.get(sku, {})
        if isinstance(override, dict) and override.get("price") is not None:
            currency = override.get("currency") or product.get("price", {}).get("currency") or "TRY"
            product["price"] = {"min": override["price"], "max": override["price"], "currency": currency}

    type_order = ["digital", "training", "consulting", "subscription", "service"]
    grouped = {}
    for product in products:
        grouped.setdefault(product.get("type", "digital"), []).append(product)

    catalog_by_sku = {product.get("sku"): product for product in products}
    featured_skus = [
        "HYBRID-STACK-01",
        "NOTION-PASSIVE-01",
        "IW-CONSULT-01",
        "IW-TRAIN-01",
        "CMD-API-01",
        "AX-SAAS-01",
    ]
    featured_html = ""
    featured_index = 0
    for sku in featured_skus:
        product = catalog_by_sku.get(sku)
        if not product:
            continue
        featured_html += generate_feature_card(product, featured_index)
        featured_index += 1

    count = 0
    for product_type in type_order + sorted(k for k in grouped.keys() if k not in type_order):
        if product_type not in grouped:
            continue
        section_cards = ""
        for product in grouped[product_type]:
            section_cards += generate_product_card(product, count)
            count += 1
        section_title = escape(product_type.replace("_", " ").title())
        products_html += f"""
        <div class="mb-10">
          <p class="uppercase tracking-[0.3em] text-xs text-slate-500">Shopier kataloğu</p>
          <h3 class="section-title mt-3">{section_title}</h3>
          <p class="section-subtitle mt-3">Shopier ile anında ödeme: {section_title} teklifleri.</p>
        </div>
        <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {section_cards}
        </div>
        """

    template = """
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AutonomaX Ticaret Stüdyosu</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&family=Sora:wght@400;600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root {
      --ink: #0b0f14;
      --surface: rgba(15, 23, 42, 0.78);
      --line: rgba(148, 163, 184, 0.18);
      --gold: #f59e0b;
      --coral: #fb7185;
      --teal: #2dd4bf;
      --sky: #38bdf8;
      --text: #e2e8f0;
    }
    * { box-sizing: border-box; }
    body {
      font-family: 'Manrope', sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at 15% 20%, rgba(56, 189, 248, 0.16), transparent 45%),
        radial-gradient(circle at 85% 0%, rgba(251, 113, 133, 0.2), transparent 35%),
        radial-gradient(circle at 10% 80%, rgba(45, 212, 191, 0.2), transparent 40%),
        #0b0f14;
    }
    h1, h2, h3, h4 {
      font-family: 'Sora', sans-serif;
      letter-spacing: -0.02em;
    }
    .glass {
      background: var(--surface);
      border: 1px solid var(--line);
      box-shadow: 0 20px 50px rgba(15, 23, 42, 0.35);
      backdrop-filter: blur(14px);
    }
    .nav-link {
      color: #cbd5f5;
      transition: color 0.2s ease;
    }
    .nav-link:hover { color: #ffffff; }
    .btn-primary {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, var(--gold), var(--coral));
      color: #0b0f14;
      padding: 0.6rem 1.4rem;
      border-radius: 999px;
      font-weight: 700;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      box-shadow: 0 12px 30px rgba(245, 158, 11, 0.2);
    }
    .btn-primary:hover { transform: translateY(-2px); }
    .btn-secondary {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--line);
      color: #e2e8f0;
      padding: 0.6rem 1.4rem;
      border-radius: 999px;
      font-weight: 600;
      transition: border-color 0.2s ease, color 0.2s ease;
    }
    .btn-secondary:hover { border-color: #fff; color: #fff; }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      padding: 0.2rem 0.65rem;
      border-radius: 999px;
      font-size: 0.7rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      background: rgba(56, 189, 248, 0.15);
      color: #bae6fd;
      border: 1px solid rgba(56, 189, 248, 0.2);
    }
    .badge-soft {
      background: rgba(45, 212, 191, 0.12);
      color: #99f6e4;
      border-color: rgba(45, 212, 191, 0.25);
    }
    .product-card {
      background: rgba(15, 23, 42, 0.86);
      border: 1px solid var(--line);
      border-radius: 20px;
      overflow: hidden;
      transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }
    .product-card:hover {
      transform: translateY(-6px);
      border-color: rgba(248, 250, 252, 0.25);
      box-shadow: 0 18px 40px rgba(15, 23, 42, 0.5);
    }
    .feature-card {
      display: grid;
      grid-template-columns: 1fr;
      background: rgba(15, 23, 42, 0.9);
      border: 1px solid var(--line);
      border-radius: 22px;
      overflow: hidden;
      box-shadow: var(--shadow);
    }
    .feature-media {
      height: 220px;
      background: #0b0f14;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 12px;
    }
    .feature-media img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      object-position: center;
      background: #0b0f14;
    }
    .feature-body {
      padding: 1.6rem;
    }
    .feature-meta {
      color: #94a3b8;
      font-size: 0.85rem;
      margin-top: 0.75rem;
    }
    .product-media {
      height: 240px;
      background: #0b0f14;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 12px;
    }
    .product-media img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      object-position: center;
      background: #0b0f14;
    }
    .product-body { padding: 1.5rem; }
    .product-title { font-size: 1.2rem; margin-bottom: 0.5rem; }
    .product-copy {
      color: #94a3b8;
      font-size: 0.95rem;
      line-height: 1.6;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
      min-height: 4.4rem;
    }
    .product-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 1.4rem;
    }
    .price {
      font-family: 'Sora', sans-serif;
      font-size: 1.3rem;
      font-weight: 700;
      color: #f8fafc;
    }
    .reveal { animation: rise 0.7s ease both; }
    @keyframes rise {
      from { opacity: 0; transform: translateY(24px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .hero-card {
      border-radius: 24px;
      padding: 2rem;
      background: linear-gradient(145deg, rgba(15, 23, 42, 0.8), rgba(15, 23, 42, 0.5));
      border: 1px solid var(--line);
    }
    .preview-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      margin-top: 20px;
    }
    .preview-card {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 18px;
      overflow: hidden;
      box-shadow: var(--shadow);
    }
    .preview-card img {
      width: 100%;
      height: 180px;
      object-fit: contain;
      object-position: center;
      background: #0b0f14;
      display: block;
    }
    .preview-card span {
      display: block;
      padding: 12px 14px;
      font-size: 0.85rem;
      color: #cbd5f5;
    }
    .journey-step {
      border-radius: 18px;
      border: 1px solid var(--line);
      padding: 1.5rem;
      background: rgba(15, 23, 42, 0.65);
    }
    .section-title {
      font-size: 2.2rem;
    }
    .section-subtitle {
      color: #94a3b8;
      max-width: 640px;
    }
    .chat-widget {
      position: fixed;
      right: 24px;
      bottom: 24px;
      z-index: 60;
      display: flex;
      flex-direction: column;
      gap: 12px;
      align-items: flex-end;
    }
    .chat-toggle {
      border: none;
      cursor: pointer;
      padding: 0.7rem 1.4rem;
      border-radius: 999px;
      font-weight: 700;
      color: #0b0f14;
      background: linear-gradient(135deg, var(--gold), var(--coral));
      box-shadow: 0 12px 30px rgba(245, 158, 11, 0.2);
    }
    .chat-panel {
      width: 320px;
      background: rgba(15, 23, 42, 0.95);
      border: 1px solid var(--line);
      border-radius: 18px;
      overflow: hidden;
      display: none;
      flex-direction: column;
      box-shadow: 0 22px 44px rgba(15, 23, 42, 0.55);
    }
    .chat-panel.open {
      display: flex;
    }
    .chat-header {
      padding: 0.85rem 1rem;
      font-weight: 700;
      border-bottom: 1px solid var(--line);
      background: rgba(15, 23, 42, 0.85);
    }
    .chat-body {
      padding: 0.9rem;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
      max-height: 280px;
      overflow-y: auto;
    }
    .chat-quick {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      padding: 0 0.9rem 0.9rem;
    }
    .chat-quick button {
      border: 1px solid rgba(148, 163, 184, 0.25);
      background: rgba(148, 163, 184, 0.08);
      color: #e2e8f0;
      font-size: 0.75rem;
      padding: 0.35rem 0.6rem;
      border-radius: 999px;
      cursor: pointer;
    }
    .chat-bubble {
      padding: 0.6rem 0.8rem;
      border-radius: 14px;
      font-size: 0.9rem;
      line-height: 1.4;
      background: rgba(59, 130, 246, 0.12);
      border: 1px solid rgba(59, 130, 246, 0.25);
      color: #dbeafe;
    }
    .chat-bubble.user {
      align-self: flex-end;
      background: rgba(16, 185, 129, 0.15);
      border-color: rgba(16, 185, 129, 0.3);
      color: #ecfdf5;
    }
    .chat-form {
      display: flex;
      gap: 8px;
      padding: 0.8rem;
      border-top: 1px solid var(--line);
      background: rgba(15, 23, 42, 0.85);
    }
    .chat-input {
      flex: 1;
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid rgba(148, 163, 184, 0.2);
      border-radius: 10px;
      padding: 0.5rem 0.7rem;
      color: #e2e8f0;
      font-size: 0.9rem;
    }
    .chat-input::placeholder {
      color: #94a3b8;
    }
    .chat-send {
      background: rgba(248, 250, 252, 0.08);
      border: 1px solid rgba(148, 163, 184, 0.3);
      color: #e2e8f0;
      padding: 0.5rem 0.8rem;
      border-radius: 10px;
      font-weight: 600;
      cursor: pointer;
    }
    @media (max-width: 640px) {
      .chat-widget {
        right: 16px;
        bottom: 16px;
      }
      .chat-panel {
        width: min(92vw, 360px);
      }
    }
  </style>
</head>
<body class="min-h-screen relative">
  <div class="absolute -top-20 -left-20 h-72 w-72 rounded-full bg-sky-500/10 blur-3xl"></div>
  <div class="absolute top-40 -right-20 h-72 w-72 rounded-full bg-rose-500/10 blur-3xl"></div>

  <nav class="sticky top-0 z-50 bg-[#0b0f14]/80 backdrop-blur border-b border-white/5">
    <div class="container mx-auto px-6 py-4 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-full bg-gradient-to-br from-amber-400 to-rose-400"></div>
        <div>
          <p class="text-sm uppercase tracking-[0.3em] text-slate-500">AutonomaX</p>
          <h1 class="text-xl font-bold">Ticaret Stüdyosu</h1>
        </div>
      </div>
      <div class="flex items-center gap-6 text-sm">
        <a class="nav-link" href="#focus">Odak</a>
        <a class="nav-link" href="#journey">Yolculuk</a>
        <a class="nav-link" href="#featured">Öne Çıkanlar</a>
        <a class="nav-link" href="#portfolio">Katalog</a>
        <a class="btn-secondary" href="#contact">Görüşme Planla</a>
      </div>
    </div>
  </nav>

  <header class="container mx-auto px-6 py-16">
    <div class="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] items-center">
      <div class="reveal">
        <p class="uppercase tracking-[0.3em] text-xs text-slate-500">Gelir orkestrasyon platformu</p>
        <h2 class="text-4xl md:text-5xl font-bold leading-tight mt-4">Premium ürünleri, hizmetleri ve otomasyonu tek bir birleşik marka sisteminde başlatın.</h2>
        <p class="mt-6 text-lg text-slate-400">Commerce Studio, danışmanlık, eğitim ve dijital ürünleri Shopier ödeme, BizOp içgörüleri ve büyüme otomasyonu ile birleştirir.</p>
        <p class="mt-4 text-base text-slate-400">Türkiye için yerelleştirildi: tüm içerik, teslimat ve destek akışları Türkçe ve dijital ürünler anında teslim edilir.</p>
        <div class="mt-8 flex flex-wrap gap-4">
          <a class="btn-primary" href="#portfolio">Shopier Kataloğunu Keşfet</a>
          <a class="btn-secondary" href="#featured">Öne Çıkan Teklifler</a>
        </div>
        <div class="mt-8 grid grid-cols-2 gap-4 text-sm text-slate-400">
          <div class="glass rounded-xl px-4 py-3">Anında ödeme için Shopier hazır ödeme akışı</div>
          <div class="glass rounded-xl px-4 py-3">Çok kanallı listeleme: Shopify, Etsy, Gumroad, YouTube</div>
        </div>
      </div>
      <div class="space-y-4">
        <div class="hero-card reveal">
          <h3 class="text-2xl font-semibold">Lansman Radarı</h3>
          <p class="text-slate-400 mt-2">Yüksek marjlı dijital ürünler, seçkin danışmanlık ve otomasyon odaklı hizmetlere odaklı.</p>
          <div class="mt-6 space-y-4">
            <div class="flex items-center justify-between border-b border-white/10 pb-3">
              <span>IntelliWealth Danışmanlık</span>
              <span class="text-amber-300">29.899 TL+</span>
            </div>
            <div class="flex items-center justify-between border-b border-white/10 pb-3">
              <span>Commander API Ops</span>
              <span class="text-sky-300">7.899 TL kurulum</span>
            </div>
            <div class="flex items-center justify-between">
              <span>YouTube Otomasyon Stüdyosu</span>
              <span class="text-emerald-300">5.899 TL+</span>
            </div>
          </div>
        </div>
        <div class="preview-grid reveal">
          <div class="preview-card">
            <img src="/static/assets/intelliwealth_preview.png" alt="IntelliWealth executive preview" loading="lazy">
            <span>IntelliWealth Yönetici Blueprint</span>
          </div>
          <div class="preview-card">
            <img src="/static/assets/mastery_preview.png" alt="Automation mastery preview" loading="lazy">
            <span>Automation Mastery Stüdyosu</span>
          </div>
        </div>
      </div>
    </div>
  </header>

  <section id="focus" class="container mx-auto px-6 py-12">
    <div class="mb-10">
      <p class="uppercase tracking-[0.3em] text-xs text-slate-500">Odak alanları</p>
      <h2 class="section-title mt-3">Hibrit operatörler ve yönetici ekipler için.</h2>
      <p class="section-subtitle mt-3">Üç gelir sütunu: dijital gelir yığınları, otomasyon odaklı hizmetler ve yönetici büyüme sistemleri.</p>
    </div>
    <div class="grid gap-6 md:grid-cols-3">
      <div class="glass rounded-2xl p-8">
        <h3 class="text-xl font-semibold">Hibrit Gelir Yığını</h3>
        <p class="text-slate-400 mt-3">Anında teslim dijital ürünler, şablonlar ve playbook'lar ile tekrarlanabilir gelir.</p>
      </div>
      <div class="glass rounded-2xl p-8">
        <h3 class="text-xl font-semibold">Otomasyon Hizmetleri</h3>
        <p class="text-slate-400 mt-3">YouTube otomasyonu, iş akışı kurulumu ve operasyonu hafifleten teslim sistemleri.</p>
      </div>
      <div class="glass rounded-2xl p-8">
        <h3 class="text-xl font-semibold">Yönetici Büyümesi</h3>
        <p class="text-slate-400 mt-3">IntelliWealth danışmanlık ve eğitim ile yapay zeka stratejisini gelir icrasıyla hizalayın.</p>
      </div>
    </div>
  </section>

  <section id="journey" class="container mx-auto px-6 py-12">
    <div class="mb-10">
      <p class="uppercase tracking-[0.3em] text-xs text-slate-500">Müşteri yolculuğu</p>
      <h2 class="section-title mt-3">Keşiften tekrar eden gelire uzanan rehberli yol.</h2>
      <p class="section-subtitle mt-3">Her aşama niyetli, sürükleyici ve uygulanabilir tasarlandı.</p>
    </div>
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
      <div class="journey-step">
        <h3 class="text-lg font-semibold">01 Keşfet</h3>
        <p class="text-sm text-slate-400 mt-2">BizOp sinyalleri, içerik kancaları ve katalog önizlemeleri teklifi şekillendirir.</p>
      </div>
      <div class="journey-step">
        <h3 class="text-lg font-semibold">02 Seç</h3>
        <p class="text-sm text-slate-400 mt-2">Net ROI çıpalarıyla ürün, eğitim veya danışmanlık yolunu seçin.</p>
      </div>
      <div class="journey-step">
        <h3 class="text-lg font-semibold">03 Aktive Et</h3>
        <p class="text-sm text-slate-400 mt-2">Shopier üzerinden ödeme yapın, anında onboarding ve playbook alın.</p>
      </div>
      <div class="journey-step">
        <h3 class="text-lg font-semibold">04 Ölçekle</h3>
        <p class="text-sm text-slate-400 mt-2">Otomatik raporlama, optimizasyon ve yeni teklifler büyümeyi sürdürür.</p>
      </div>
    </div>
  </section>

  <section id="featured" class="container mx-auto px-6 py-12">
    <div class="mb-10">
      <p class="uppercase tracking-[0.3em] text-xs text-slate-500">Öne çıkan teklifler</p>
      <h2 class="section-title mt-3">Hemen ödeme alabilecek amiral programlar.</h2>
      <p class="section-subtitle mt-3">Gelir ivmesi ve otomasyon için en yüksek kaldıraçlı teklifler.</p>
    </div>
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      [[FEATURED]]
    </div>
  </section>

  <section id="portfolio" class="container mx-auto px-6 py-12">
    <div class="mb-10">
      <p class="uppercase tracking-[0.3em] text-xs text-slate-500">Portföy kasası</p>
      <h2 class="section-title mt-3">Lansmana hazır varlıklar ve platformlar.</h2>
      <p class="section-subtitle mt-3">Pazar yerlerinde yayınlanmaya hazır dijital ürünler ve playbook'lar.</p>
    </div>
    [[PRODUCTS]]
  </section>

  <section id="assurance" class="container mx-auto px-6 py-12">
    <div class="mb-10">
      <p class="uppercase tracking-[0.3em] text-xs text-slate-500">Teslimat vaadi</p>
      <h2 class="section-title mt-3">Her sipariş net teslimat ve destekle gelir.</h2>
      <p class="section-subtitle mt-3">Dijital varlıkları anında, hizmetleri net onboarding takvimiyle teslim ediyoruz.</p>
    </div>
    <div class="grid gap-6 md:grid-cols-3">
      <div class="glass rounded-2xl p-8">
        <h3 class="text-xl font-semibold">Anında Erişim</h3>
        <p class="text-slate-400 mt-3">Dijital ürünler ödeme sonrası güvenli indirme ile anında açılır.</p>
      </div>
      <div class="glass rounded-2xl p-8">
        <h3 class="text-xl font-semibold">Onboarding Zamanlaması</h3>
        <p class="text-slate-400 mt-3">Hizmetler ödeme sonrası 24-48 saat içinde kickoff alır.</p>
      </div>
      <div class="glass rounded-2xl p-8">
        <h3 class="text-xl font-semibold">Operasyonel Destek</h3>
        <p class="text-slate-400 mt-3">Haftalık kontrol ve teslimat güncellemeleri her işi yolda tutar.</p>
      </div>
    </div>
  </section>

  <section id="contact" class="container mx-auto px-6 py-12">
    <div class="glass rounded-2xl p-10 flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
      <div>
        <h2 class="text-3xl font-semibold">Lansmana hazır mısınız?</h2>
        <p class="text-slate-400 mt-2">Bir yol seçin, teslimat, varlıklar ve raporlamayı orkestre edelim.</p>
      </div>
      <div class="flex flex-wrap gap-3">
        <a class="btn-primary" href="#portfolio">Ürünlerle Başla</a>
        <a class="btn-secondary" href="#featured">Danışmanlık Planla</a>
      </div>
    </div>
  </section>

  <div class="chat-widget">
    <button id="chat-toggle" class="chat-toggle" type="button">Sohbet</button>
    <div id="chat-panel" class="chat-panel" role="dialog" aria-label="AutonomaX Asistan">
      <div class="chat-header">AutonomaX Asistan</div>
      <div id="chat-body" class="chat-body">
        <div class="chat-bubble">Merhaba! Size hangi ürün veya hizmet konusunda yardımcı olabilirim?</div>
      </div>
      <div class="chat-quick">
        <button type="button" data-question="Dijital teslimat nasıl oluyor?">Dijital teslimat</button>
        <button type="button" data-question="İade politikası nedir?">İade politikası</button>
        <button type="button" data-question="Danışmanlık süreci nasıl ilerliyor?">Danışmanlık süreci</button>
        <button type="button" data-question="Hangi paket bana uygun?">Paket önerisi</button>
      </div>
      <form id="chat-form" class="chat-form">
        <input id="chat-input" class="chat-input" type="text" placeholder="Mesajınızı yazın..." autocomplete="off">
        <button class="chat-send" type="submit">Gönder</button>
      </form>
    </div>
  </div>

  <footer class="py-10 text-center text-slate-500 text-sm">
    <p>AutonomaX Commerce Studio. Gelir netliği ve icra için üretildi.</p>
  </footer>
  <script>
    document.querySelectorAll('.shopier-pay').forEach((button) => {
      button.addEventListener('click', (event) => {
        event.preventDefault();
        const sku = button.dataset.sku || 'ORDER';
        const price = button.dataset.price || '0';
        const currency = button.dataset.currency || 'USD';
        const title = button.dataset.title || 'Order';
        const orderId = `${sku}-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
        const params = new URLSearchParams({
          amount: price,
          currency,
          order_id: orderId,
          product_name: title,
        });
        window.location.href = `/api/payment/shopier/pay?${params.toString()}`;
      });
    });

    const chatToggle = document.getElementById('chat-toggle');
    const chatPanel = document.getElementById('chat-panel');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatBody = document.getElementById('chat-body');
    const chatQuick = document.querySelectorAll('.chat-quick button');
    const chatHistory = [];

    const appendMessage = (text, role) => {
      const bubble = document.createElement('div');
      bubble.className = `chat-bubble${role === 'user' ? ' user' : ''}`;
      bubble.textContent = text;
      chatBody.appendChild(bubble);
      chatBody.scrollTop = chatBody.scrollHeight;
    };

    if (chatToggle && chatPanel) {
      chatToggle.addEventListener('click', () => {
        chatPanel.classList.toggle('open');
      });
    }

    const sendMessage = async (message) => {
      appendMessage(message, 'user');
      chatHistory.push({ role: 'user', content: message });
      try {
        const response = await fetch('/api/ai/ambassador', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message, history: chatHistory.slice(-6) }),
        });
        const payload = await response.json();
        const reply = payload.reply || 'Şu anda yanıt veremiyorum, birazdan tekrar dener misiniz?';
        appendMessage(reply, 'assistant');
        chatHistory.push({ role: 'assistant', content: reply });
      } catch (error) {
        appendMessage('Bağlantı sorunu oluştu, lütfen tekrar deneyin.', 'assistant');
      }
    };

    if (chatForm && chatInput) {
      chatForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const message = chatInput.value.trim();
        if (!message) {
          return;
        }
        chatInput.value = '';
        await sendMessage(message);
      });
    }

    if (chatQuick.length) {
      chatQuick.forEach((button) => {
        button.addEventListener('click', async () => {
          const message = button.getAttribute('data-question');
          if (!message) {
            return;
          }
          await sendMessage(message);
        });
      });
    }
  </script>
</body>
</html>
    """

    final_html = template.replace("[[PRODUCTS]]", products_html)
    final_html = final_html.replace("[[FEATURED]]", featured_html)

    with open(OUTPUT_FILE, 'w') as f:
        f.write(final_html)

    print(f"Storefront deployed successfully to: {OUTPUT_FILE}")
    print(f"Total Products: {count}")


if __name__ == "__main__":
    asyncio.run(deploy())
