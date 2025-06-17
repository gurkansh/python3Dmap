"""
3D Harita Görüntüleyici - Konfigürasyon Dosyası
"""

# API Ayarları
API_SETTINGS = {
    'ELEVATION_API_URL': 'https://api.open-elevation.com/api/v1/lookup',
    'OSM_TILE_URL': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    'REQUEST_TIMEOUT': 30,
    'MAX_RETRIES': 3,
    'BATCH_SIZE': 100,  # Elevation API için batch boyutu
    'RATE_LIMIT_DELAY': 0.1,  # Saniye cinsinden
}

# Mapbox API (Opsiyonel - API key gerekli)
MAPBOX_SETTINGS = {
    'ACCESS_TOKEN': '',  # Buraya Mapbox token'ınızı girin
    'STYLE_URL': 'mapbox://styles/mapbox/satellite-v9',
    'TILE_SIZE': 512,
}

# Görüntü Ayarları
RENDER_SETTINGS = {
    'DEFAULT_TERRAIN_SIZE': 50,  # Grid boyutu
    'HEIGHT_SCALE': 0.1,  # Yükseklik çarpanı
    'TILE_CACHE_SIZE': 100,  # MB cinsinden
    'TERRAIN_QUALITY': 'medium',  # low, medium, high
}

# Kamera Ayarları
CAMERA_SETTINGS = {
    'DEFAULT_DISTANCE': 5.0,
    'DEFAULT_ROTATION_X': -30.0,
    'DEFAULT_ROTATION_Y': 0.0,
    'MOUSE_SENSITIVITY': 0.5,
    'ZOOM_SPEED': 0.001,
    'MIN_DISTANCE': 1.0,
    'MAX_DISTANCE': 20.0,
}

# Renk Ayarları
COLOR_SETTINGS = {
    'WATER_COLOR': (0.2, 0.4, 0.8),      # Mavi
    'LAND_LOW_COLOR': (0.2, 0.7, 0.2),    # Yeşil
    'LAND_MID_COLOR': (0.6, 0.4, 0.2),    # Kahverengi
    'LAND_HIGH_COLOR': (0.9, 0.9, 0.9),   # Beyaz
    'GRID_COLOR': (0.3, 0.3, 0.3),        # Gri
    'BACKGROUND_COLOR': (0.5, 0.7, 0.9, 1.0),  # Açık mavi
}

# Yükseklik Eşikleri (0.0 - 1.0 arası normalize)
HEIGHT_THRESHOLDS = {
    'WATER_LEVEL': 0.3,
    'LOW_LAND': 0.6,
    'MID_LAND': 0.8,
}

# Uygulama Ayarları
APP_SETTINGS = {
    'WINDOW_TITLE': '3D Harita Görüntüleyici',
    'WINDOW_WIDTH': 1200,
    'WINDOW_HEIGHT': 800,
    'FPS_TARGET': 60,
    'CACHE_DIR': 'cache',
    'LOG_LEVEL': 'INFO',  # DEBUG, INFO, WARNING, ERROR
}

# Varsayılan Konumlar
DEFAULT_LOCATIONS = {
    'Istanbul': (41.0082, 28.9784),
    'Ankara': (39.9334, 32.8597),
    'Izmir': (38.4192, 27.1287),
    'Antalya': (36.8969, 30.7133),
    'Bursa': (40.1826, 29.0665),
    'Everest': (27.9881, 86.9250),
    'Grand_Canyon': (36.1069, -112.1129),
    'Mount_Fuji': (35.3606, 138.7274),
}

# Performans Ayarları
PERFORMANCE_SETTINGS = {
    'USE_DISPLAY_LISTS': True,
    'USE_VBO': False,  # Vertex Buffer Objects (gelişmiş)
    'MULTISAMPLING': True,
    'VSYNC': True,
    'THREAD_COUNT': 4,  # Veri yükleme için
}

# Hata Ayıklama
DEBUG_SETTINGS = {
    'ENABLE_WIREFRAME': False,
    'SHOW_NORMALS': False,
    'SHOW_GRID': True,
    'PRINT_FPS': False,
    'VERBOSE_LOGGING': False,
}

# Gelişmiş API Ayarları
ADVANCED_API_SETTINGS = {
    # NASA SRTM verisi (gelecekte kullanılabilir)
    'SRTM_API_URL': 'https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/SRTM_GL1',
    
    # Google Elevation API (API key gerekli)
    'GOOGLE_ELEVATION_API': 'https://maps.googleapis.com/maps/api/elevation/json',
    'GOOGLE_API_KEY': '',  # Buraya Google API key'inizi girin
    
    # Mapbox Elevation API
    'MAPBOX_ELEVATION_API': 'https://api.mapbox.com/v4/mapbox.terrain-rgb',
}

def get_terrain_quality_settings(quality='medium'):
    """Terrain kalite ayarlarını döndürür"""
    quality_map = {
        'low': {
            'terrain_size': 30,
            'height_scale': 0.05,
            'tile_zoom': 12,
        },
        'medium': {
            'terrain_size': 50,
            'height_scale': 0.1,
            'tile_zoom': 14,
        },
        'high': {
            'terrain_size': 100,
            'height_scale': 0.2,
            'tile_zoom': 16,
        }
    }
    return quality_map.get(quality, quality_map['medium'])

def get_location_coordinates(location_name):
    """Varsayılan konum koordinatlarını döndürür"""
    return DEFAULT_LOCATIONS.get(location_name, DEFAULT_LOCATIONS['Istanbul'])