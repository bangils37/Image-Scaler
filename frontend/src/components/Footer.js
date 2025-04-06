import React from 'react';
import { Typography, Box } from '@mui/material';

const Footer = () => {
  return (
    <Box sx={{ p: 2, textAlign: 'center', backgroundColor: '#f5f5f5' }}>
      <Typography variant="body2">
        © 2025 ImageScaler. All rights reserved.
      </Typography>
    </Box>
  );
};

export default Footer;