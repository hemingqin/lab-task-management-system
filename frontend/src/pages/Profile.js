import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  TextField,
  Button,
  Alert,
  Grid,
  Divider,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

function Profile() {
  const { user, setUser } = useAuth();
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await axios.put('http://localhost:5000/api/auth/profile', {
        username: formData.username,
        email: formData.email,
      });
      setUser(response.data);
      setSuccess('Profile updated successfully');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (formData.newPassword !== formData.confirmPassword) {
      return setError('New passwords do not match');
    }

    setLoading(true);

    try {
      await axios.put('http://localhost:5000/api/auth/change-password', {
        current_password: formData.currentPassword,
        new_password: formData.newPassword,
      });
      setSuccess('Password changed successfully');
      setFormData({
        ...formData,
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Profile Settings
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Account Information
            </Typography>
            <Box component="form" onSubmit={handleUpdateProfile}>
              <TextField
                fullWidth
                label="Username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                margin="normal"
                required
              />
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                margin="normal"
                required
              />
              <Button
                type="submit"
                variant="contained"
                sx={{ mt: 2 }}
                disabled={loading}
              >
                {loading ? 'Updating...' : 'Update Profile'}
              </Button>
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
          </Grid>

          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Change Password
            </Typography>
            <Box component="form" onSubmit={handleChangePassword}>
              <TextField
                fullWidth
                label="Current Password"
                name="currentPassword"
                type="password"
                value={formData.currentPassword}
                onChange={handleChange}
                margin="normal"
                required
              />
              <TextField
                fullWidth
                label="New Password"
                name="newPassword"
                type="password"
                value={formData.newPassword}
                onChange={handleChange}
                margin="normal"
                required
              />
              <TextField
                fullWidth
                label="Confirm New Password"
                name="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange}
                margin="normal"
                required
              />
              <Button
                type="submit"
                variant="contained"
                color="primary"
                sx={{ mt: 2 }}
                disabled={loading}
              >
                {loading ? 'Changing Password...' : 'Change Password'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
}

export default Profile; 