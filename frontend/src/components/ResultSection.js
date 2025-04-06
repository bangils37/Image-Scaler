import React from 'react';
import { Button, Box, Typography } from '@mui/material';

const ResultSection = ({ originalImage, upscaledImage, psnr }) => {
  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = upscaledImage;
    link.download = 'upscaled_image.png';
    link.click();
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-around' }}>
        {originalImage && (
          <div>
            <Typography>Original Image</Typography>
            <img src={originalImage} alt="Original" style={{ maxWidth: '300px' }} />
          </div>
        )}
        {upscaledImage && (
          <div>
            <Typography>Upscaled Image</Typography>
            <img src={upscaledImage} alt="Upscaled" style={{ maxWidth: '300px' }} />
          </div>
        )}
      </Box>
      {psnr && <Typography sx={{ mt: 2 }}>PSNR: {psnr} dB</Typography>}
      {upscaledImage && (
        <Button variant="outlined" onClick={handleDownload} sx={{ mt: 2 }}>
          Download Image
        </Button>
      )}
    </Box>
  );
};

export default ResultSection;