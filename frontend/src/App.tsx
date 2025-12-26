import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  AppBar,
  Toolbar,
  Button,
  CssBaseline,
  ThemeProvider,
  createTheme
} from '@mui/material';
import PricingPage from './components/PricingPage';
import RevenueDashboard from './components/RevenueDashboard';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import { OAuthCallback } from './components/Auth/OAuthCallback';
import { useState } from 'react';
import { Tabs, Tab, Paper } from '@mui/material';
import { InitializationTab } from './components/Dashboard/InitializationTab';
import { AnalyticsTab } from './components/Dashboard/AnalyticsTab';
import { PerformanceTab } from './components/Dashboard/PerformanceTab';
import { HealthTab } from './components/Dashboard/HealthTab';
import { EarningsTab } from './components/Dashboard/EarningsTab';
import { ManagementTab } from './components/Dashboard/ManagementTab';
import { ModelsTab } from './components/Dashboard/ModelsTab';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const isLoggedIn = !!localStorage.getItem('auth_token');

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              YouTube AI Platform
            </Typography>
            {isLoggedIn ? (
              <>
                <Button color="inherit" component={Link} to="/">Dashboard</Button>
                <Button color="inherit" component={Link} to="/pricing">Pricing</Button>
                <Button color="inherit" component={Link} to="/revenue">Revenue</Button>
                <Button color="inherit" onClick={handleLogout}>Logout</Button>
              </>
            ) : (
              <>
                <Button color="inherit" component={Link} to="/login">Login</Button>
                <Button color="inherit" component={Link} to="/register">Register</Button>
              </>
            )}
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ py: 4 }}>
          <Routes>
            <Route path="/" element={<DashboardView />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/pricing" element={<PricingPage />} />
            <Route path="/revenue" element={<RevenueDashboard />} />
            <Route path="/oauth/callback" element={<OAuthCallback />} />
          </Routes>
        </Container>
      </Router>
    </ThemeProvider>
  );
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function DashboardView() {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const tabs = [
    'Initialization',
    'Analytics',
    'Performance',
    'Health',
    'Earnings',
    'Management',
    'Models'
  ];

  return (
    <>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        YouTube AI Dashboard
      </Typography>
      <Typography variant="subtitle1" align="center" color="textSecondary" gutterBottom>
        Profit-Centric Content Creation Platform
      </Typography>

      <Paper sx={{ mt: 4 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            aria-label="dashboard tabs"
            variant="scrollable"
            scrollButtons="auto"
          >
            {tabs.map((tab, index) => (
              <Tab key={index} label={tab} id={`dashboard-tab-${index}`} />
            ))}
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <InitializationTab />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <AnalyticsTab />
        </TabPanel>
        <TabPanel value={tabValue} index={2}>
          <PerformanceTab />
        </TabPanel>
        <TabPanel value={tabValue} index={3}>
          <HealthTab />
        </TabPanel>
        <TabPanel value={tabValue} index={4}>
          <EarningsTab />
        </TabPanel>
        <TabPanel value={tabValue} index={5}>
          <ManagementTab />
        </TabPanel>
        <TabPanel value={tabValue} index={6}>
          <ModelsTab />
        </TabPanel>
      </Paper>
    </>
  );
}

export default App;
