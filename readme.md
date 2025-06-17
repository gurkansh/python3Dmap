# 3D Harita Görüntüleyici

PyQt6, OpenGL ve OpenStreetMap kullanarak 3D harita görüntüleme uygulaması.

## Özellikler

- **3D Terrain Görüntüleme**: Gerçek elevation verilerini kullanarak 3D arazi modeli
- **Etkileşimli Kontroller**: Fare ile döndürme, zoom, kaydırma
- **Gerçek Harita Verileri**: OpenStreetMap tile'ları ve Open-Elevation API
- **Yükseklik Bazlı Renklendirme**: Su, orman, dağ, kar seviyelerini farklı renklerle gösterim
- **Caching Sistemi**: İndirilen harita verilerini yerel olarak saklar

## Kurulum

### 1. Gereksinimler

Python 3.8+ gereklidir.

```bash
pip install -r requirements.txt
```

### 2. Bağımlılıklar

- **PyQt6**: GUI framework
- **PyOpenGL**: 3D grafik rendering
- **NumPy**: Veri işleme
- **Pillow**: Görüntü işleme
- **Requests**: API istekleri

### 3. Çalıştırma

```bash
python main.py
```

## Kullanım

### Temel Kontroller

1. **Koordinat Girişi**: 
   - Enlem ve boylam değerlerini girin
   - Örnek: İstanbul için 41.0082, 28.9784

2. **Harita Yükleme**:
   - "3D Haritayı Yükle" butonuna tıklayın
   - Veriler yüklenirken progress bar görünür

3. **3D Navigasyon**:
   - **Sol Fare Tuşu + Sürükleme**: Kamerayı döndür
   - **Sağ Fare Tuşu + Sürükleme**: Haritayı kaydır
   - **Fare Tekerleği**: Zoom in/out

### Klavye Kısayolları

- **R**: Kamerayı başlangıç pozisyonuna reset et
- **W**: Wireframe moduna geç
- **S**: Solid (dolu) moduna geç

### Renk Kodları

- **Mavi**: Su seviyeleri (düşük elevation)
- **Yeşil**: Düşük tepeler ve ormanlar
- **Kahverengi**: Orta yükseklik tepeler
- **Beyaz**: Yüksek dağlar ve kar çizgisi

## Proje Yapısı

```
3d-map-viewer/
├── main.py              # Ana uygulama
├── map_widget.py        # 3D OpenGL widget
├── map_data_loader.py   # Veri yükleme modülü
├── requirements.txt     # Python bağımlılıkları
├── cache/              # İndirilen veriler (otomatik oluşur)
└── README.md           # Bu dosya
```

## API'ler ve Veri Kaynakları

### Elevation Verileri
- **Open-Elevation API**: Ücretsiz elevation verisi
- **URL**: https://api.open-elevation.com/
- **Limitler**: Dakikada ~1000 istek

### Harita Tile'ları
- **OpenStreetMap**: Ücretsiz harita tile'ları
- **URL**: https://tile.openstreetmap.org/
- **Politika**: Fair use, caching önerilir

## Gelişmiş Özellikler

### Cache Sistemi
- İndirilen tile'lar `cache/` dizininde saklanır
- Tekrar kullanım için hızlandırır
- Cache temizleme: `cache/` dizinini silin

### Performans Optimizasyonu
- Display lists kullanılarak rendering hızlandırılır
- Batch API istekleri ile veri yükleme optimize edilir
- Multi-threading ile UI donması engellenir

## Sorun Giderme

### Yaygın Hatalar

1. **"No module named 'OpenGL'"**
   ```bash
   pip install PyOpenGL PyOpenGL-accelerate
   ```

2. **API Timeout Hataları**
   - İnternet bağlantınızı kontrol edin
   - Farklı koordinat deneyin
   - Sahte veri modu otomatik devreye girer

3. **Slow Performance**
   - OpenGL driver'larınızı güncelleyin
   - Daha düşük grid resolution kullanın
   - Wireframe modu deneyin (W tuşu)

### Debug Modu

Terminal çıktısından detaylı hata mesajları alabilirsiniz:

```bash
python main.py
```

## Gelecek Geliştirmeler

- [ ] Mapbox/Google Maps entegrasyonu
- [ ] Gerçek zamanlı hava durumu overlay
- [ ] GPX track import/export
- [ ] Topographic contour lines
- [ ] Uydu görüntüsü overlay
- [ ] Çoklu koordinat bookmark sistemi

## Lisans

Bu proje eğitim amaçlıdır. Kullanılan API'ların kendi kullanım koşulları geçerlidir.

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun
3. Commit edin
4. Push edin
5. Pull Request oluşturun

## İletişim

Sorularınız için GitHub Issues kullanabilirsiniz.