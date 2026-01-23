'use client';

import { useEffect, useState } from 'react';
import AppHeader from '@/components/app-header';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { getJson, postJson } from '@/lib/backend';

type CatalogProduct = {
  sku: string;
  title: string;
  short_description?: string;
  long_description?: string;
  image_url?: string;
  channels?: string[];
  checkout_price?: number;
  checkout_currency?: string;
  shopier_url?: string;
};

type CatalogResponse = {
  count: number;
  products: CatalogProduct[];
};

type PrintableOffer = {
  id: number;
  sku: string;
  title: string;
  description?: string;
  price: number;
  currency: string;
  status: string;
  offer_type: string;
  asset_id?: number;
  metadata?: {
    file_format?: string;
    dimensions?: string;
    dpi?: number;
    license_terms?: string;
    tags?: string[];
  };
};

export default function ShopfrontPage() {
  const [products, setProducts] = useState<CatalogProduct[]>([]);
  const [offers, setOffers] = useState<PrintableOffer[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [data, offerData] = await Promise.all([
          getJson<CatalogResponse>('/api/commerce/catalog'),
          getJson<PrintableOffer[]>('/api/commerce/offers?offer_type=printable'),
        ]);
        setProducts(data.products || []);
        setOffers(offerData || []);
      } catch (err: any) {
        setError(err?.message || 'Failed to load catalog');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleCheckout = async (product: CatalogProduct) => {
    if (product.shopier_url) {
      window.location.href = product.shopier_url;
      return;
    }
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
      const headers = token ? { Authorization: `Bearer ${token}` } : undefined;
      const result = await postJson<{ checkout_url: string }>('/api/commerce/checkout', {
        sku: product.sku,
      }, { headers });
      if (result.checkout_url) {
        window.location.href = result.checkout_url;
      }
    } catch (err: any) {
      setError(err?.message || 'Checkout failed');
    }
  };

  const handleOfferCheckout = async (offer: PrintableOffer) => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
      const headers = token ? { Authorization: `Bearer ${token}` } : undefined;
      const result = await postJson<{ checkout_url: string }>('/api/commerce/checkout', {
        offer_id: offer.id,
      }, { headers });
      if (result.checkout_url) {
        window.location.href = result.checkout_url;
      }
    } catch (err: any) {
      setError(err?.message || 'Checkout failed');
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <AppHeader />
      <main className="container mx-auto flex-1 px-4 py-8">
        <div className="mb-6">
          <h2 className="font-headline text-3xl font-bold">Shopfront</h2>
          <p className="text-muted-foreground">Curated offers from Autonomax and Alexandria portfolio.</p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-sm text-muted-foreground">Loading catalog...</div>
        ) : (
          <div className="space-y-10">
            <section>
              <div className="mb-4">
                <h3 className="text-2xl font-semibold">Zen-Art Wall Printables</h3>
                <p className="text-sm text-muted-foreground">
                  Instant downloadable art packs for mindful spaces.
                </p>
              </div>
              {offers.length ? (
                <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                  {offers.map((offer) => (
                    <Card key={offer.id} className="flex h-full flex-col">
                      <CardHeader>
                        <CardTitle>{offer.title}</CardTitle>
                        <CardDescription>{offer.description}</CardDescription>
                      </CardHeader>
                      <CardContent className="mt-auto space-y-4">
                        <div className="flex flex-wrap gap-2">
                          {(offer.metadata?.tags || []).map((tag) => (
                            <Badge key={tag} variant="secondary">
                              {tag}
                            </Badge>
                          ))}
                          {offer.metadata?.file_format && (
                            <Badge variant="outline">{offer.metadata.file_format}</Badge>
                          )}
                          {offer.metadata?.dimensions && (
                            <Badge variant="outline">{offer.metadata.dimensions}</Badge>
                          )}
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-semibold">
                            {offer.price} {offer.currency}
                          </span>
                          <Button onClick={() => handleOfferCheckout(offer)}>Checkout</Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">No printables listed yet.</div>
              )}
            </section>

            <section>
              <div className="mb-4">
                <h3 className="text-2xl font-semibold">Portfolio Catalog</h3>
                <p className="text-sm text-muted-foreground">
                  Strategic offers and service bundles from the network.
                </p>
              </div>
              <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                {products.map((product) => (
                  <Card key={product.sku} className="flex h-full flex-col">
                    <CardHeader>
                      <CardTitle>{product.title}</CardTitle>
                      <CardDescription>{product.short_description || product.long_description}</CardDescription>
                    </CardHeader>
                    <CardContent className="mt-auto space-y-4">
                      <div className="flex flex-wrap gap-2">
                        {(product.channels || []).map((channel) => (
                          <Badge key={channel} variant="secondary">
                            {channel}
                          </Badge>
                        ))}
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-semibold">
                          {product.checkout_price
                            ? `${product.checkout_price} ${product.checkout_currency || ''}`
                            : 'Custom pricing'}
                        </span>
                        <Button onClick={() => handleCheckout(product)}>Checkout</Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </section>
          </div>
        )}
      </main>
    </div>
  );
}
