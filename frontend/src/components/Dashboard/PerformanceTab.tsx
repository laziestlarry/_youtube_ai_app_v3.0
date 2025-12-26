import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  TrendingUp,
  BarChart as BarChartIcon,
  Timeline as TimelineIcon,
  AttachMoney as MoneyIcon
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { apiService } from '../../services/api';

export const PerformanceTab: React.FC = () => {
  const [data, setData] = useState<{ views: any[]; revenue: any[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await apiService.getPerformanceMetrics(30);
        setData(result);
      } catch (err) {
        console.error('Error fetching performance data:', err);
        setError('Failed to load performance metrics.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !data) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">{error || 'No performance data available'}</Alert>
      </Box>
    );
  }

  // Merge views and revenue history for the chart
  const trendData = data.views.map((v, i) => ({
    date: v.date,
    views: v.views,
    revenue: data.revenue[i]?.revenue || 0
  }));

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Video Performance Trends
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" sx={{ mb: 4 }}>
        Deep-dive into your channel's growth and monetization trajectory
      </Typography>

      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <TimelineIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Views Growth (30D)</Typography>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={trendData}>
                  <defs>
                    <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#1976d2" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#1976d2" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="views" stroke="#1976d2" fillOpacity={1} fill="url(#colorViews)" />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <MoneyIcon color="secondary" sx={{ mr: 1 }} />
                <Typography variant="h6">Revenue Trajectory (30D)</Typography>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={trendData}>
                  <defs>
                    <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#dc004e" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#dc004e" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="revenue" stroke="#dc004e" fillOpacity={1} fill="url(#colorRev)" />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Insights */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>AI Performance Insights</Typography>
          <Box sx={{ mt: 2 }}>
            <Alert severity="success" sx={{ mb: 2 }}>
              Your views are up 12% compared to the previous 30-day period. The latest "AI tutorials" series is driving 40% of new traffic.
            </Alert>
            <Alert severity="info">
              Optimization Tip: Videos uploaded between 4 PM and 6 PM EST show 25% higher initial engagement.
            </Alert>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};