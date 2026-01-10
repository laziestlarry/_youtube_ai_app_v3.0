import React, { useState } from 'react';
import {
    Box,
    Card,
    CardContent,
    TextField,
    Button,
    Typography,
    Alert,
    Container,
    Tabs,
    Tab,
    Divider
} from '@mui/material';
import { useNavigate, Link } from 'react-router-dom';
import { apiService } from '../../services/api';

const Login: React.FC = () => {
    const [tabValue, setTabValue] = useState(0);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [accessKey, setAccessKey] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
        setTabValue(newValue);
        setError(null);
    };

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            const data = await apiService.login(username.trim(), password.trim());
            localStorage.setItem('auth_token', data.access_token);
            navigate('/');
            window.location.reload(); // Refresh to update app state
        } catch (err: any) {
            console.error('Login failed:', err);
            setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    const handleKeyLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            const data = await apiService.loginWithKey(accessKey.trim());
            localStorage.setItem('auth_token', data.access_token);
            navigate('/');
            window.location.reload();
        } catch (err: any) {
            console.error('Key validation failed:', err);
            setError(err.response?.data?.detail || 'Invalid Access Key. Please check your purchase email.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="sm">
            <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Card elevation={3} sx={{ width: '100%', border: tabValue === 1 ? '2px solid #009688' : 'none' }}>
                    <CardContent sx={{ p: 4 }}>
                        <Typography variant="h4" component="h1" gutterBottom align="center">
                            Autonomax Access
                        </Typography>

                        <Tabs
                            value={tabValue}
                            onChange={handleTabChange}
                            centered
                            sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}
                        >
                            <Tab label="Standard Login" />
                            <Tab label="License Key" />
                        </Tabs>

                        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

                        {tabValue === 0 ? (
                            <Box component="form" onSubmit={handleLogin}>
                                <TextField
                                    margin="normal"
                                    required
                                    fullWidth
                                    label="Username or Email"
                                    autoComplete="username"
                                    autoFocus
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                                <TextField
                                    margin="normal"
                                    required
                                    fullWidth
                                    label="Password"
                                    type="password"
                                    autoComplete="current-password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                                <Button
                                    type="submit"
                                    fullWidth
                                    variant="contained"
                                    size="large"
                                    sx={{ mt: 3, mb: 2 }}
                                    disabled={loading}
                                >
                                    {loading ? 'Logging in...' : 'Login'}
                                </Button>
                                <Box textAlign="center" sx={{ mt: 2 }}>
                                    <Typography variant="body2">
                                        Don't have an account? <Button component={Link} to="/register" sx={{ textTransform: 'none' }}>Create one here</Button>
                                    </Typography>
                                    <Divider sx={{ my: 2 }}>OR</Divider>
                                    <Button
                                        color="secondary"
                                        fullWidth
                                        onClick={() => setTabValue(1)}
                                        sx={{ textTransform: 'none' }}
                                    >
                                        Use Shopier Access Key
                                    </Button>
                                </Box>
                            </Box>
                        ) : (
                            <Box component="form" onSubmit={handleKeyLogin}>
                                <Typography variant="body2" color="textSecondary" align="center" sx={{ mb: 3 }}>
                                    Enter the License Key sent to your purchase email from Shopier.
                                </Typography>
                                <TextField
                                    margin="normal"
                                    required
                                    fullWidth
                                    label="License Key"
                                    placeholder="e.g. AUTONOMAX_..."
                                    autoFocus
                                    value={accessKey}
                                    onChange={(e) => setAccessKey(e.target.value)}
                                />
                                <Button
                                    type="submit"
                                    fullWidth
                                    variant="contained"
                                    color="secondary"
                                    size="large"
                                    sx={{ mt: 3, mb: 2, bgcolor: '#009688', '&:hover': { bgcolor: '#00796b' } }}
                                    disabled={loading}
                                >
                                    {loading ? 'Verifying...' : 'Unlock Access'}
                                </Button>
                                <Box textAlign="center" sx={{ mt: 2 }}>
                                    <Typography variant="body2">
                                        Don't have a key? <a href="YOUR_SHOPIER_LINK" target="_blank" rel="noopener noreferrer" style={{ color: '#009688', textDecoration: 'underline' }}>Buy Access Here</a>
                                    </Typography>
                                    <Button
                                        fullWidth
                                        onClick={() => setTabValue(0)}
                                        sx={{ mt: 2, textTransform: 'none' }}
                                    >
                                        Back to Password Login
                                    </Button>
                                </Box>
                            </Box>
                        )}
                    </CardContent>
                </Card>
            </Box>
        </Container>
    );
};

export default Login;
