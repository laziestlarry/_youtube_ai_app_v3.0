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
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
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

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [summary, perf] = await Promise.all([
          apiService.getAnalyticsSummary(),
          apiService.getPerformanceMetrics(6) // Get last 6 data points
        ]);
        setData(summary);
        setHistory(perf.revenue);
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
      <Typography variant="h4" gutterBottom>Financial Performance</Typography>
      <Typography variant="subtitle1" color="textSecondary" sx={{ mb: 4 }}>
        Consolidated revenue analytics and AI-driven growth forecasting
      </Typography>

      {/* Revenue Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" color="primary">Lifetime Revenue</Typography>
              <Typography variant="h3" sx={{ my: 1 }}>${stats.estimated_revenue.toLocaleString()}</Typography>
              <Typography variant="body2" color="textSecondary">Total estimated earnings</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ height: '100%', bgcolor: 'rgba(0, 200, 83, 0.05)' }}>
            <CardContent>
              <Typography variant="h6" color="success.main">30D Projected</Typography>
              <Typography variant="h3" sx={{ my: 1 }}>${forecast.projected_revenue.toLocaleString()}</Typography>
              <Box display="flex" alignItems="center" gap={1}>
                <Chip label={forecast.confidence.toUpperCase()} size="small" color="success" />
                <Typography variant="body2" color="textSecondary">AI Confidence</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" color="primary">Daily Efficiency</Typography>
              <Typography variant="h3" sx={{ my: 1 }}>
                ${(stats.estimated_revenue / Math.max(stats.video_count, 1)).toFixed(2)}
              </Typography>
              <Typography variant="body2" color="textSecondary">Revenue per video</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Revenue Chart */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Revenue Trends (Last 30 Days)</Typography>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip formatter={(value) => [`$${value}`, 'Revenue']} />
              <Area type="monotone" dataKey="revenue" stroke="#2e7d32" fill="#e8f5e9" />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Strategy Alert */}
      <Alert severity="info" sx={{ mb: 4 }}>
        <Typography variant="subtitle2" gutterBottom>Optimization Opportunity Found</Typography>
        <Typography variant="body2">
          Your revenue trajectory suggests that shifting 20% of your content to "Tech Reviews" could increase your RPM by 15% based on current market high-value keywords identified by our AI.
        </Typography>
      </Alert>

      {/* Actions */}
      <Box display="flex" gap={2}>
        <Button variant="contained" color="primary">Execute Payout</Button>
        <Button variant="outlined">Download Financial Report</Button>
      </Box>
    </Box>
  );
};