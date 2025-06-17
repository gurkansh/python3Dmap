"""
3D OpenGL Widget - Harita görüntüleme ve etkileşim
"""

import numpy as np
from PyQt6.QtOpenGL import QOpenGLWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QMouseEvent, QWheelEvent
from OpenGL.GL import *
from OpenGL.GLU import *
import math


class Map3DWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        
        # Kamera parametreleri
        self.camera_distance = 5.0
        self.camera_rotation_x = -30.0
        self.camera_rotation_y = 0.0
        self.camera_target_x = 0.0
        self.camera_target_y = 0.0
        
        # Mouse kontrolü
        self.last_mouse_pos = None
        self.mouse_sensitivity = 0.5
        
        # Terrain verileri
        self.elevation_data = None
        self.texture_data = None
        self.terrain_size = 50  # Grid boyutu
        self.height_scale = 0.1  # Yükseklik ölçeği
        
        # Render listesi
        self.terrain_list = None
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS
    
    def initializeGL(self):
        """OpenGL başlatma"""
        # Arka plan rengi
        glClearColor(0.5, 0.7, 0.9, 1.0)  # Açık mavi gökyüzü
        
        # Depth testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        # Lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # Light pozisyonu ve özellikleri
        light_pos = [1.0, 1.0, 1.0, 0.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        
        # Material
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Smooth shading
        glShadeModel(GL_SMOOTH)
        
        # Wireframe veya solid toggle için
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    def resizeGL(self, width, height):
        """Pencere boyutu değiştiğinde çağrılır"""
        if height == 0:
            height = 1
        
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        aspect_ratio = width / height
        gluPerspective(45.0, aspect_ratio, 0.1, 100.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def paintGL(self):
        """Çizim fonksiyonu"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Kamera pozisyonu
        cam_x = self.camera_distance * math.cos(math.radians(self.camera_rotation_y)) * math.cos(math.radians(self.camera_rotation_x))
        cam_y = self.camera_distance * math.sin(math.radians(self.camera_rotation_x))
        cam_z = self.camera_distance * math.sin(math.radians(self.camera_rotation_y)) * math.cos(math.radians(self.camera_rotation_x))
        
        gluLookAt(cam_x + self.camera_target_x, cam_y + self.camera_target_y, cam_z,
                  self.camera_target_x, self.camera_target_y, 0,
                  0, 1, 0)
        
        # Grid çiz
        self.draw_grid()
        
        # Terrain çiz
        if self.elevation_data is not None:
            self.draw_terrain()
        else:
            self.draw_placeholder()
    
    def draw_grid(self):
        """Referans grid çizer"""
        glDisable(GL_LIGHTING)
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_LINES)
        
        for i in range(-10, 11):
            # X ekseni çizgileri
            glVertex3f(i * 0.5, -5.0, 0.0)
            glVertex3f(i * 0.5, 5.0, 0.0)
            # Z ekseni çizgileri
            glVertex3f(-5.0, i * 0.5, 0.0)
            glVertex3f(5.0, i * 0.5, 0.0)
        
        glEnd()
        glEnable(GL_LIGHTING)
    
    def draw_placeholder(self):
        """Veri yüklenmeden önce placeholder çizer"""
        glColor3f(0.6, 0.8, 0.6)  # Açık yeşil
        
        # Basit bir tepe
        glBegin(GL_TRIANGLES)
        for i in range(8):
            angle1 = i * 2 * math.pi / 8
            angle2 = (i + 1) * 2 * math.pi / 8
            
            # Tepe noktası
            glNormal3f(0, 0, 1)
            glVertex3f(0, 0, 1)
            
            # Taban noktaları
            glNormal3f(math.cos(angle1), math.sin(angle1), 0.5)
            glVertex3f(math.cos(angle1), math.sin(angle1), 0)
            
            glNormal3f(math.cos(angle2), math.sin(angle2), 0.5)
            glVertex3f(math.cos(angle2), math.sin(angle2), 0)
        glEnd()
    
    def draw_terrain(self):
        """Terrain verilerini çizer"""
        if self.terrain_list is None:
            self.generate_terrain_display_list()
        
        if self.terrain_list is not None:
            glCallList(self.terrain_list)
    
    def generate_terrain_display_list(self):
        """Terrain için display list oluşturur"""
        if self.elevation_data is None:
            return
        
        self.terrain_list = glGenLists(1)
        glNewList(self.terrain_list, GL_COMPILE)
        
        rows, cols = self.elevation_data.shape
        
        # Renk haritası için min/max yükseklik
        min_height = np.min(self.elevation_data)
        max_height = np.max(self.elevation_data)
        height_range = max_height - min_height if max_height != min_height else 1
        
        # Triangle strips ile terrain çiz
        for i in range(rows - 1):
            glBegin(GL_TRIANGLE_STRIP)
            
            for j in range(cols):
                for row in [i, i + 1]:
                    # Koordinatları normalize et
                    x = (j / (cols - 1) - 0.5) * 4
                    y = (row / (rows - 1) - 0.5) * 4
                    z = self.elevation_data[row, j] * self.height_scale
                    
                    # Yükseklik bazlı renk
                    height_ratio = (self.elevation_data[row, j] - min_height) / height_range
                    
                    if height_ratio < 0.3:  # Su seviyesi - mavi
                        glColor3f(0.2, 0.4, 0.8)
                    elif height_ratio < 0.6:  # Düşük - yeşil
                        glColor3f(0.2, 0.7, 0.2)
                    elif height_ratio < 0.8:  # Orta - kahverengi
                        glColor3f(0.6, 0.4, 0.2)
                    else:  # Yüksek - beyaz (kar)
                        glColor3f(0.9, 0.9, 0.9)
                    
                    # Normal hesapla (basit)
                    if row > 0 and row < rows - 1 and j > 0 and j < cols - 1:
                        # Gradient hesapla
                        dx = self.elevation_data[row, j + 1] - self.elevation_data[row, j - 1]
                        dy = self.elevation_data[row + 1, j] - self.elevation_data[row - 1, j]
                        
                        # Normal vektör
                        normal_x = -dx * self.height_scale * 2
                        normal_y = -dy * self.height_scale * 2
                        normal_z = 4.0 / max(rows, cols)
                        
                        # Normalize
                        length = math.sqrt(normal_x**2 + normal_y**2 + normal_z**2)
                        if length > 0:
                            normal_x /= length
                            normal_y /= length
                            normal_z /= length
                        
                        glNormal3f(normal_x, normal_y, normal_z)
                    else:
                        glNormal3f(0, 0, 1)
                    
                    glVertex3f(x, y, z)
            
            glEnd()
        
        glEndList()
    
    def load_terrain_data(self, elevation_data, texture_data=None):
        """Terrain verilerini yükler"""
        self.elevation_data = elevation_data
        self.texture_data = texture_data
        
        # Eski display list'i sil
        if self.terrain_list is not None:
            glDeleteLists(self.terrain_list, 1)
            self.terrain_list = None
        
        # Kamerayı resetle
        self.camera_distance = 8.0
        self.camera_rotation_x = -30.0
        self.camera_rotation_y = 0.0
        self.camera_target_x = 0.0
        self.camera_target_y = 0.0
        
        self.update()
    
    def mousePressEvent(self, event: QMouseEvent):
        """Mouse basma eventi"""
        self.last_mouse_pos = event.pos()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Mouse hareket eventi"""
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.pos()
            return
        
        dx = event.pos().x() - self.last_mouse_pos.x()
        dy = event.pos().y() - self.last_mouse_pos.y()
        
        if event.buttons() & Qt.MouseButton.LeftButton:
            # Sol tık: Dönüş
            self.camera_rotation_y += dx * self.mouse_sensitivity
            self.camera_rotation_x += dy * self.mouse_sensitivity
            
            # X rotasyonunu sınırla
            self.camera_rotation_x = max(-89, min(89, self.camera_rotation_x))
            
        elif event.buttons() & Qt.MouseButton.RightButton:
            # Sağ tık: Kaydırma
            move_speed = 0.01
            self.camera_target_x -= dx * move_speed
            self.camera_target_y += dy * move_speed
        
        self.last_mouse_pos = event.pos()
        self.update()
    
    def wheelEvent(self, event: QWheelEvent):
        """Mouse tekerlek eventi - Zoom"""
        zoom_speed = 0.001
        delta = event.angleDelta().y()
        
        self.camera_distance -= delta * zoom_speed
        self.camera_distance = max(1.0, min(20.0, self.camera_distance))
        
        self.update()
    
    def keyPressEvent(self, event):
        """Klavye eventi"""
        if event.key() == Qt.Key.Key_R:
            # Reset kamera
            self.camera_distance = 5.0
            self.camera_rotation_x = -30.0
            self.camera_rotation_y = 0.0
            self.camera_target_x = 0.0
            self.camera_target_y = 0.0
            self.update()
        elif event.key() == Qt.Key.Key_W:
            # Wireframe toggle
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            self.update()
        elif event.key() == Qt.Key.Key_S:
            # Solid mode
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            self.update()
    
    def cleanup(self):
        """Temizlik"""
        if self.terrain_list is not None:
            glDeleteLists(self.terrain_list, 1)