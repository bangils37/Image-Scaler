import numpy as np
from PIL import Image
from scipy import interpolate
import cv2

# Constants
MAX_IMAGE_SIZE = 1024

def lagrange_interpolation(x: float, x_points: np.ndarray, y_points: np.ndarray) -> float:
    n = len(x_points)
    result = 0.0

    if len(np.unique(x_points)) != len(x_points):
        raise ValueError(f"Duplicate x_points={x_points}, src_x={x}")

    for i in range(n):
        term = y_points[i]
        for j in range(n):
            if j != i:
                term = term * (x - x_points[j]) / (x_points[i] - x_points[j])
        result += term
    return result

def upscale_lagrange(image: np.ndarray, scale: float = 2.0) -> np.ndarray:
    if len(image.shape) != 3 or image.shape[2] != 3:
        raise ValueError("Input image must be RGB with shape (h, w, 3)")

    h, w, c = image.shape
    new_h, new_w = int(h * scale), int(w * scale)
    result = np.zeros((new_h, new_w, 3), dtype=np.float64)

    x = np.arange(w)
    y = np.arange(h)

    x_points = np.zeros(4, dtype=np.int64)
    y_points = np.zeros(4, dtype=np.int64)

    for i in range(new_h):
        for j in range(new_w):
            src_x = j / scale
            src_y = i / scale

            tmp = int(src_x)
            for k in range(max(2, 4 - (w - 1 - tmp))):
                if tmp - 1 >= 0:
                    tmp -= 1
            for k in range(4):
                x_points[k] = min(tmp, w - 1)
                if tmp < w - 1:
                    tmp += 1

            tmp = int(src_y)
            for k in range(max(2, 4 - (h - 1 - tmp))):
                if tmp - 1 >= 0:
                    tmp -= 1
            for k in range(4):
                y_points[k] = min(tmp, h - 1)
                if tmp < h - 1:
                    tmp += 1

            for channel in range(3):
                x_values = image[int(src_y), x_points, channel]
                result[i, j, channel] = lagrange_interpolation(src_x, x_points, x_values)

    return np.clip(result, 0, 255).astype(np.uint8)

def newton_interpolation(x, x_points, y_points):
    n = len(x_points)
    coef = np.copy(y_points).astype(np.float64)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) / (x_points[i] - x_points[i - j])
    
    result = coef[-1]
    for i in range(n - 2, -1, -1):
        result = result * (x - x_points[i]) + coef[i]
    return result

def upscale_newton(image: np.ndarray, scale: float = 2) -> np.ndarray:
    if len(image.shape) != 3 or image.shape[2] != 3:
        raise ValueError("Input image must be RGB with shape (h, w, 3)")

    h, w, c = image.shape
    new_h, new_w = int(h * scale), int(w * scale)
    result = np.zeros((new_h, new_w, 3), dtype=np.float64)

    x = np.arange(w)
    y = np.arange(h)
    x_points = np.zeros(4, dtype=np.int64)
    y_points = np.zeros(4, dtype=np.int64)

    for i in range(new_h):
        for j in range(new_w):
            src_x = j / scale
            src_y = i / scale

            tmp = int(src_x)
            for k in range(max(2, 4 - (w - 1 - tmp))):
                if tmp - 1 >= 0:
                    tmp -= 1
            for k in range(4):
                x_points[k] = min(tmp, w - 1)
                if tmp < w - 1:
                    tmp += 1

            tmp = int(src_y)
            for k in range(max(2, 4 - (h - 1 - tmp))):
                if tmp - 1 >= 0:
                    tmp -= 1
            for k in range(4):
                y_points[k] = min(tmp, h - 1)
                if tmp < h - 1:
                    tmp += 1

            for channel in range(3):
                x_values = image[int(src_y), x_points, channel]
                result[i, j, channel] = newton_interpolation(src_x, x_points, x_values)

    return np.clip(result, 0, 255).astype(np.uint8)

def spline_interpolation(x: float, x_points: np.ndarray, y_points: np.ndarray) -> float:
    unique_x_points, indices = np.unique(x_points, return_index=True)
    if len(unique_x_points) != len(x_points):
        y_points = y_points[indices]
        x_points = unique_x_points
        if len(x_points) < 2:
            return y_points[0]

    cs = interpolate.CubicSpline(x_points, y_points, bc_type='natural')
    return cs(x)

def upscale_spline(image: np.ndarray, scale: float = 2.0) -> np.ndarray:
    if len(image.shape) != 3 or image.shape[2] != 3:
        raise ValueError("Input image must be RGB with shape (h, w, 3)")

    h, w, c = image.shape
    new_h, new_w = int(h * scale), int(w * scale)
    result = np.zeros((new_h, new_w, 3), dtype=np.float64)

    for i in range(new_h):
        for j in range(new_w):
            src_x = j / scale
            src_y = i / scale

            x_points = np.zeros(4, dtype=np.int64)
            tmp = int(src_x)
            start = max(0, tmp - 2)
            for k in range(4):
                x_points[k] = min(start + k, w - 1)

            y_points = np.zeros(4, dtype=np.int64)
            tmp = int(src_y)
            start = max(0, tmp - 2)
            for k in range(4):
                y_points[k] = min(start + k, h - 1)

            for channel in range(3):
                x_values = image[int(src_y), x_points, channel]
                result[i, j, channel] = spline_interpolation(src_x, x_points, x_values)

    return np.clip(result, 0, 255).astype(np.uint8)

def calculate_psnr(original: np.ndarray, processed: np.ndarray) -> float:
    mse = np.mean((original - processed) ** 2)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    return 20 * np.log10(max_pixel / np.sqrt(mse))
