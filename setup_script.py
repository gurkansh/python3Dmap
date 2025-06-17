#!/usr/bin/env python3
"""
3D Harita Görüntüleyici - Kurulum Scripti
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Python versiyonunu kontrol eder"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 veya üstü gereklidir!")
        print(f"Şu anki versiyon: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} uygun")
    return True

def install_requirements():
    """Requirements.txt'den paketleri yükler"""
    try:
        print("📦 Gerekli paketler yükleniyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Tüm paketler başarıyla yüklendi")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Paket yükleme hatası: {e}")
        return False

def test_opengl():
    """OpenGL kurulumunu test eder"""
    try:
        print("🎮 OpenGL test ediliyor...")
        import OpenGL.GL
        from PyQt6.QtOpenGL import QOpenGLWidget
        print("✅ OpenGL kurulumu başarılı")
        return True
    except ImportError as e:
        print(f"❌ OpenGL kurulum hatası: {e}")
        print("Çözüm için README.md dosyasını kontrol edin")
        return False

def create_directories():
    """Gerekli dizinleri oluşturur"""
    dirs = ["cache"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"📁 {dir_name}/ dizini oluşturuldu")

def test_internet_connection():
    """İnternet bağlantısını test eder"""
    try:
        print("🌐 İnternet bağlantısı test ediliyor...")
        import requests
        response = requests.get("https://api.open-elevation.com/", timeout=5)
        print("✅ İnternet bağlantısı çalışıyor")
        return True
    except:
        print("⚠️  İnternet bağlantısı yok - offline mod kullanılacak")
        return False

def run_demo():
    """Demo uygulamayı çalıştırır"""
    try:
        print("🚀 Demo uygulaması başlatılıyor...")
        print("Uygulama açıldığında varsayılan İstanbul koordinatları yüklü olacak.")
        print("'3D Haritayı Yükle' butonuna tıklayarak test edebilirsiniz.")
        
        # Ana uygulamayı import et ve çalıştır
        import main
        main.main()
        
    except KeyboardInterrupt:
        print("\n👋 Uygulama kapatıldı")
    except Exception as e:
        print(f"❌ Uygulama başlatma hatası: {e}")

def main():
    """Ana kurulum fonksiyonu"""
    print("=" * 50)
    print("🗺️  3D Harita Görüntüleyici - Kurulum")
    print("=" * 50)
    
    # Sistem kontrolleri
    if not check_python_version():
        return
    
    # Paket kurulumu
    if not install_requirements():
        return
    
    # OpenGL testi
    if not test_opengl():
        return
    
    # Dizin oluşturma
    create_directories()
    
    # İnternet testi
    test_internet_connection()
    
    print("\n" + "=" * 50)
    print("✅ Kurulum tamamlandı!")
    print("=" * 50)
    
    # Demo çalıştırma seçeneği
    response = input("\nDemo uygulamasını şimdi çalıştırmak ister misiniz? (e/h): ")
    if response.lower() in ['e', 'evet', 'y', 'yes']:
        run_demo()
    else:
        print("\nUygulamayı manuel olarak çalıştırmak için:")
        print("python main.py")

if __name__ == "__main__":
    main()