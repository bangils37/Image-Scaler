import React, { useState } from 'react';
import Header from './components/Header';
import UploadSection from './components/UploadSection';
import ResultSection from './components/ResultSection';
import Footer from './components/Footer';
import Snackbar from '@mui/material/Snackbar';
import './App.css';

function App() {
  const [originalImage, setOriginalImage] = useState(null);
  const [upscaledImage, setUpscaledImage] = useState(null);
  const [psnr, setPsnr] = useState(null);
  const [snackbarMessage, setSnackbarMessage] = useState(null); // Thêm state cho thông báo

  const handleCloseSnackbar = () => {
    setSnackbarMessage(null); // Đóng thông báo
  };

  return (
    <div className="App">
      <Header />
      <main>
        <UploadSection 
          setOriginalImage={setOriginalImage} 
          setUpscaledImage={setUpscaledImage}
          setPsnr={setPsnr}
          setSnackbarMessage={setSnackbarMessage} // Truyền hàm để hiển thị thông báo
        />
        <ResultSection 
          originalImage={originalImage} 
          upscaledImage={upscaledImage} 
          psnr={psnr} 
        />
      </main>
      <Footer />
      {/* Thêm Snackbar để hiển thị thông báo */}
      {snackbarMessage && (
        <Snackbar
          open={!!snackbarMessage}
          autoHideDuration={3000} // Tự đóng sau 3 giây
          onClose={handleCloseSnackbar}
          message={snackbarMessage}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        />
      )}
    </div>
  );
}

export default App;