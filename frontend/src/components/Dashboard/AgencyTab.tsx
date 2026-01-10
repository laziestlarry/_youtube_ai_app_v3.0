import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    Button,
    TextField,
    MenuItem,
    Select,
    FormControl,
    InputLabel,
    CircularProgress,
    Alert,
    Paper,
    Divider,
    Fade,
    LinearProgress
} from '@mui/material';
import { apiService } from '../../services/api';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';

export const AgencyTab: React.FC = () => {
    const [departments, setDepartments] = useState<Array<{ name: string; description: string }>>([]);
    const [selectedDept, setSelectedDept] = useState('');
    const [objective, setObjective] = useState('');
    const [loading, setLoading] = useState(false);
    const [executing, setExecuting] = useState(false);
    const [result, setResult] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchDepts = async () => {
            try {
                setLoading(true);
                const data = await apiService.getAgencyDepartments();
                setDepartments(data);
                if (data.length > 0) setSelectedDept(data[0].name);
            } catch (err) {
                setError('Failed to load Agency departments.');
            } finally {
                setLoading(false);
            }
        };
        fetchDepts();
    }, []);

    const handleExecute = async () => {
        if (!objective || !selectedDept) return;
        try {
            setExecuting(true);
            setResult(null);
            setError(null);
            const data = await apiService.executeAgencyTask(objective, selectedDept);
            setResult(data.result);
        } catch (err) {
            setError('Task execution failed.');
        } finally {
            setExecuting(false);
        }
    };

    if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>;

    return (
        <Box>
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                AI Agency Orchestrator
            </Typography>
            <Typography variant="subtitle1" color="textSecondary" sx={{ mb: 4 }}>
                Cognysis the Chimera: High-performance departmental automation infused with your Altered Self perfil.
            </Typography>

            <Grid container spacing={4}>
                {/* Input Section */}
                <Grid size={{ xs: 12, md: 5 }}>
                    <Card sx={{
                        borderRadius: 4,
                        backdropFilter: 'blur(10px)',
                        backgroundColor: 'rgba(255, 255, 255, 0.8)',
                        border: '1px solid rgba(255, 255, 255, 0.3)',
                        boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.1)'
                    }}>
                        <CardContent>
                            <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                                <RocketLaunchIcon color="primary" /> Mission Objective
                            </Typography>

                            <FormControl fullWidth sx={{ mt: 2, mb: 3 }}>
                                <InputLabel>Department</InputLabel>
                                <Select
                                    value={selectedDept}
                                    label="Department"
                                    onChange={(e) => setSelectedDept(e.target.value)}
                                >
                                    {departments.map((dept) => (
                                        <MenuItem key={dept.name} value={dept.name}>
                                            {dept.name.charAt(0).toUpperCase() + dept.name.slice(1)}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>

                            <TextField
                                fullWidth
                                multiline
                                rows={4}
                                label="What should the agency accomplish?"
                                variant="outlined"
                                placeholder="e.g., Create a 30-day viral content strategy for AI tutorials..."
                                value={objective}
                                onChange={(e) => setObjective(e.target.value)}
                                sx={{ mb: 3 }}
                            />

                            <Button
                                fullWidth
                                variant="contained"
                                size="large"
                                startIcon={executing ? <CircularProgress size={20} color="inherit" /> : <SmartToyIcon />}
                                onClick={handleExecute}
                                disabled={executing || !objective}
                                sx={{
                                    borderRadius: 2,
                                    py: 1.5,
                                    textTransform: 'none',
                                    fontSize: '1.1rem',
                                    fontWeight: 600
                                }}
                            >
                                {executing ? 'Engine Warming Up...' : 'Ignite Workflow'}
                            </Button>
                        </CardContent>
                    </Card>

                    <Box sx={{ mt: 3 }}>
                        <Alert severity="info" variant="outlined" sx={{ borderRadius: 2 }}>
                            The <strong>Chimera Engine</strong> will automatically select the most efficient model for this task.
                        </Alert>
                    </Box>
                </Grid>

                {/* Result Section */}
                <Grid size={{ xs: 12, md: 7 }}>
                    <Paper sx={{
                        p: 3,
                        minHeight: 400,
                        borderRadius: 4,
                        bgcolor: '#f8fbfc',
                        border: '1px dashed #ced4da',
                        display: 'flex',
                        flexDirection: 'column'
                    }}>
                        <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                            <AutorenewIcon color="secondary" sx={{ animation: executing ? 'spin 2s linear infinite' : 'none' }} />
                            Execution Analysis
                            {executing && <Typography variant="caption" sx={{ ml: 'auto' }}>Pulsing Chimera Neurons...</Typography>}
                        </Typography>
                        <Divider sx={{ mb: 2 }} />

                        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

                        {executing && (
                            <Box sx={{ width: '100%', mt: 4 }}>
                                <LinearProgress sx={{ borderRadius: 1, height: 8 }} />
                                <Typography variant="body2" color="textSecondary" align="center" sx={{ mt: 2 }}>
                                    Analyzing data points, infusing Altered Self context, and rendering tactical plan...
                                </Typography>
                            </Box>
                        )}

                        {!executing && result && (
                            <Fade in={true}>
                                <Box sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.95rem' }}>
                                    {result}
                                </Box>
                            </Fade>
                        )}

                        {!executing && !result && !error && (
                            <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.5 }}>
                                <Typography>Select a department and define your objective to generate an AI execution plan.</Typography>
                            </Box>
                        )}
                    </Paper>
                </Grid>
            </Grid>

            <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
        </Box>
    );
};
