import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress, Typography, Alert, Paper } from '@mui/material';
import { apiService } from '../../services/api';

export const OAuthCallback: React.FC = () => {
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [error, setError] = useState<string | null>(null);
    const location = useLocation();
    const navigate = useNavigate();

    useEffect(() => {
        const handleCallback = async () => {
            const query = new URLSearchParams(location.search);
            const code = query.get('code');

            if (!code) {
                setStatus('error');
                setError('No authorization code found in URL');
                return;
            }

            try {
                await apiService.connectYouTube(code);
                setStatus('success');
                // Wait a bit then redirect back to dashboard
                setTimeout(() => {
                    navigate('/');
                }, 2000);
            } catch (err: any) {
                console.error('OAuth Error:', err);
                setStatus('error');
                setError(err.response?.data?.detail || 'Failed to connect YouTube account');
            }
        };

        handleCallback();
    }, [location, navigate]);

    return (
        <Box
            sx={{
                height: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: '#f5f5f5'
            }}
        >
            <Paper elevation={3} sx={{ p: 4, maxWidth: 400, width: '100%', textAlign: 'center' }}>
                {status === 'loading' && (
                    <>
                        <CircularProgress sx={{ mb: 2 }} />
                        <Typography variant="h6">Connecting to YouTube...</Typography>
                        <Typography color="textSecondary" variant="body2">
                            Exchanging authorization code for access tokens
                        </Typography>
                    </>
                )}

                {status === 'success' && (
                    <>
                        <Typography variant="h5" color="success.main" gutterBottom>
                            Connection Successful!
                        </Typography>
                        <Typography>
                            Your YouTube account has been linked. Redirecting to dashboard...
                        </Typography>
                    </>
                )}

                {status === 'error' && (
                    <>
                        <Typography variant="h5" color="error" gutterBottom>
                            Connection Failed
                        </Typography>
                        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
                        <Typography
                            variant="body2"
                            sx={{ cursor: 'pointer', color: 'primary.main', textDecoration: 'underline' }}
                            onClick={() => navigate('/')}
                        >
                            Return to Dashboard
                        </Typography>
                    </>
                )}
            </Paper>
        </Box>
    );
};
