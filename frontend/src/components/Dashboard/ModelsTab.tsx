import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  LinearProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction
} from '@mui/material';
import {
  Psychology,
  TrendingUp,
  Settings,
  PlayArrow,
  Pause,
  Refresh,
  CheckCircle,
  Warning,
  Error,
  Schedule
} from '@mui/icons-material';
import type { AIModel } from '../../types/dashboard';

export const ModelsTab: React.FC = () => {
  const [models, setModels] = useState<AIModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedModel, setSelectedModel] = useState<AIModel | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState<Record<string, number>>({});

  useEffect(() => {
    // Simulate loading AI models
    setTimeout(() => {
      setModels([
        {
          name: "Content Generator v2.1",
          status: "active",
          accuracy: 94.5,
          lastTrained: "2024-01-20",
          type: "content",
          version: "2.1.0",
          performance: "excellent",
          trainingData: "50K+ videos",
          revenueImpact: "+23%"
        },
        {
          name: "Thumbnail Optimizer",
          status: "training",
          accuracy: 89.2,
          lastTrained: "2024-01-18",
          type: "thumbnail",
          version: "1.8.2",
          performance: "good",
          trainingData: "25K+ thumbnails",
          revenueImpact: "+15%"
        },
        {
          name: "Title Generator",
          status: "active",
          accuracy: 91.8,
          lastTrained: "2024-01-15",
          type: "title",
          version: "1.5.0",
          performance: "excellent",
          trainingData: "100K+ titles",
          revenueImpact: "+18%"
        },
        {
          name: "Description Writer",
          status: "inactive",
          accuracy: 87.3,
          lastTrained: "2024-01-10",
          type: "description",
          version: "1.2.1",
          performance: "good",
          trainingData: "75K+ descriptions",
          revenueImpact: "+12%"
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle color="success" />;
      case 'training': return <Schedule color="warning" />;
      case 'inactive': return <Pause color="disabled" />;
      case 'error': return <Error color="error" />;
      default: return <Warning color="warning" />;
    }
  };

  const getPerformanceColor = (performance: string) => {
    switch (performance) {
      case 'excellent': return 'success';
      case 'good': return 'primary';
      case 'fair': return 'warning';
      case 'poor': return 'error';
      default: return 'default';
    }
  };

  const handleTrainModel = (modelName: string) => {
    setTrainingProgress(prev => ({ ...prev, [modelName]: 0 }));
    
    // Simulate training progress
    const interval = setInterval(() => {
      setTrainingProgress(prev => {
        const current = prev[modelName] || 0;
        if (current >= 100) {
          clearInterval(interval);
          return prev;
        }
        return { ...prev, [modelName]: current + 10 };
      });
    }, 500);
  };

  const handleOptimizeModel = (modelName: string) => {
    console.log(`Optimizing model: ${modelName}`);
    // Implement model optimization logic
  };

  if (loading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          AI Model Management
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        AI Model Management & Optimization
      </Typography>

      {/* Model Overview */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
        <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                Active Models
              </Typography>
              <Typography variant="h4">
                {models.filter(m => m.status === 'active').length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Currently operational
              </Typography>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                Average Accuracy
              </Typography>
              <Typography variant="h4">
                {Math.round(models.reduce((acc, m) => acc + m.accuracy, 0) / models.length)}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Across all models
              </Typography>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                Revenue Impact
              </Typography>
              <Typography variant="h4" sx={{ color: 'success.main' }}>
                +17%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Average improvement
              </Typography>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                Training Status
              </Typography>
              <Typography variant="h4">
                {models.filter(m => m.status === 'training').length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Currently training
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* AI Models List */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            AI Models
          </Typography>
          <List>
            {models.map((model) => (
              <ListItem
                key={model.name}
                sx={{
                  border: '1px solid #e0e0e0',
                  borderRadius: 1,
                  mb: 1,
                  '&:hover': { backgroundColor: '#f5f5f5' }
                }}
              >
                <ListItemIcon>
                  <Psychology />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1">
                        {model.name}
                      </Typography>
                      <Chip
                        label={model.status}
                        color={model.status === 'active' ? 'success' : model.status === 'training' ? 'warning' : 'default'}
                        size="small"
                      />
                      <Chip
                        label={`v${model.version}`}
                        variant="outlined"
                        size="small"
                      />
                      <Chip
                        label={model.performance}
                        color={getPerformanceColor(model.performance) as any}
                        size="small"
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        Accuracy: {model.accuracy}% | Type: {model.type} | Last Trained: {model.lastTrained}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Training Data: {model.trainingData} | Revenue Impact: {model.revenueImpact}
                      </Typography>
                      {model.status === 'training' && trainingProgress[model.name] !== undefined && (
                        <Box sx={{ mt: 1 }}>
                          <LinearProgress 
                            variant="determinate" 
                            value={trainingProgress[model.name]} 
                            sx={{ height: 8, borderRadius: 4 }}
                          />
                          <Typography variant="caption" color="textSecondary">
                            Training Progress: {trainingProgress[model.name]}%
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {model.status === 'active' && (
                      <Button
                        size="small"
                        startIcon={<Refresh />}
                        onClick={() => handleTrainModel(model.name)}
                      >
                        Retrain
                      </Button>
                    )}
                    {model.status === 'inactive' && (
                      <Button
                        size="small"
                        startIcon={<PlayArrow />}
                        onClick={() => handleOptimizeModel(model.name)}
                      >
                        Activate
                      </Button>
                    )}
                    <Button
                      size="small"
                      startIcon={<Settings />}
                      onClick={() => handleOptimizeModel(model.name)}
                    >
                      Optimize
                    </Button>
                  </Box>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>

      {/* Model Performance Insights */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
        <Box sx={{ flex: '1 1 500px', minWidth: '300px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🎯 Model Performance Insights
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Alert severity="success">
                  <Typography variant="body2">
                    <strong>Content Generator v2.1:</strong> 23% revenue increase, excellent performance
                  </Typography>
                </Alert>
                <Alert severity="info">
                  <Typography variant="body2">
                    <strong>Thumbnail Optimizer:</strong> Currently training with new dataset
                  </Typography>
                </Alert>
                <Alert severity="warning">
                  <Typography variant="body2">
                    <strong>Description Writer:</strong> Needs retraining with updated content patterns
                  </Typography>
                </Alert>
              </Box>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🚀 Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  fullWidth
                  startIcon={<TrendingUp />}
                >
                  Run Performance Analysis
                </Button>
                <Button
                  variant="outlined"
                  color="primary"
                  fullWidth
                  startIcon={<Refresh />}
                >
                  Retrain All Models
                </Button>
                <Button
                  variant="outlined"
                  color="secondary"
                  fullWidth
                  startIcon={<Settings />}
                >
                  Optimize Settings
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Model Configuration */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Model Configuration
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControlLabel
              control={<Switch defaultChecked />}
              label="Auto-optimize models for maximum revenue"
            />
            <FormControlLabel
              control={<Switch defaultChecked />}
              label="Enable real-time model updates"
            />
            <FormControlLabel
              control={<Switch />}
              label="Use advanced AI algorithms (higher cost)"
            />
            <FormControlLabel
              control={<Switch defaultChecked />}
              label="Automatically retrain models weekly"
            />
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};