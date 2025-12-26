import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Grid
} from '@mui/material';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';
import type { VideoAnalytics, AnalyticsSummary } from '../../types/dashboard';
import { apiService } from '../../services/api';

export const AnalyticsTab: React.FC = () => {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const summary = await apiService.getAnalyticsSummary();
        setData(summary);
      } catch (err) {
        console.error('Error fetching analytics data:', err);
        setError('Failed to load analytics data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>Analytics Dashboard</Typography>
        <Typography>Loading production analytics data...</Typography>
      </Box>
    );
  }

  if (error || !data) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>Analytics Dashboard</Typography>
        <Typography color="error">{error || 'No data available'}</Typography>
      </Box>
    );
  }

  const { stats, forecast, recent_videos } = data;

  // Prepare chart data
  const chartData = recent_videos.slice(0, 5).map(v => ({
    name: v.title.length > 20 ? v.title.substring(0, 20) + '...' : v.title,
    views: v.views,
    likes: v.likes
  }));

  const confidenceColor = (conf: string) => {
    switch (conf) {
      case 'high': return 'success';
      case 'medium': return 'warning';
      default: return 'error';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Analytics Dashboard
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">Total Views</Typography>
              <Typography variant="h4">{stats.view_count.toLocaleString()}</Typography>
              <Typography variant="body2" color="textSecondary">Lifetime views</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">Subscribers</Typography>
              <Typography variant="h4">{stats.subscriber_count.toLocaleString()}</Typography>
              <Typography variant="body2" color="textSecondary">Channel subscribers</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">Total Revenue</Typography>
              <Typography variant="h4">${stats.estimated_revenue.toLocaleString()}</Typography>
              <Typography variant="body2" color="textSecondary">Lifetime earnings</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ bgcolor: 'rgba(0, 255, 0, 0.05)' }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                <Typography variant="h6" color="secondary">30D Forecast</Typography>
                <Chip
                  size="small"
                  label={forecast.confidence.toUpperCase()}
                  color={confidenceColor(forecast.confidence) as any}
                />
              </Box>
              <Typography variant="h4">${forecast.projected_revenue.toLocaleString()}</Typography>
              <Typography variant="body2" color="textSecondary">AI Projected Earnings</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Box sx={{ mb: 4 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Recent Video Performance</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="views" fill="#8884d8" name="Views" />
                <Bar dataKey="likes" fill="#82ca9d" name="Likes" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Box>

      {/* Video Analytics Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Detailed Metrics
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Video Title</TableCell>
                  <TableCell align="right">Views</TableCell>
                  <TableCell align="right">Likes</TableCell>
                  <TableCell align="right">Comments</TableCell>
                  <TableCell align="right">Revenue</TableCell>
                  <TableCell align="right">Upload Date</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recent_videos.length > 0 ? (
                  recent_videos.map((video, index) => (
                    <TableRow key={index}>
                      <TableCell component="th" scope="row">{video.title}</TableCell>
                      <TableCell align="right">{video.views.toLocaleString()}</TableCell>
                      <TableCell align="right">{video.likes.toLocaleString()}</TableCell>
                      <TableCell align="right">{video.comments.toLocaleString()}</TableCell>
                      <TableCell align="right">${video.revenue.toFixed(2)}</TableCell>
                      <TableCell align="right">
                        {video.upload_date ? new Date(video.upload_date).toLocaleDateString() : 'N/A'}
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} align="center">No recent videos found</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};