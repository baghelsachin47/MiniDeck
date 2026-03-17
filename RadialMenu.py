from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QPainter, QColor, QCursor, QRadialGradient, QPen
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
import math

class RadialMenu(QWidget):
    def __init__(self, list_apps):
        super().__init__()
        self.items = list_apps

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resize(500, 500) 
        self.selected = -1

        self.center_radius = 50
        self.radius = 180 
        self.icon_size = 48
        self.clamp_to_screen = True
        self.start_pos = None

        # Animation state tracker (0.0 to 1.0 for each slice)
        self.hover_progress = [0.0] * len(self.items)

        self.mouse_timer = QTimer()
        self.mouse_timer.timeout.connect(self.track_mouse)

        # Window Opacity Animation Setup
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(50) # 150ms fade
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def show(self):
        self.start_pos = QCursor.pos()
        screen = QApplication.screenAt(self.start_pos).geometry()

        menu_size = self.width()
        half = menu_size // 2

        x = self.start_pos.x() - half
        y = self.start_pos.y() - half

        # ---> ONLY CLAMP IF THE SETTING IS TRUE <---
        if getattr(self, 'clamp_to_screen', True):
            x = max(screen.left(), min(x, screen.right() - menu_size))
            y = max(screen.top(), min(y, screen.bottom() - menu_size))

        self.move(x, y)
        
        self.setWindowOpacity(0.0)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()

        self.mouse_timer.start(16) 
        super().show()

    def hide(self):
        self.mouse_timer.stop()
        self.launch_selected()
        self.selected = -1
        # Instantly hide for responsiveness, though we could fade out here too!
        super().hide()

    def track_mouse(self):
        if not self.start_pos:
            return

        current = QCursor.pos()
        dx = current.x() - self.start_pos.x()
        dy = self.start_pos.y() - current.y()

        distance = math.hypot(dx, dy)
        new_selected = -1

        if distance >= self.center_radius and len(self.items) > 0:
            angle = math.degrees(math.atan2(dy, dx))
            angle = (angle + 90) % 360
            slice_angle = 360 / len(self.items)
            new_selected = int(angle / slice_angle)

        self.selected = new_selected

        # --- Smooth Animation Math (Lerping) ---
        needs_update = False
        for i in range(len(self.items)):
            target = 1.0 if i == self.selected else 0.0
            current_prog = self.hover_progress[i]
            
            if current_prog != target:
                # Move 30% towards the target every frame for a snappy "spring" effect
                diff = target - current_prog
                if abs(diff) < 0.01:
                    self.hover_progress[i] = target
                else:
                    self.hover_progress[i] += diff * 0.3
                needs_update = True

        if needs_update:
            self.update()

    def paintEvent(self, event):
        if not self.items:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        center_x = self.width() / 2
        center_y = self.height() / 2

        angle_per_item = 360 / len(self.items)
        icon_radius = (self.center_radius + self.radius) / 2
        gap_angle = 2 if len(self.items) > 1 else 0

        for i in range(len(self.items)):
            start_angle = (i * angle_per_item - 90) + (gap_angle / 2)
            span_angle = angle_per_item - gap_angle

            # Get the exact animation frame (0.0 to 1.0) for this specific slice
            progress = self.hover_progress[i]

            # Smoothly expand the radius based on progress
            current_radius = self.radius + (12 * progress)

            # --- 1. Dynamic Glass Backgrounds ---
            gradient = QRadialGradient(center_x, center_y, current_radius)
            
            # Interpolate colors based on hover progress
            base_r, base_g, base_b = 30, 30, 32   # Obsidian base
            hov_r, hov_g, hov_b = 60, 60, 65      # Lighter hover state
            
            curr_r = int(base_r + (hov_r - base_r) * progress)
            curr_g = int(base_g + (hov_g - base_g) * progress)
            curr_b = int(base_b + (hov_b - base_b) * progress)

            gradient.setColorAt(0.0, QColor(curr_r + 15, curr_g + 15, curr_b + 15, 230))
            gradient.setColorAt(1.0, QColor(curr_r, curr_g, curr_b, 200))
            
            painter.setPen(QPen(QColor(0, 0, 0, 150), 1))
            painter.setBrush(gradient)

            # Draw the slice
            painter.drawPie(
                int(center_x - current_radius),
                int(center_y - current_radius),
                int(current_radius * 2),
                int(current_radius * 2),
                int(start_angle * 16),
                int(span_angle * 16)
            )

            # --- 2. Smooth Glowing Edge Accent ---
            if progress > 0.05: # Only draw if it's actually fading in
                # Smoothly fade in the neon cyan border
                accent_alpha = int(255 * progress)
                accent_pen = QPen(QColor(0, 210, 255, accent_alpha), 3) 
                accent_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                
                painter.setPen(accent_pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                
                painter.drawArc(
                    int(center_x - current_radius),
                    int(center_y - current_radius),
                    int(current_radius * 2),
                    int(current_radius * 2),
                    int((start_angle + 1) * 16),
                    int((span_angle - 2) * 16)
                )

            # --- 3. Clean Icon Rendering ---
            mid_angle = start_angle + span_angle / 2
            rad = math.radians(mid_angle)

            # Push icon outward smoothly
            current_icon_radius = icon_radius + (6 * progress)

            icon_x = center_x + current_icon_radius * math.cos(rad)
            icon_y = center_y - current_icon_radius * math.sin(rad)

            icon = self.items[i].icon
            if icon:
                scaled_icon = icon.scaled(
                    self.icon_size, self.icon_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                painter.drawPixmap(
                    int(icon_x - self.icon_size/2),
                    int(icon_y - self.icon_size/2),
                    scaled_icon
                )

        # --- 4. The Machined Center Hub ---
        hub_gradient = QRadialGradient(center_x, center_y, self.center_radius)
        hub_gradient.setColorAt(0.0, QColor(60, 60, 65, 255))
        hub_gradient.setColorAt(1.0, QColor(25, 25, 28, 255))

        painter.setBrush(hub_gradient)
        painter.setPen(QPen(QColor(10, 10, 10, 200), 2)) 
        
        painter.drawEllipse(
            int(center_x - self.center_radius),
            int(center_y - self.center_radius),
            self.center_radius * 2,
            self.center_radius * 2
        )

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        painter.drawEllipse(
            int(center_x - self.center_radius + 1),
            int(center_y - self.center_radius + 1),
            self.center_radius * 2 - 2,
            self.center_radius * 2 - 2
        )

    def launch_selected(self):
        if self.selected == -1:
            return
        if self.selected >= len(self.items):
            return

        app = self.items[self.selected]
        if app:
            app.open_instance()

    def update_apps(self, applications):
        self.items = applications
        # Reset the hover progress array if the number of apps changes
        self.hover_progress = [0.0] * len(self.items)
        self.update()

    def set_icon_size(self, size):
        self.icon_size = size
        self.update()

    def set_radius(self, radius):
        self.radius = radius
        self.update()