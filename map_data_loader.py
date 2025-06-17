"""
Harita Veri Yükleyici - Elevation ve texture verilerini çevrimiçi kaynaklardan alır
"""

import requests
import numpy as np
from PIL import Image
import io
import math
import time
import os
from concurrent.futures import ThreadPoolExecutor
import threading


class MapDataLoader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PyQt6-3D-Map-Viewer/1.0'
        })
        
        # Cache dizini
        self.cache_dir = "cache"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_elevation_data(self, lat, lon, size=50):
        """
        Elevation verilerini alır
        Open-Elevation API kullanır (ücretsiz)
        """
        try:
            # Grid oluştur
            grid_size = 0.01  # Yaklaşık 1km
            half_size = grid_size * size / 2
            
            lats = np.linspace(lat - half_size, lat + half_size, size)
            lons = np.linspace(lon - half_size, lon + half_size, size)
            
            elevation_data = np.zeros((size, size))
            
            # Batch istekleri için koordinatları hazırla
            coordinates = []
            for i, curr_lat in enumerate(lats):
                for j, curr_lon in enumerate(lons):
                    coordinates.append({
                        'latitude': curr_lat,
                        'longitude': curr_lon,
                        'i': i,
                        'j': j
                    })
            
            # Batch olarak elevation verilerini al
            batch_size = 100  # API limitlerini aşmamak için
            
            for batch_start in range(0, len(coordinates), batch_size):
                batch_coords = coordinates[batch_start:batch_start + batch_size]
                
                # API isteği
                locations = [{'latitude': coord['latitude'], 'longitude': coord['longitude']} 
                           for coord in batch_coords]
                
                try:
                    response = self.session.post(
                        'https://api.open-elevation.com/api/v1/lookup',
                        json={'locations': locations},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        results = response.json()['results']
                        
                        for coord, result in zip(batch_coords, results):
                            elevation = result.get('elevation', 0)
                            if elevation is None:
                                elevation = 0
                            elevation_data[coord['i'], coord['j']] = elevation
                    else:
                        # API başarısız olursa, sahte veri oluştur
                        print(f"Elevation API hatası: {response.status_code}")
                        return self._generate_fake_elevation_data(lat, lon, size)
                
                except Exception as e:
                    print(f"Elevation API isteği başarısız: {e}")
                    return self._generate_fake_elevation_data(lat, lon, size)
                
                # API rate limiting için kısa bekleme
                time.sleep(0.1)
            
            return elevation_data
            
        except Exception as e:
            print(f"Elevation veri yükleme hatası: {e}")
            return self._generate_fake_elevation_data(lat, lon, size)
    
    def _generate_fake_elevation_data(self, lat, lon, size):
        """Gerçek veri alınamazsa sahte elevation verisi oluşturur"""
        print("Sahte elevation verisi oluşturuluyor...")
        
        # Perlin noise benzeri sahte veri
        elevation_data = np.zeros((size, size))
        
        for i in range(size):
            for j in range(size):
                # Birden fazla frekans ile noise
                x = i / size * 4
                y = j / size * 4
                
                elevation = 0
                elevation += 50 * math.sin(x * 2) * math.cos(y * 2)
                elevation += 25 * math.sin(x * 4) * math.cos(y * 4)
                elevation += 10 * math.sin(x * 8) * math.cos(y * 8)
                elevation += np.random.normal(0, 5)  # Noise
                
                # Deniz seviyesinin altına inmemesi için
                elevation = max(0, elevation + 100)
                elevation_data[i, j] = elevation
        
        return elevation_data
    
    def get_map_tiles(self, lat, lon, zoom_level=14):
        """
        OpenStreetMap tile'larını alır ve birleştirir
        """
        try:
            # Tile koordinatlarını hesapla
            tile_x, tile_y = self._deg2tile(lat, lon, zoom_level)
            
            # 3x3 tile grid al
            tiles = []
            tile_size = 256
            grid_size = 3
            
            for dy in range(-1, 2):
                row = []
                for dx in range(-1, 2):
                    tx = tile_x + dx
                    ty = tile_y + dy
                    
                    tile_data = self._get_tile(tx, ty, zoom_level)
                    if tile_data:
                        row.append(tile_data)
                    else:
                        # Boş tile için placeholder
                        placeholder = Image.new('RGB', (tile_size, tile_size), (200, 200, 200))
                        row.append(placeholder)
                
                tiles.append(row)
            
            # Tile'ları birleştir
            combined_image = self._combine_tiles(tiles)
            return combined_image
            
        except Exception as e:
            print(f"Tile yükleme hatası: {e}")
            # Hata durumunda basit gradient oluştur
            return self._generate_gradient_texture()
    
    def _deg2tile(self, lat, lon, zoom):
        """Lat/lon'u tile koordinatlarına çevirir"""
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return x, y
    
    def _get_tile(self, x, y, z):
        """Tek bir OSM tile'ını indirir"""
        cache_file = os.path.join(self.cache_dir, f"tile_{z}_{x}_{y}.png")
        
        # Cache'den kontrol et
        if os.path.exists(cache_file):
            try:
                return Image.open(cache_file)
            except:
                os.remove(cache_file)  # Bozuk cache dosyasını sil
        
        # OSM sunucusundan indir
        url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                
                # Cache'e kaydet
                image.save(cache_file)
                return image
            else:
                print(f"Tile indirme hatası: {response.status_code} for {url}")
                return None
                
        except Exception as e:
            print(f"Tile indirme exception: {e}")
            return None
    
    def _combine_tiles(self, tiles):
        """Tile'ları birleştirerek tek görüntü oluşturur"""
        if not tiles or not tiles[0]:
            return self._generate_gradient_texture()
        
        tile_size = 256
        grid_height = len(tiles)
        grid_width = len(tiles[0])
        
        # Birleştirilmiş görüntü oluştur
        combined_width = grid_width * tile_size
        combined_height = grid_height * tile_size
        combined_image = Image.new('RGB', (combined_width, combined_height))
        
        # Tile'ları yerleştir
        for i, row in enumerate(tiles):
            for j, tile in enumerate(row):
                if tile:
                    x = j * tile_size
                    y = i * tile_size
                    combined_image.paste(tile, (x, y))
        
        return combined_image
    
    def _generate_gradient_texture(self):
        """Basit gradient texture oluşturur"""
        size = 512
        image = Image.new('RGB', (size, size))
        pixels = []
        
        for y in range(size):
            for x in range(size):
                # Basit gradient
                r = int(100 + (x / size) * 100)
                g = int(150 + (y / size) * 50)
                b = int(80 + ((x + y) / (2 * size)) * 100)
                pixels.append((r, g, b))
        
        image.putdata(pixels)
        return image
    
    def get_satellite_imagery(self, lat, lon, zoom_level=16):
        """
        Uydu görüntülerini alır (Mapbox veya Google alternatifi)
        Bu örnek için basit implementation
        """
        try:
            # Mapbox Static API (API key gerekli)
            # Bu örnekte OSM tile'ları kullanıyoruz
            return self.get_map_tiles(lat, lon, zoom_level)
        except Exception as e:
            print(f"Uydu görüntüsü alınamadı: {e}")
            return self._generate_gradient_texture()
    
    def get_terrain_data_advanced(self, lat, lon, size=100):
        """
        Gelişmiş terrain verisi - NASA SRTM verilerini kullanır
        Bu örnekte basitleştirilmiş
        """
        try:
            # SRTM verilerini gerçek projede buradan alabilirsiniz:
            # https://dwtkns.com/srtm30m/
            # Şimdilik basit versiyonu kullanıyoruz
            return self.get_elevation_data(lat, lon, size)
        except Exception as e:
            print(f"Gelişmiş terrain verisi alınamadı: {e}")
            return self._generate_fake_elevation_data(lat, lon, size)