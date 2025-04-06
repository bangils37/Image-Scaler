from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import numpy as np
from PIL import Image
import io
import os
import time
import cv2
from typing import Dict
from interpolation import upscale_lagrange, upscale_newton, upscale_spline, calculate_psnr

# Constants
MAX_IMAGE_SIZE = 1024
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(
    title="Image Upscaling API",
    description="API for upscaling grayscale images using different interpolation methods",
    version="1.0.0"
)

app.mount("/output", StaticFiles(directory="output"), name="output")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Chỉ cho phép Frontend từ React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upscale", response_model=Dict[str, str])
async def upscale_image(
    file: UploadFile = File(...),
    scale_factor: float = Form(2.0),
    method: str = Form("lagrange")
):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        if max(image.size) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Image dimensions exceed maximum allowed size of {MAX_IMAGE_SIZE}px"
            )

        img_array = np.array(image)

        # Resize original image for PSNR calculation
        original_resized = cv2.resize(img_array, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_NEAREST)

        start_time = time.time()
        if method.lower() == "lagrange":
            result = upscale_lagrange(img_array, scale_factor)
        elif method.lower() == "newton":
            result = upscale_newton(img_array, scale_factor)
        elif method.lower() == "spline":
            result = upscale_spline(img_array, scale_factor)
        elif method.lower() == "bilinear":
            result = cv2.resize(img_array, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
        elif method.lower() == "bicubic":
            result = cv2.resize(img_array, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
        else:
            raise HTTPException(status_code=400, detail="Invalid method. Choose 'lagrange', 'newton', 'spline', 'bilinear', or 'bicubic'.")

        processing_time = time.time() - start_time
        psnr = calculate_psnr(original_resized, result)

        output_path = os.path.join(OUTPUT_DIR, "upscaled_image.png")
        Image.fromarray(result).save(output_path)

        response_data = {
            "output_image": output_path,
            "scale_factor": scale_factor,
            "method": method,
            "metrics": {
                "psnr": f"{psnr:.2f} dB",
                "processing_time": f"{processing_time:.3f} seconds"
            }
        }

        return {
            "message": "Image processed successfully",
            "result": json.dumps(response_data),
            "image_path": "/output/upscaled_image.png"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)