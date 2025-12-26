import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import { YouTube, Psychology, TrendingUp, CheckCircle } from '@mui/icons-material';
import { apiService } from '../../services/api';

const steps = [
  'YouTube Connectivity',
  'AI Integration',
  'Content Strategy',
  'Finalization'
];

export const InitializationTab: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [channels, setChannels] = useState<any[]>([]);
  const [contentType, setContentType] = useState('');
  const [isInitializing, setIsInitializing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleConnectYouTube = async () => {
    try {
      const { url } = await apiService.getYouTubeAuthUrl();
      window.location.href = url;
    } catch (err) {
      console.error('Failed to get auth URL:', err);
      setError('Failed to initiate YouTube connection. Please try again.');
    }
  };

  const handleInitializeAI = async () => {
    setIsInitializing(true);
    // Simulate AI warm-up
    setTimeout(() => {
      setIsInitializing(false);
      handleNext();
    }, 2000);
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ textAlign: 'center', py: 2 }}>
            <YouTube sx={{ fontSize: 60, color: '#FF0000', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Connect Your YouTube Channel
            </Typography>
            <Typography color="textSecondary" sx={{ mb: 3 }}>
              Allow Antigravity to sync your channel analytics and optimize your video performance.
            </Typography>
            <Button
              variant="contained"
              color="error"
              onClick={handleConnectYouTube}
              startIcon={<YouTube />}
              size="large"
            >
              Connect with Google OAuth
            </Button>
            {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
          </Box>
        );
      case 1:
        return (
          <Box sx={{ py: 2 }}>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <Psychology color="primary" />
              <Typography variant="h6">AI Engine Configuration</Typography>
            </Box>
            <Alert severity="info" sx={{ mb: 3 }}>
              We are initializing your personalized AI agents for script generation and thumbnail optimization.
            </Alert>
            {isInitializing && (
              <Box sx={{ width: '100%', mb: 2 }}>
                <LinearProgress />
                <Typography variant="caption" sx={{ mt: 1, display: 'block', textAlign: 'center' }}>
                  Warming up GPT-4 modules...
                </Typography>
              </Box>
            )}
            <Button
              variant="contained"
              onClick={handleInitializeAI}
              disabled={isInitializing}
              fullWidth
            >
              Initialize AI Engine
            </Button>
          </Box>
        );
      case 2:
        return (
          <Box sx={{ py: 2 }}>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <TrendingUp color="primary" />
              <Typography variant="h6">Content Strategy</Typography>
            </Box>
            <Typography gutterBottom color="textSecondary">
              Select your primary niche to help our AI better understand your audience.
            </Typography>
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>Primary Niche</InputLabel>
              <Select
                value={contentType}
                label="Primary Niche"
                onChange={(e) => setContentType(e.target.value)}
              >
                <MenuItem value="educational">Educational / Tutorials</MenuItem>
                <MenuItem value="entertainment">Entertainment / Vlogs</MenuItem>
                <MenuItem value="tech">Technology / Reviews</MenuItem>
                <MenuItem value="lifestyle">Lifestyle / Business</MenuItem>
              </Select>
            </FormControl>
          </Box>
        );
      case 3:
        return (
          <Box sx={{ py: 2, textAlign: 'center' }}>
            <CheckCircle sx={{ fontSize: 60, color: '#4caf50', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              System Ready!
            </Typography>
            <Typography color="textSecondary" sx={{ mb: 3 }}>
              Your "First Class Asset" is configured and historical data is being synchronized in the background.
            </Typography>
            <Alert severity="success">
              You're all set! Check the Analytics tab in a few moments to see your data.
            </Alert>
          </Box>
        );
      default:
        return null;
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 2 }}>
      <Typography variant="h4" gutterBottom align="center">
        System Onboarding
      </Typography>
      <Typography variant="subtitle1" gutterBottom align="center" color="textSecondary" sx={{ mb: 4 }}>
        Powering your production-ready content workflow
      </Typography>

      <Card elevation={3}>
        <CardContent sx={{ p: 4 }}>
          <Stepper activeStep={activeStep} sx={{ mb: 6 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          <Box sx={{ minHeight: 250 }}>
            {renderStepContent(activeStep)}
          </Box>

          <Box sx={{ display: 'flex', flexDirection: 'row', pt: 4, borderTop: '1px solid #eee', mt: 2 }}>
            <Button
              color="inherit"
              disabled={activeStep === 0 || activeStep === steps.length - 1}
              onClick={handleBack}
              sx={{ mr: 1 }}
            >
              Back
            </Button>
            <Box sx={{ flex: '1 1 auto' }} />
            {activeStep === steps.length - 1 ? (
              <Button variant="contained" color="success" size="large">
                Go to Dashboard
              </Button>
            ) : (
              activeStep > 0 && activeStep < 3 && (
                <Button
                  onClick={handleNext}
                  variant="contained"
                  disabled={isInitializing || (activeStep === 2 && !contentType)}
                >
                  Next
                </Button>
              )
            )}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};