import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Alert,
  CircularProgress,
  Divider,
  Paper
} from '@mui/material';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { apiService } from '../../services/api';
import { AnalyticsSummary } from '../../types/dashboard';

export const EarningsTab: React.FC = () => {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [igniteStats, setIgniteStats] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [summary, perf, ignite] = await Promise.all([
          apiService.getAnalyticsSummary(),
          apiService.getPerformanceMetrics(6),
          apiService.getIgniteRevenueStats()
        ]);
        setData(summary);
        setHistory(perf.revenue);
        setIgniteStats(ignite);
      } catch (err) {
        console.error('Error fetching earnings:', err);
        setError('Failed to load financial data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>;
  if (error || !data) return <Box sx={{ p: 4 }}><Alert severity="error">{error || 'No data'}</Alert></Box>;

  const { stats, forecast } = data;

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>Financial Performance</Typography>
      <Typography variant="subtitle1" color="textSecondary" sx={{ mb: 4 }}>
        Consolidated revenue analytics and AI-driven growth forecasting
      </Typography>

      {/* Revenue Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ height: '100%', borderRadius: 3 }}>
            <CardContent>
              <Typography variant="h6" color="primary">Lifetime Revenue</Typography>
              <Typography variant="h3" sx={{ my: 1, fontWeight: 700 }}>${stats.estimated_revenue.toLocaleString()}</Typography>
              <Typography variant="body2" color="textSecondary">Total estimated earnings</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ height: '100%', bgcolor: 'rgba(0, 200, 83, 0.05)', borderRadius: 3 }}>
            <CardContent>
              <Typography variant="h6" color="success.main">30D Projected</Typography>
              <Typography variant="h3" sx={{ my: 1, fontWeight: 700 }}>${forecast.projected_revenue.toLocaleString()}</Typography>
              <Box display="flex" alignItems="center" gap={1}>
                <Chip label={forecast.confidence.toUpperCase()} size="small" color="success" />
                <Typography variant="body2" color="textSecondary">AI Confidence</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ height: '100%', borderRadius: 3 }}>
            <CardContent>
              <Typography variant="h6" color="primary">Daily Efficiency</Typography>
              <Typography variant="h3" sx={{ my: 1, fontWeight: 700 }}>
                ${(stats.estimated_revenue / Math.max(stats.video_count, 1)).toFixed(2)}
              </Typography>
              <Typography variant="body2" color="textSecondary">Revenue per video</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Land Ignite Stats (Project Ignite) */}
      {igniteStats && (
        <Card sx={{
          mb: 4,
          borderRadius: 4,
          background: 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
          color: 'white',
          boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.2)'
        }}>
          <CardContent>
            <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
              🚀 Land Ignite Performance Stats
            </Typography>
            <Divider sx={{ bgcolor: 'rgba(255,255,255,0.2)', mb: 2 }} />
            <Grid container spacing={2}>
              <Grid size={{ xs: 6, md: 3 }}>
                <Typography variant="caption" sx={{ opacity: 0.8 }}>Monthly Estimate</Typography>
                <Typography variant="h5" sx={{ fontWeight: 700 }}>${igniteStats.monthly_estimate.toLocaleString()}</Typography>
              </Grid>
              <Grid size={{ xs: 6, md: 3 }}>
                <Typography variant="caption" sx={{ opacity: 0.8 }}>Daily Average</Typography>
                <Typography variant="h5" sx={{ fontWeight: 700 }}>${igniteStats.daily_average.toLocaleString()}</Typography>
              </Grid>
              <Grid size={{ xs: 6, md: 3 }}>
                <Typography variant="caption" sx={{ opacity: 0.8 }}>Active Campaigns</Typography>
                <Typography variant="h5" sx={{ fontWeight: 700 }}>{igniteStats.active_campaigns}</Typography>
              </Grid>
              <Grid size={{ xs: 6, md: 3 }}>
                <Typography variant="caption" sx={{ opacity: 0.8 }}>Projected Yearly</Typography>
                <Typography variant="h5" sx={{ fontWeight: 700 }}>${igniteStats.projected_yearly.toLocaleString()}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Revenue Chart */}
      <Card sx={{ mb: 4, borderRadius: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Revenue Trends (Last 30 Days)</Typography>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip formatter={(value: any) => [`$${value}`, 'Revenue']} />
              <Area type="monotone" dataKey="revenue" stroke="#2196F3" fill="#E3F2FD" />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Strategy Alert */}
      <Alert severity="info" sx={{ mb: 4, borderRadius: 2, border: '1px solid #2196F3' }}>
        <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 700 }}>Optimization Opportunity Found</Typography>
        <Typography variant="body2">
          Your revenue trajectory suggests that shifting 20% of your content to "Tech Reviews" could increase your RPM by 15% based on current market high-value keywords identified by our AI.
        </Typography>
      </Alert>

      {/* Actions */}
      <Box display="flex" gap={2}>
        <Button variant="contained" color="primary" sx={{ borderRadius: 2, px: 4 }}>Execute Payout</Button>
        <Button variant="outlined" sx={{ borderRadius: 2, px: 4 }}>Download Financial Report</Button>
      </Box>
    </Box>
  );
};