import React from 'react';
import { Typography, Box } from '@mui/material';

const SettingsPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        System Settings
      </Typography>
      <Typography>
        System configuration interface will be implemented here.
      </Typography>
    </Box>
  );
};

export default SettingsPage;
