'use client';

import { useEffect, useState } from 'react';
import AppHeader from '@/components/app-header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { buildBackendUrl, getJson, postJson } from '@/lib/backend';

type CommerceSummary = {
  journey_events: number;
  loyalty_points: number;
  loyalty_tier: string;
  active_contracts: number;
};

type LoyaltyEntry = {
  id: number;
  delta: number;
  reason: string;
  reference?: string;
  created_at: string;
};

type LoyaltyAccount = {
  user_id: number;
  points_balance: number;
  tier: string;
  updated_at?: string;
  ledger: LoyaltyEntry[];
};

type OfferResult = {
  id: number;
  title: string;
  sku: string;
  price: number;
  currency: string;
};

export default function CommercePage() {
  const [summary, setSummary] = useState<CommerceSummary | null>(null);
  const [loyalty, setLoyalty] = useState<LoyaltyAccount | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [accessKey, setAccessKey] = useState('');
  const [authError, setAuthError] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [offerTitle, setOfferTitle] = useState('');
  const [offerDescription, setOfferDescription] = useState('');
  const [offerPrice, setOfferPrice] = useState('24');
  const [offerCurrency, setOfferCurrency] = useState('USD');
  const [offerFormat, setOfferFormat] = useState('PDF');
  const [offerDimensions, setOfferDimensions] = useState('A4, A3, 11x14');
  const [offerDpi, setOfferDpi] = useState('300');
  const [offerLicense, setOfferLicense] = useState('Personal use only.');
  const [offerTags, setOfferTags] = useState('zen, minimalist, wall art');
  const [offerFile, setOfferFile] = useState<File | null>(null);
  const [offerResult, setOfferResult] = useState<OfferResult | null>(null);
  const [offerCheckoutUrl, setOfferCheckoutUrl] = useState<string | null>(null);
  const [offerLoading, setOfferLoading] = useState(false);
  const [offerError, setOfferError] = useState<string | null>(null);

  useEffect(() => {
    const load = async (authToken?: string) => {
      try {
        const headers = authToken ? { Authorization: `Bearer ${authToken}` } : undefined;
        const [summaryData, loyaltyData] = await Promise.all([
          getJson<CommerceSummary>('/api/commerce/summary', { headers }),
          getJson<LoyaltyAccount>('/api/commerce/loyalty', { headers }),
        ]);
        setSummary(summaryData);
        setLoyalty(loyaltyData);
        setError(null);
      } catch (err: any) {
        const message = err?.message || 'Commerce data requires authentication.';
        setError(message);
        if (message.includes('(401)')) {
          setAuthError('Authentication required. Use your access key to continue.');
        }
      }
    };
    const stored = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    if (stored) {
      setToken(stored);
      load(stored);
    } else {
      load();
    }
  }, []);

  const handleKeyLogin = async () => {
    if (!accessKey.trim()) {
      setAuthError('Access key required.');
      return;
    }
    setAuthLoading(true);
    try {
      const result = await postJson<{ access_token: string }>('/api/auth/login-with-key', {
        access_key: accessKey.trim(),
      });
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', result.access_token);
      }
      setToken(result.access_token);
      setAuthError(null);
      const headers = { Authorization: `Bearer ${result.access_token}` };
      const [summaryData, loyaltyData] = await Promise.all([
        getJson<CommerceSummary>('/api/commerce/summary', { headers }),
        getJson<LoyaltyAccount>('/api/commerce/loyalty', { headers }),
      ]);
      setSummary(summaryData);
      setLoyalty(loyaltyData);
      setError(null);
    } catch (err: any) {
      setAuthError(err?.message || 'Access key login failed.');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleOfferSubmit = async () => {
    if (!token) {
      setOfferError('Sign in required to create offers.');
      return;
    }
    if (!offerFile) {
      setOfferError('Upload the printable file (PDF/PNG).');
      return;
    }
    if (!offerTitle.trim()) {
      setOfferError('Offer title is required.');
      return;
    }
    setOfferLoading(true);
    setOfferError(null);
    setOfferResult(null);
    setOfferCheckoutUrl(null);

    try {
      const formData = new FormData();
      formData.append('file', offerFile);
      const uploadResponse = await fetch(buildBackendUrl('/api/commerce/assets/upload'), {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });
      if (!uploadResponse.ok) {
        const body = await uploadResponse.text();
        throw new Error(body || 'Asset upload failed');
      }
      const asset = await uploadResponse.json();

      const priceValue = Number(offerPrice);
      if (!Number.isFinite(priceValue) || priceValue < 0) {
        throw new Error('Price must be a valid number.');
      }

      const offer = await postJson<OfferResult>(
        '/api/commerce/offers',
        {
          title: offerTitle.trim(),
          description: offerDescription.trim() || null,
          price: priceValue,
          currency: offerCurrency.trim().toUpperCase() || 'USD',
          asset_id: asset.id,
          offer_type: 'printable',
          status: 'active',
          file_format: offerFormat,
          dimensions: offerDimensions,
          dpi: Number(offerDpi) || null,
          license_terms: offerLicense,
          tags: offerTags
            .split(',')
            .map((tag) => tag.trim())
            .filter(Boolean),
        },
        { headers: { Authorization: `Bearer ${token}` } },
      );

      const checkout = await postJson<{ checkout_url: string }>(
        '/api/commerce/checkout',
        { offer_id: offer.id },
        { headers: { Authorization: `Bearer ${token}` } },
      );

      setOfferResult(offer);
      setOfferCheckoutUrl(checkout.checkout_url);
    } catch (err: any) {
      setOfferError(err?.message || 'Offer creation failed.');
    } finally {
      setOfferLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <AppHeader />
      <main className="container mx-auto flex-1 px-4 py-8">
        <div className="mb-6">
          <h2 className="font-headline text-3xl font-bold">Commerce Dashboard</h2>
          <p className="text-muted-foreground">Loyalty, contracts, and customer journey signals.</p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
            {error}
          </div>
        )}

        {authError && !token && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Access Required</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Enter your Shopier access key or admin key to view commerce data.
              </p>
              <div className="flex flex-col gap-2 md:flex-row">
                <Input
                  value={accessKey}
                  onChange={(event) => setAccessKey(event.target.value)}
                  placeholder="Access key"
                />
                <Button onClick={handleKeyLogin} disabled={authLoading}>
                  {authLoading ? 'Signing in...' : 'Sign in'}
                </Button>
              </div>
              {authError && (
                <div className="text-sm text-destructive">{authError}</div>
              )}
            </CardContent>
          </Card>
        )}

        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm text-muted-foreground">Journey Events</CardTitle>
            </CardHeader>
            <CardContent className="text-2xl font-semibold">
              {summary?.journey_events ?? 0}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm text-muted-foreground">Loyalty Points</CardTitle>
            </CardHeader>
            <CardContent className="text-2xl font-semibold">
              {summary?.loyalty_points ?? 0}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm text-muted-foreground">Loyalty Tier</CardTitle>
            </CardHeader>
            <CardContent className="text-2xl font-semibold">
              {summary?.loyalty_tier ?? 'bronze'}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm text-muted-foreground">Active Contracts</CardTitle>
            </CardHeader>
            <CardContent className="text-2xl font-semibold">
              {summary?.active_contracts ?? 0}
            </CardContent>
          </Card>
        </div>

        <div className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Zen-Art Printable Builder</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-sm text-muted-foreground">
                Upload a printable (PDF/PNG) and publish a paid offer in minutes.
              </div>
              {offerError && (
                <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
                  {offerError}
                </div>
              )}
              <div className="grid gap-4 md:grid-cols-2">
                <Input
                  value={offerTitle}
                  onChange={(event) => setOfferTitle(event.target.value)}
                  placeholder="Offer title"
                />
                <Input
                  value={offerPrice}
                  onChange={(event) => setOfferPrice(event.target.value)}
                  placeholder="Price"
                  type="number"
                  min="0"
                  step="0.01"
                />
                <Input
                  value={offerCurrency}
                  onChange={(event) => setOfferCurrency(event.target.value)}
                  placeholder="Currency (USD)"
                />
                <Input
                  value={offerFormat}
                  onChange={(event) => setOfferFormat(event.target.value)}
                  placeholder="Format (PDF)"
                />
                <Input
                  value={offerDimensions}
                  onChange={(event) => setOfferDimensions(event.target.value)}
                  placeholder="Dimensions (A4, A3, 11x14)"
                />
                <Input
                  value={offerDpi}
                  onChange={(event) => setOfferDpi(event.target.value)}
                  placeholder="DPI (300)"
                />
              </div>
              <textarea
                className="min-h-[96px] w-full rounded-md border border-input bg-background p-3 text-sm"
                value={offerDescription}
                onChange={(event) => setOfferDescription(event.target.value)}
                placeholder="Short description for the printable."
              />
              <textarea
                className="min-h-[96px] w-full rounded-md border border-input bg-background p-3 text-sm"
                value={offerLicense}
                onChange={(event) => setOfferLicense(event.target.value)}
                placeholder="License terms (e.g., personal use only)."
              />
              <Input
                value={offerTags}
                onChange={(event) => setOfferTags(event.target.value)}
                placeholder="Tags (comma-separated)"
              />
              <div className="flex flex-col gap-3 md:flex-row md:items-center">
                <Input
                  type="file"
                  accept="application/pdf,image/png,image/jpeg"
                  onChange={(event) => setOfferFile(event.target.files?.[0] || null)}
                />
                <Button onClick={handleOfferSubmit} disabled={offerLoading}>
                  {offerLoading ? 'Publishing...' : 'Create Offer'}
                </Button>
              </div>
              {offerResult && (
                <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-700">
                  Offer created: {offerResult.title} ({offerResult.sku})
                </div>
              )}
              {offerCheckoutUrl && (
                <div className="rounded-lg border border-border bg-muted p-3 text-sm">
                  Checkout link: <a className="underline" href={offerCheckoutUrl}>{offerCheckoutUrl}</a>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Recent Loyalty Activity</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              {loyalty?.ledger?.length ? (
                loyalty.ledger.slice(0, 8).map((entry) => (
                  <div key={entry.id}>
                    <div className="font-medium text-foreground">
                      {entry.reason} · {entry.delta > 0 ? `+${entry.delta}` : entry.delta} points
                    </div>
                    <div>{entry.reference || 'no reference'} · {new Date(entry.created_at).toLocaleString()}</div>
                  </div>
                ))
              ) : (
                <div>No loyalty activity yet.</div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
