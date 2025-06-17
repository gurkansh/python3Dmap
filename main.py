#!/usr/bin/env python3
"""
3D Harita Görüntüleyici - Ana Uygulama
PyQt6, OpenGL ve OpenStreetMap kullanarak 3D harita görüntüleme
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QHBoxLayout, QWidget, QPushButton, QLineEdit, 
                             QLabel, QStatusBar, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from map_widget import Map3DWidget
from map_data_loader import MapDataLoader


class DataLoadingThread(QThread):
    """Harita verilerini arka planda yüklemek için thread"""
    data_loaded = pyqtSignal(object)  # elevation_data, texture_data
    progress_updated = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, lat, lon, zoom_level=14):
        super().__init__()
        self.lat = lat
        self.lon = lon
        self.zoom_level = zoom_level
        self.loader = MapDataLoader()
    
    def run(self):
        try:
            # Elevation verilerini yükle
            self.progress_updated.emit(25)
            elevation_data = self.loader.get_elevation_data(self.lat, self.lon)
            
            # Texture verilerini yükle
            self.progress_updated.emit(50)
            texture_data = self.loader.get_map_tiles(self.lat, self.lon, self.zoom_level)
            
            self.progress_updated.emit(100)
            self.data_loaded.emit((elevation_data, texture_data))
            
        except Exception as e:
            self.error_occurred.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Harita Görüntüleyici")
        self.setGeometry(100, 100, 1200, 800)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Üst kontrol paneli
        self.setup_control_panel(main_layout)
        
        # 3D Harita widget'ı
        self.map_widget = Map3DWidget()
        main_layout.addWidget(self.map_widget)
        
        # Status bar
        self.setup_status_bar()
        
        # Varsayılan konum (İstanbul)
        self.lat_input.setText("41.0082")
        self.lon_input.setText("28.9784")
        
        # Data loading thread
        self.loading_thread = None
    
    def setup_control_panel(self, main_layout):
        """Kontrol panelini oluşturur"""
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        
        # Koordinat girişi
        coord_label = QLabel("Koordinatlar:")
        coord_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        control_layout.addWidget(coord_label)
        
        lat_label = QLabel("Enlem:")
        control_layout.addWidget(lat_label)
        self.lat_input = QLineEdit()
        self.lat_input.setPlaceholderText("41.0082")
        self.lat_input.setMaximumWidth(100)
        control_layout.addWidget(self.lat_input)
        
        lon_label = QLabel("Boylam:")
        control_layout.addWidget(lon_label)
        self.lon_input = QLineEdit()
        self.lon_input.setPlaceholderText("28.9784")
        self.lon_input.setMaximumWidth(100)
        control_layout.addWidget(self.lon_input)
        
        # Haritayı yükle butonu
        self.load_button = QPushButton("3D Haritayı Yükle")
        self.load_button.clicked.connect(self.load_map)
        control_layout.addWidget(self.load_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        control_layout.addWidget(self.progress_bar)
        
        control_layout.addStretch()
        
        # Kontrol talimatları
        instructions = QLabel("Kontroller: Fare ile döndür | Tekerlek ile zoom | Sağ tık+sürükle ile kaydır")
        instructions.setStyleSheet("color: #666; font-style: italic;")
        control_layout.addWidget(instructions)
        
        main_layout.addWidget(control_panel)
    
    def setup_status_bar(self):
        """Status bar'ı oluşturur"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Koordinat girin ve '3D Haritayı Yükle' butonuna tıklayın")
    
    def load_map(self):
        """Harita verilerini yükler"""
        try:
            lat = float(self.lat_input.text())
            lon = float(self.lon_input.text())
            
            # Koordinat doğrulaması
            if not (-90 <= lat <= 90):
                raise ValueError("Enlem -90 ile 90 arasında olmalıdır")
            if not (-180 <= lon <= 180):
                raise ValueError("Boylam -180 ile 180 arasında olmalıdır")
            
            # UI'yi loading moduna al
            self.load_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_bar.showMessage("Harita verileri yükleniyor...")
            
            # Loading thread'i başlat
            self.loading_thread = DataLoadingThread(lat, lon)
            self.loading_thread.data_loaded.connect(self.on_data_loaded)
            self.loading_thread.progress_updated.connect(self.progress_bar.setValue)
            self.loading_thread.error_occurred.connect(self.on_loading_error)
            self.loading_thread.start()
            
        except ValueError as e:
            QMessageBox.warning(self, "Hata", f"Geçersiz koordinat: {str(e)}")
    
    def on_data_loaded(self, data):
        """Veri yükleme tamamlandığında çağrılır"""
        elevation_data, texture_data = data
        
        # 3D widget'a verileri gönder
        self.map_widget.load_terrain_data(elevation_data, texture_data)
        
        # UI'yi normal moda al
        self.load_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("3D harita yüklendi. Fare ile etkileşime geçebilirsiniz.")
    
    def on_loading_error(self, error_message):
        """Veri yükleme hatası durumunda çağrılır"""
        self.load_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Harita yüklenemedi")
        QMessageBox.critical(self, "Hata", f"Harita verileri yüklenirken hata oluştu:\n{error_message}")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("3D Harita Görüntüleyici")
    
    # Ana pencereyi oluştur ve göster
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()