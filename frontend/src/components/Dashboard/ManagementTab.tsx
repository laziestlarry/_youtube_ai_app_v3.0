import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Alert,
  LinearProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  PlayArrow,
  Edit,
  Delete,
  Upload,
  Analytics,
  TrendingUp,
  Schedule,
  MonetizationOn,
  ContentCopy,
  Visibility
} from '@mui/icons-material';
import { mockData } from '../../services/api';

interface ContentItem {
  id: string;
  title: string;
  status: 'draft' | 'scheduled' | 'published' | 'archived';
  type: 'video' | 'short' | 'live';
  uploadDate: string;
  views: number;
  revenue: number;
  thumbnail: string;
}

export const ManagementTab: React.FC = () => {
  const [content, setContent] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedContent, setSelectedContent] = useState<ContentItem | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [contentType, setContentType] = useState('video');
  const [autoOptimize, setAutoOptimize] = useState(true);

  useEffect(() => {
    // Simulate loading content data
    setTimeout(() => {
      setContent([
        {
          id: '1',
          title: 'How to Build a YouTube Empire with AI',
          status: 'published',
          type: 'video',
          uploadDate: '2024-01-15',
          views: 125000,
          revenue: 450.25,
          thumbnail: '/thumbnails/video1.jpg'
        },
        {
          id: '2',
          title: 'AI Content Creation Secrets Revealed',
          status: 'scheduled',
          type: 'video',
          uploadDate: '2024-01-20',
          views: 0,
          revenue: 0,
          thumbnail: '/thumbnails/video2.jpg'
        },
        {
          id: '3',
          title: 'Quick Tips: Boost Your CPM',
          status: 'draft',
          type: 'short',
          uploadDate: '',
          views: 0,
          revenue: 0,
          thumbnail: '/thumbnails/short1.jpg'
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published': return 'success';
      case 'scheduled': return 'warning';
      case 'draft': return 'default';
      case 'archived': return 'error';
      default: return 'default';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'video': return <PlayArrow />;
      case 'short': return <ContentCopy />;
      case 'live': return <Visibility />;
      default: return <PlayArrow />;
    }
  };

  const handleContentAction = (action: string, contentId: string) => {
    console.log(`${action} content ${contentId}`);
    // Implement actual actions here
  };

  const handleGenerateContent = () => {
    setDialogOpen(true);
  };

  const handleOptimizeContent = (contentId: string) => {
    console.log(`Optimizing content ${contentId}`);
    // Implement AI-powered content optimization
  };

  if (loading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Content Management
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Content Management & Profit Optimization
      </Typography>

      {/* Quick Actions */}
      <Box sx={{ display: 'flex', gap: 2, mb: 4, flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<Upload />}
          onClick={handleGenerateContent}
        >
          Generate New Content
        </Button>
        <Button
          variant="outlined"
          color="primary"
          startIcon={<Analytics />}
        >
          Content Analytics
        </Button>
        <Button
          variant="outlined"
          color="secondary"
          startIcon={<TrendingUp />}
        >
          Performance Insights
        </Button>
        <Button
          variant="outlined"
          startIcon={<Schedule />}
        >
          Schedule Manager
        </Button>
      </Box>

      {/* Content Library */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Content Library
          </Typography>
          <List>
            {content.map((item) => (
              <ListItem
                key={item.id}
                sx={{
                  border: '1px solid #e0e0e0',
                  borderRadius: 1,
                  mb: 1,
                  '&:hover': { backgroundColor: '#f5f5f5' }
                }}
              >
                <ListItemIcon>
                  {getTypeIcon(item.type)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1">
                        {item.title}
                      </Typography>
                      <Chip
                        label={item.status}
                        color={getStatusColor(item.status) as any}
                        size="small"
                      />
                      <Chip
                        label={item.type}
                        variant="outlined"
                        size="small"
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        Upload Date: {item.uploadDate || 'Not uploaded'}
                      </Typography>
                      {item.status === 'published' && (
                        <Typography variant="body2" color="textSecondary">
                          Views: {item.views.toLocaleString()} | Revenue: ${item.revenue.toFixed(2)}
                        </Typography>
                      )}
                    </Box>
                  }
                />
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    size="small"
                    startIcon={<Edit />}
                    onClick={() => handleContentAction('edit', item.id)}
                  >
                    Edit
                  </Button>
                  <Button
                    size="small"
                    startIcon={<Analytics />}
                    onClick={() => handleOptimizeContent(item.id)}
                  >
                    Optimize
                  </Button>
                  <Button
                    size="small"
                    color="error"
                    startIcon={<Delete />}
                    onClick={() => handleContentAction('delete', item.id)}
                  >
                    Delete
                  </Button>
                </Box>
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>

      {/* Profit Optimization Tools */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
        <Box sx={{ flex: '1 1 400px', minWidth: '300px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🎯 Profit Optimization
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={autoOptimize}
                      onChange={(e) => setAutoOptimize(e.target.checked)}
                    />
                  }
                  label="Auto-optimize content for maximum revenue"
                />
                <Button
                  variant="contained"
                  color="primary"
                  fullWidth
                  startIcon={<TrendingUp />}
                >
                  Run Revenue Analysis
                </Button>
                <Button
                  variant="outlined"
                  color="primary"
                  fullWidth
                  startIcon={<MonetizationOn />}
                >
                  Optimize CPM Settings
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 400px', minWidth: '300px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 Performance Insights
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Alert severity="info">
                  <Typography variant="body2">
                    <strong>Top performing content:</strong> "How to Build a YouTube Empire with AI"
                  </Typography>
                  <Typography variant="body2">
                    Revenue: $450.25 | Views: 125,000 | CPM: $3.60
                  </Typography>
                </Alert>
                <Alert severity="success">
                  <Typography variant="body2">
                    <strong>Optimization opportunity:</strong> Increase video length to 8+ minutes for mid-roll ads
                  </Typography>
                </Alert>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Content Generation Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Generate New Content</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 2 }}>
            <TextField
              fullWidth
              label="Content Topic"
              placeholder="Enter a topic or keyword for content generation"
              multiline
              rows={3}
            />
            <FormControl fullWidth>
              <InputLabel>Content Type</InputLabel>
              <Select
                value={contentType}
                onChange={(e) => setContentType(e.target.value)}
              >
                <MenuItem value="video">Long-form Video (8+ min)</MenuItem>
                <MenuItem value="short">YouTube Short</MenuItem>
                <MenuItem value="live">Live Stream</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Target Audience"
              placeholder="e.g., Tech enthusiasts, beginners, professionals"
            />
            <FormControlLabel
              control={<Switch defaultChecked />}
              label="Include AI-generated thumbnail"
            />
            <FormControlLabel
              control={<Switch defaultChecked />}
              label="Optimize for maximum revenue"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setDialogOpen(false)}>
            Generate Content
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};