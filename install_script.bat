@echo off
echo ========================================
echo 3D Harita Goruntuleyici - Otomatik Kurulum
echo ========================================
echo.

echo Python versiyonu kontrol ediliyor...
python --version
if errorlevel 1 (
    echo HATA: Python yuklu degil!
    echo Python 3.8+ yukleyin: https://python.org
    pause
    exit /b 1
)

echo.
echo Pip guncelleniyor...
python -m pip install --upgrade pip

echo.
echo Gerekli paketler yukleniliyor...
echo - PyQt6 yukleniliyor...
python -m pip install PyQt6>=6.4.0

echo - PyOpenGL yukleniliyor...
python -m pip install PyOpenGL>=3.1.6
python -m pip install PyOpenGL-accelerate>=3.1.6

echo - Diger paketler yukleniliyor...
python -m pip install numpy>=1.21.0
python -m pip install Pillow>=9.0.0
python -m pip install requests>=2.28.0

echo.
echo Cache dizini olusturuluyor...
if not exist cache mkdir cache

echo.
echo Kurulum tamamlandi!
echo.
echo Uygulamayi calistirmak icin:
echo python main.py
echo.
pause