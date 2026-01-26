import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  Alert,
  CircularProgress
} from '@mui/material';
import { apiService } from '../services/api';

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

export const ShopfrontPage: React.FC = () => {
  const [products, setProducts] = useState<CatalogProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const catalog = await apiService.getCommerceCatalog();
        setProducts(catalog.products || []);
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
      const result = await apiService.createCheckout(product.sku);
      if (result.checkout_url) {
        window.location.href = result.checkout_url;
      }
    } catch (err: any) {
      setError(err?.message || 'Checkout failed');
    }
  };

  if (loading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Shopfront
        </Typography>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Shopfront Catalog
      </Typography>
      {error && <Alert severity="warning" sx={{ mb: 2 }}>{error}</Alert>}
      <Grid container spacing={2}>
        {products.map((product) => (
          <Grid item xs={12} md={6} lg={4} key={product.sku}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                <Typography variant="overline">{product.sku}</Typography>
                <Typography variant="h6" gutterBottom>
                  {product.title}
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  {product.short_description || product.long_description}
                </Typography>
                <Box sx={{ mb: 2 }}>
                  {(product.channels || []).map((channel) => (
                    <Chip key={channel} label={channel} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                  ))}
                </Box>
                <Box sx={{ mt: 'auto' }}>
                  <Typography variant="subtitle1" sx={{ mb: 1 }}>
                    {product.checkout_price ? `${product.checkout_price} ${product.checkout_currency || ''}` : 'Contact for pricing'}
                  </Typography>
                  <Button variant="contained" onClick={() => handleCheckout(product)}>
                    Checkout
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};
