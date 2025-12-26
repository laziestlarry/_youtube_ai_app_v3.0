import React from 'react';
import { Box, Tabs, Tab, Typography, Paper, Container, Card, CardContent } from '@mui/material';

const tabLabels = [
  'Initialization',
  'Analytics',
  'Performance',
  'Health',
  'Earnings',
  'Management',
  'Models',
];

function TabPanel(props: { children?: React.ReactNode; index: number; value: number }) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function Dashboard() {
  const [currentTab, setCurrentTab] = React.useState(0);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          YouTube AI Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Modern dashboard foundation (Vite + React + MUI)
        </Typography>
      </Box>
      <Paper sx={{ width: '100%', mt: 3 }}>
        <Tabs
          value={currentTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          {tabLabels.map((label, index) => (
            <Tab key={index} label={label} />
          ))}
        </Tabs>
        {tabLabels.map((label, index) => (
          <TabPanel value={currentTab} index={index} key={index}>
            <Card>
              <CardContent>
                <Typography variant="h5" component="h2" gutterBottom>
                  {label}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {label} content goes here.
                </Typography>
              </CardContent>
            </Card>
          </TabPanel>
        ))}
      </Paper>
    </Container>
  );
} 