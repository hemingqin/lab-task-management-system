import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress,
} from '@mui/material';
import { format } from 'date-fns';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { isAuthenticated, user } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      if (!isAuthenticated) {
        console.log('Not authenticated, skipping data fetch');
        setLoading(false);
        return;
      }

      const token = localStorage.getItem('token');
      console.log('Fetching data with token:', token);
      console.log('Current user:', user);

      // Create axios instance with auth headers
      const api = axios.create({
        baseURL: 'http://127.0.0.1:5000',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      try {
        console.log('Making API requests...');
        const [tasksResponse, projectsResponse] = await Promise.all([
          api.get('/api/tasks'),
          api.get('/api/projects')
        ]);

        console.log('Tasks response:', tasksResponse.data);
        console.log('Projects response:', projectsResponse.data);

        setTasks(tasksResponse.data || []);
        setProjects(projectsResponse.data || []);
        setError('');
      } catch (err) {
        console.error('Error fetching dashboard data:', {
          message: err.message,
          response: err.response?.data,
          status: err.response?.status,
          headers: err.response?.headers
        });
        setError('Failed to fetch dashboard data');
        setTasks([]);
        setProjects([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [isAuthenticated, user]);

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'warning';
      case 'todo':
        return 'default';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  const recentTasks = tasks.slice(0, 5);
  const recentProjects = projects.slice(0, 5);

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Recent Tasks
          </Typography>
          <List>
            {recentTasks.map((task) => (
              <ListItem key={task.id}>
                <ListItemText
                  primary={task.title}
                  secondary={
                    <Box component="span">
                      <Typography variant="body2" component="span">
                        Due: {task.due_date ? format(new Date(task.due_date), 'MMM d, yyyy') : 'No due date'}
                      </Typography>
                      <Box component="span" sx={{ ml: 1 }}>
                        <Chip
                          label={task.priority}
                          size="small"
                          color={getPriorityColor(task.priority)}
                          sx={{ mr: 1 }}
                        />
                        <Chip
                          label={task.status}
                          size="small"
                          color={getStatusColor(task.status)}
                        />
                      </Box>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      </Grid>
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Recent Projects
          </Typography>
          <List>
            {recentProjects.map((project) => (
              <ListItem key={project.id}>
                <ListItemText
                  primary={project.name}
                  secondary={
                    <Box component="span">
                      <Typography variant="body2" component="span">
                        {project.task_count} tasks
                      </Typography>
                      {project.deadline && (
                        <Typography variant="body2" component="span" sx={{ ml: 1 }}>
                          • Due: {format(new Date(project.deadline), 'MMM d, yyyy')}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      </Grid>
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Statistics
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <Typography variant="subtitle1">Total Tasks</Typography>
              <Typography variant="h4">{tasks.length}</Typography>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Typography variant="subtitle1">Total Projects</Typography>
              <Typography variant="h4">{projects.length}</Typography>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Typography variant="subtitle1">Completed Tasks</Typography>
              <Typography variant="h4">
                {tasks.filter((task) => task.status === 'completed').length}
              </Typography>
            </Grid>
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  );
}

export default Dashboard; 