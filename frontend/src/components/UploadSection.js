import React, { useState } from 'react';
import { Button, TextField, MenuItem, Select, Box, CircularProgress } from '@mui/material';
import axios from 'axios';

const UploadSection = ({ setOriginalImage, setUpscaledImage, setPsnr, setSnackbarMessage }) => {
  const [file, setFile] = useState(null);
  const [scaleFactor, setScaleFactor] = useState(2.0);
  const [method, setMethod] = useState('lagrange');
  const [isLoading, setIsLoading] = useState(false); // Trạng thái đợi

  const API_URL = "https://5f9f-35-247-64-96.ngrok-free.app";

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setOriginalImage(URL.createObjectURL(selectedFile)); // Hiển thị ảnh gốc
      setUpscaledImage(null); // Reset ảnh phóng to
      setPsnr(null); // Reset PSNR
      setSnackbarMessage('Ảnh đã được tải lên thành công!'); // Thông báo upload
    }
  };

  const handleScaleImage = async () => {
    if (!file) {
      setSnackbarMessage('Vui lòng chọn ảnh trước khi phóng to!');
      return;
    }

    setUpscaledImage(null); // Reset ảnh phóng to
    setPsnr(null); // Reset PSNR

    const formData = new FormData();
    formData.append("file", file);
    formData.append("scale_factor", scaleFactor); // Gửi scaleFactor
    formData.append("method", method); // Gửi method

    setIsLoading(true); // Hiển thị biểu tượng đợi
    try {
      const response = await axios.post(`${API_URL}/upscale`, formData);

      // Lấy đường dẫn ảnh và dữ liệu từ response
      const { image_path, result } = response.data;

      // Hiển thị ảnh đã upscale
      // Do trình duyệt cache lại ảnh upscaled_image, nên khi bạn gửi request mới nhưng URL giống hệt (ví dụ: /static/uploads/result.jpg), thì trình duyệt nghĩ: "Ờ cái này mình đã tải rồi mà, khỏi tải lại"
      setUpscaledImage(`${API_URL}${image_path}?t=${new Date().getTime()}`);

      // Parse result và lấy PSNR dựa trên method
      const parsedResult = JSON.parse(result);
      const psnrValue = parsedResult.metrics?.psnr || 'N/A';
      setPsnr(psnrValue);

      setSnackbarMessage('Ảnh đã được phóng to thành công!'); // Thông báo thành công
    } catch (error) {
      console.error("Error scaling image:", error);
      setSnackbarMessage('Có lỗi xảy ra khi phóng to ảnh!'); // Thông báo lỗi
    } finally {
      setIsLoading(false); // Tắt biểu tượng đợi
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <TextField
        label="Scale Factor"
        type="number"
        value={scaleFactor}
        onChange={(e) => setScaleFactor(e.target.value)}
        sx={{ mt: 2, mr: 2 }}
      />
      <Select
        value={method}
        onChange={(e) => setMethod(e.target.value)}
        sx={{ mt: 2, mr: 2 }}
      >
        <MenuItem value="lagrange">Lagrange Interpolation</MenuItem>
        <MenuItem value="newton">Newton Interpolation</MenuItem>
        <MenuItem value="spline">Spline Interpolation</MenuItem>
        <MenuItem value="bilinear">Bilinear Interpolation</MenuItem>
        <MenuItem value="bicubic">Bicubic Interpolation</MenuItem>
      </Select>
      <Box sx={{ position: 'relative', display: 'inline-block', mt: 2 }}>
        <Button
          variant="contained"
          onClick={handleScaleImage}
          disabled={isLoading} // Vô hiệu hóa nút khi đang xử lý
        >
          Scale Image
        </Button>
        {isLoading && (
          <CircularProgress
            size={24}
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              marginTop: '-12px',
              marginLeft: '-12px',
            }}
          />
        )}
      </Box>
    </Box>
  );
};

export default UploadSection;