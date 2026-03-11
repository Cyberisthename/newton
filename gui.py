"""
Desktop Newton - GUI Module
Real-time settings panel with sliders and color picker.
"""
import pygame
import pygame.gfxdraw


class Slider:
    """A simple horizontal slider widget."""
    
    def __init__(self, x, y, width, min_val, max_val, initial, label, step=0.1):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial
        self.label = label
        self.step = step
        self.dragging = False
        self.handle_radius = 8
        
    def draw(self, surface, font):
        # Draw track
        pygame.draw.rect(surface, (60, 60, 60), self.rect, border_radius=3)
        
        # Draw filled portion
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        filled_width = int(self.rect.width * ratio)
        filled_rect = pygame.Rect(self.rect.x, self.rect.y, filled_width, self.rect.height)
        pygame.draw.rect(surface, (100, 150, 200), filled_rect, border_radius=3)
        
        # Draw handle
        handle_x = self.rect.x + int(self.rect.width * ratio)
        handle_y = self.rect.centery
        pygame.gfxdraw.filled_circle(surface, handle_x, handle_y, self.handle_radius, (200, 200, 200))
        pygame.gfxdraw.aacircle(surface, handle_x, handle_y, self.handle_radius, (150, 150, 150))
        
        # Draw label and value
        label_surf = font.render(f"{self.label}: {self.value:.1f}", True, (255, 255, 255))
        surface.blit(label_surf, (self.rect.x, self.rect.y - 20))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value(event.pos[0])
            return True
        return False
        
    def _update_value(self, mouse_x):
        ratio = (mouse_x - self.rect.x) / self.rect.width
        ratio = max(0, min(1, ratio))
        self.value = self.min_val + ratio * (self.max_val - self.min_val)
        # Round to step
        self.value = round(self.value / self.step) * self.step
        
    def get_value(self):
        return self.value


