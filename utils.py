"""
3D Harita Görüntüleyici - Yardımcı Fonksiyonlar
"""

import math
import numpy as np
import os
import time
import logging
from typing import Tuple, List, Optional
from config import APP_SETTINGS

# Logging setup
logging.basicConfig(
    level=getattr(logging, APP_SETTINGS['LOG_LEVEL']),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_coordinates(lat: float, lon: float) -> bool:
    """Koordinat doğrulaması yapar"""
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return False
    
    if not (-90 <= lat <= 90):
        return False
    
    if not (-180 <= lon <= 180):
        return False
    
    return True

def deg2rad(degrees: float) -> float:
    """Derece to radyan çevirici"""
    return degrees * math.pi / 180.0

def rad2deg(radians: float) -> float:
    """Radyan to derece çevirici"""
    return radians * 180.0 / math.pi

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """İki koordinat arası mesafeyi hesaplar (km)"""
    R = 6371  # Dünya yarıçapı (km)
    
    dlat = deg2rad(lat2 - lat1)
    dlon = deg2rad(lon2 - lon1)
    
    a = (math.sin(dlat/2) * math.sin(dlat/2) + 
         math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * 
         math.sin(dlon/2) * math.sin(dlon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def tile_to_lat_lon(x: int, y: int, z: int) -> Tuple[float, float]:
    """Tile koordinatlarını lat/lon'a çevirir"""
    n = 2.0 ** z
    lon = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat = math.degrees(lat_rad)
    return lat, lon

def lat_lon_to_tile(lat: float, lon: float, z: int) -> Tuple[int, int]:
    """Lat/lon'u tile koordinatlarına çevirir"""
    lat_rad = math.radians(lat)
    n = 2.0 ** z
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return x, y

def calculate_tile_bounds(center_lat: float, center_lon: float, zoom: int, 
                         tile_count: int = 3) -> List[Tuple[int, int]]:
    """Merkez koordinat etrafındaki tile'ları hesaplar"""
    center_x, center_y = lat_lon_to_tile(center_lat, center_lon, zoom)
    
    tiles = []
    half_count = tile_count // 2
    
    for dx in range(-half_count, half_count + 1):
        for dy in range(-half_count, half_count + 1):
            tiles.append((center_x + dx, center_y + dy))
    
    return tiles

def normalize_elevation_data(elevation_data: np.ndarray) -> np.ndarray:
    """Elevation verilerini normalize eder (0-1 arası)"""
    min_val = np.min(elevation_data)
    max_val = np.max(elevation_data)
    
    if max_val == min_val:
        return np.zeros_like(elevation_data)
    
    return (elevation_data - min_val) / (max_val - min_val)

def smooth_elevation_data(elevation_data: np.ndarray, iterations: int = 1) -> np.ndarray:
    """Elevation verilerini düzleştirir"""
    smoothed = elevation_data.copy()
    
    for _ in range(iterations):
        # Gaussian blur benzeri işlem
        kernel = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]]) / 16
        
        # Convolution işlemi
        rows, cols = smoothed.shape
        result = np.zeros_like(smoothed)
        
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                region = smoothed[i-1:i+2, j-1:j+2]
                result[i, j] = np.sum(region * kernel)
        
        # Kenarları koru
        result[0, :] = smoothed[0, :]
        result[-1, :] = smoothed[-1, :]
        result[:, 0] = smoothed[:, 0]
        result[:, -1] = smoothed[:, -1]
        
        smoothed = result
    
    return smoothed

def calculate_normals(elevation_data: np.ndarray, scale: float = 1.0) -> np.ndarray:
    """Elevation verilerinden normal vektörleri hesaplar"""
    rows, cols = elevation_data.shape
    normals = np.zeros((rows, cols, 3))
    
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            # Gradient hesapla
            dx = elevation_data[i, j + 1] - elevation_data[i, j - 1]
            dy = elevation_data[i + 1, j] - elevation_data[i - 1, j]
            
            # Normal vektör
            normal = np.array([-dx * scale, -dy * scale, 2.0])
            
            # Normalize
            length = np.linalg.norm(normal)
            if length > 0:
                normal /= length
            else:
                normal = np.array([0, 0, 1])
            
            normals[i, j] = normal
    
    # Kenar normalleri
    normals[0, :] = normals[1, :]
    normals[-1, :] = normals[-2, :]
    normals[:, 0] = normals[:, 1]
    normals[:, -1] = normals[:, -2]
    
    return normals

def generate_heightmap_texture(elevation_data: np.ndarray) -> np.ndarray:
    """Elevation verilerinden texture oluşturur"""
    normalized = normalize_elevation_data(elevation_data)
    
    # Renk haritası
    colors = np.zeros((elevation_data.shape[0], elevation_data.shape[1], 3))
    
    for i in range(elevation_data.shape[0]):
        for j in range(elevation_data.shape[1]):
            height = normalized[i, j]
            
            if height < 0.3:  # Su
                colors[i, j] = [0.2, 0.4, 0.8]
            elif height < 0.6:  # Düşük arazi
                colors[i, j] = [0.2, 0.7, 0.2]
            elif height < 0.8:  # Orta yükseklik
                colors[i, j] = [0.6, 0.4, 0.2]
            else:  # Yüksek
                colors[i, j] = [0.9, 0.9, 0.9]
    
    return (colors * 255).astype(np.uint8)

def ensure_cache_directory(cache_dir: str = None) -> str:
    """Cache dizininin var olduğundan emin olur"""
    if cache_dir is None:
        cache_dir = APP_SETTINGS['CACHE_DIR']
    
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def clean_old_cache_files(cache_dir: str = None, max_age_days: int = 7):
    """Eski cache dosyalarını temizler"""
    if cache_dir is None:
        cache_dir = APP_SETTINGS['CACHE_DIR']