import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Alert,
  Button,
  CircularProgress
} from '@mui/material';
import { apiService } from '../../services/api';

type CommerceSummary = {
  journey_events: number;
  loyalty_points: number;
  loyalty_tier: string;
  active_contracts: number;
};

type LoyaltyLedgerItem = {
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
  ledger: LoyaltyLedgerItem[];
};

export const CommerceTab: React.FC = () => {
  const [summary, setSummary] = useState<CommerceSummary | null>(null);
  const [loyalty, setLoyalty] = useState<LoyaltyAccount | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [summaryData, loyaltyData] = await Promise.all([
          apiService.getCommerceSummary(),
          apiService.getCommerceLoyalty()
        ]);
        setSummary(summaryData);
        setLoyalty(loyaltyData);
      } catch (err: any) {
        setError(err?.message || 'Failed to load commerce data');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Commerce Control
        </Typography>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Commerce Control
      </Typography>
      {error && <Alert severity="warning" sx={{ mb: 2 }}>{error}</Alert>}

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="overline">Journey Events</Typography>
              <Typography variant="h5">{summary?.journey_events ?? 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="overline">Loyalty Points</Typography>
              <Typography variant="h5">{summary?.loyalty_points ?? 0}</Typography>
              <Typography variant="body2" color="textSecondary">
                Tier: {summary?.loyalty_tier ?? 'bronze'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="overline">Active Contracts</Typography>
              <Typography variant="h5">{summary?.active_contracts ?? 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="overline">Shopfront</Typography>
              <Button variant="contained" color="primary" href="/shop">
                Open Catalog
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Loyalty Ledger
          </Typography>
          {loyalty?.ledger?.length ? (
            loyalty.ledger.slice(0, 8).map((entry) => (
              <Box key={entry.id} sx={{ mb: 1 }}>
                <Typography variant="body2">
                  {entry.reason} · {entry.delta > 0 ? `+${entry.delta}` : entry.delta} points
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {entry.reference || 'no reference'} · {new Date(entry.created_at).toLocaleString()}
                </Typography>
              </Box>
            ))
          ) : (
            <Typography variant="body2" color="textSecondary">
              No loyalty activity yet.
            </Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};