class ColorButton:
    """A color selection button."""
    
    def __init__(self, x, y, size, color, label):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color
        self.label = label
        self.selected = False
        
    def draw(self, surface, font):
        # Draw color square
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Draw border (thicker if selected)
        border_width = 3 if self.selected else 1
        border_color = (255, 255, 255) if self.selected else (100, 100, 100)
        pygame.draw.rect(surface, border_color, self.rect, border_width)
        
        # Draw label below
        label_surf = font.render(self.label, True, (255, 255, 255))
        surface.blit(label_surf, (self.rect.x, self.rect.bottom + 2))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class Button:
    """A simple button widget."""
    
    def __init__(self, x, y, width, height, text, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        
    def draw(self, surface, font):
        # Draw button background
        color = (100, 150, 200) if self.hovered else (70, 100, 140)
        pygame.draw.rect(surface, color, self.rect, border_radius=4)
        
        # Draw text
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False


class SettingsPanel:
    """
    A toggleable settings panel with sliders for physics parameters
    and color selection buttons.
    """
    
    def __init__(self, x, y, width, callback=None):
        self.rect = pygame.Rect(x, y, width, 400)
        self.visible = True
        self.callback = callback
        self.font = None
        
        # Create sliders
        slider_x = x + 20
        slider_y = y + 50
        slider_width = width - 40
        
        self.sliders = {
            'gravity': Slider(slider_x, slider_y, slider_width, 0, 2000, 900, "Gravity"),
            'damping': Slider(slider_x, slider_y + 70, slider_width, 0.1, 1.0, 0.9, "Air Resistance"),
            'elasticity': Slider(slider_x, slider_y + 140, slider_width, 0.0, 1.0, 0.3, "Bounciness"),
            'scale': Slider(slider_x, slider_y + 210, slider_width, 0.5, 2.0, 1.0, "Scale"),
        }
        
        # Color selection buttons
        color_y = slider_y + 280
        self.color_buttons = {
            'head': [
                ColorButton(slider_x, color_y, 30, (255, 200, 150), "Skin"),
                ColorButton(slider_x + 50, color_y, 30, (255, 100, 100), "Red"),
                ColorButton(slider_x + 100, color_y, 30, (100, 200, 100), "Green"),
                ColorButton(slider_x + 150, color_y, 30, (100, 150, 255), "Blue"),
            ],
            'torso': [
                ColorButton(slider_x, color_y + 60, 30, (100, 150, 200), "Blue"),
                ColorButton(slider_x + 50, color_y + 60, 30, (200, 100, 100), "Red"),
                ColorButton(slider_x + 100, color_y + 60, 30, (100, 200, 100), "Green"),
                ColorButton(slider_x + 150, color_y + 60, 30, (200, 200, 100), "Yellow"),
            ]
        }
        
        self.selected_colors = {'head': 0, 'torso': 0}
        
        # Control buttons
        self.reset_button = Button(slider_x, color_y + 120, slider_width, 30, "Reset Ragdoll", self._reset_callback)
        self.toggle_button = Button(x + width - 30, y + 5, 25, 25, "X", self._toggle_callback)
        
        self.last_values = {k: v.get_value() for k, v in self.sliders.items()}
        
    def _reset_callback(self):
        if self.callback:
            self.callback('reset', None)
            
    def _toggle_callback(self):
        self.visible = False
        
    def set_font(self, font):
        self.font = font
        
    def toggle(self):
        self.visible = not self.visible
        
    def draw(self, surface):
        if not self.visible:
            return
            
        if self.font is None:
            self.font = pygame.font.SysFont('Arial', 14)
            
        # Draw panel background
        panel_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (30, 30, 30, 220), panel_surf.get_rect(), border_radius=8)
        pygame.draw.rect(panel_surf, (100, 100, 100), panel_surf.get_rect(), 2, border_radius=8)
        surface.blit(panel_surf, self.rect.topleft)
        
        # Draw title
        title = self.font.render("Physics Settings", True, (255, 255, 255))
        surface.blit(title, (self.rect.x + 15, self.rect.y + 10))
        
        # Draw close button
        self.toggle_button.draw(surface, self.font)
        
        # Draw sliders
        for slider in self.sliders.values():
            slider.draw(surface, self.font)
            
        # Draw color section label
        color_label = self.font.render("Colors:", True, (200, 200, 200))
        surface.blit(color_label, (self.rect.x + 20, self.rect.y + 330))
        
        # Draw color buttons
        for part_type, buttons in self.color_buttons.items():
            for i, btn in enumerate(buttons):
                btn.selected = (self.selected_colors[part_type] == i)
                btn.draw(surface, self.font)
                
        # Draw reset button
        self.reset_button.draw(surface, self.font)
        
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if self.toggle_button.handle_event(event):
            return True
            
        for slider_name, slider in self.sliders.items():
            if slider.handle_event(event):
                if self.callback and slider.get_value() != self.last_values.get(slider_name):
                    self.last_values[slider_name] = slider.get_value()
                    self.callback(slider_name, slider.get_value())
                return True
                
        for part_type, buttons in self.color_buttons.items():
            for i, btn in enumerate(buttons):
                if btn.handle_event(event):
                    self.selected_colors[part_type] = i
                    if self.callback:
                        self.callback(f'color_{part_type}', btn.color)
                    return True
                    
        if self.reset_button.handle_event(event):
            return True
            
        return False
        
    def get_slider_value(self, name):
        if name in self.sliders:
            return self.sliders[name].get_value()
        return None
        
    def set_slider_value(self, name, value):
        if name in self.sliders:
            self.sliders[name].value = value
            self.last_values[name] = value


class MiniToggleButton:
    """A small button to toggle the settings panel when it's hidden."""
    
    def __init__(self, x, y, callback):
        self.rect = pygame.Rect(x, y, 50, 30)
        self.callback = callback
        self.hovered = False
        
    def draw(self, surface, font):
        color = (100, 150, 200) if self.hovered else (70, 100, 140)
        pygame.draw.rect(surface, color, self.rect, border_radius=4)
        
        # Draw "Settings" label
        text = font.render("Settings", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False
