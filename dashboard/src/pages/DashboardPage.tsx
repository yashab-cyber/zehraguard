import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Chip,
  LinearProgress,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  Security as SecurityIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
);

interface DashboardStats {
  totalUsers: number;
  activeAlerts: number;
  resolvedThreats: number;
  riskScore: number;
}

interface RecentAlert {
  id: string;
  user: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
}

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalUsers: 0,
    activeAlerts: 0,
    resolvedThreats: 0,
    riskScore: 0
  });
  const [recentAlerts, setRecentAlerts] = useState<RecentAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Simulate API calls - replace with actual API endpoints
      const statsResponse = await fetch('/api/dashboard/stats');
      const alertsResponse = await fetch('/api/alerts/recent');
      
      // Mock data for demonstration
      setStats({
        totalUsers: 1247,
        activeAlerts: 23,
        resolvedThreats: 156,
        riskScore: 67
      });

      setRecentAlerts([
        {
          id: '1',
          user: 'john.doe',
          type: 'Data Exfiltration',
          severity: 'high',
          timestamp: '2024-01-15 14:30:22'
        },
        {
          id: '2',
          user: 'jane.smith',
          type: 'Anomalous Behavior',
          severity: 'medium',
          timestamp: '2024-01-15 13:45:11'
        },
        {
          id: '3',
          user: 'mike.wilson',
          type: 'Policy Violation',
          severity: 'low',
          timestamp: '2024-01-15 12:15:05'
        }
      ]);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const threatTrendData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Threats Detected',
        data: [12, 19, 15, 25, 22, 18],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        tension: 0.1
      },
      {
        label: 'Threats Resolved',
        data: [8, 15, 12, 20, 18, 16],
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        tension: 0.1
      }
    ]
  };

  const threatTypeData = {
    labels: ['Data Exfiltration', 'Policy Violation', 'Anomalous Behavior', 'Privilege Escalation'],
    datasets: [
      {
        data: [35, 25, 25, 15],
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 205, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)'
        ]
      }
    ]
  };

  const userActivityData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Active Users',
        data: [850, 920, 880, 950, 870, 320, 280],
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
      }
    ]
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Security Dashboard
        </Typography>
        <IconButton onClick={fetchDashboardData} disabled={loading}>
          <RefreshIcon />
        </IconButton>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Users
                  </Typography>
                  <Typography variant="h4">
                    {stats.totalUsers.toLocaleString()}
                  </Typography>
                </Box>
                <PeopleIcon sx={{ fontSize: 40, color: 'primary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Alerts
                  </Typography>
                  <Typography variant="h4" color="error">
                    {stats.activeAlerts}
                  </Typography>
                </Box>
                <WarningIcon sx={{ fontSize: 40, color: 'error.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Resolved Threats
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {stats.resolvedThreats}
                  </Typography>
                </Box>
                <SecurityIcon sx={{ fontSize: 40, color: 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Risk Score
                  </Typography>
                  <Typography variant="h4">
                    {stats.riskScore}%
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={stats.riskScore} 
                    sx={{ mt: 1 }}
                    color={stats.riskScore > 70 ? 'error' : stats.riskScore > 40 ? 'warning' : 'success'}
                  />
                </Box>
                <TrendingUpIcon sx={{ fontSize: 40, color: 'warning.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Threat Detection Trends
            </Typography>
            <Box sx={{ height: 300 }}>
              <Line data={threatTrendData} options={{ responsive: true, maintainAspectRatio: false }} />
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Threat Types Distribution
            </Typography>
            <Box sx={{ height: 300 }}>
              <Doughnut data={threatTypeData} options={{ responsive: true, maintainAspectRatio: false }} />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Bottom Row */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              User Activity This Week
            </Typography>
            <Box sx={{ height: 300 }}>
              <Bar data={userActivityData} options={{ responsive: true, maintainAspectRatio: false }} />
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Alerts
            </Typography>
            <List dense>
              {recentAlerts.map((alert) => (
                <ListItem key={alert.id} divider>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" component="span">
                          {alert.user}
                        </Typography>
                        <Chip 
                          label={alert.severity} 
                          size="small" 
                          color={getSeverityColor(alert.severity) as any}
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {alert.type}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {alert.timestamp}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
