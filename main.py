"""
Desktop Newton - Main Application
A modern recreation of the classic Desktop Newton ragdoll simulation.
"""
import pygame
import pymunk
import pymunk.pygame_util
import sys
import os
import math

from physics import PhysicsWorld
from gui import SettingsPanel, MiniToggleButton
from win_utils import WindowManager


class DesktopNewton:
    """
    Main application class for Desktop Newton.
    Handles rendering, input, and coordinates physics and GUI.
    """
    
    def __init__(self):
        pygame.init()
        
        # Window settings
        self.screen_width = 1200
        self.screen_height = 800
        self.fps = 60
        
        # Create window - use NOFRAME for borderless
        self.window_flags = pygame.NOFRAME
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            self.window_flags
        )
        pygame.display.set_caption("Desktop Newton")
        
        # Try to set window icon
        self._set_window_icon()
        
        # Initialize window manager for desktop integration
        self.win_manager = WindowManager()
        self.win_manager.initialize()
        
        # Create clock
        self.clock = pygame.time.Clock()
        
        # Fill screen with transparent color
        self.transparent_color = self.win_manager.get_transparent_color()
        
        # Initialize physics
        self.physics = PhysicsWorld()
        self.ragdoll = self.physics.create_ragdoll(
            position=(self.screen_width // 2, self.screen_height // 3),
            scale=1.0
        )
        
        # Drawing options for pymunk
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        pymunk.pygame_util.positive_y_is_up = False
        
        # GUI
        self.gui_font = pygame.font.SysFont('Arial', 14)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        
        def gui_callback(name, value):
            self._handle_gui_event(name, value)
            
        self.settings_panel = SettingsPanel(20, 50, 260, gui_callback)
        self.settings_panel.set_font(self.gui_font)
        
        self.mini_button = MiniToggleButton(20, 50, self._toggle_settings)
        self.mini_button.set_font(self.gui_font)
        
        # Input state
        self.dragging = False
        self.dragged_part = None
        
        # Application state
        self.running = True
        self.show_help = True
        
    def _set_window_icon(self):
        """Load and set the window icon."""
        icon_paths = [
            'assets/icons/7.png',
            'assets/icons/6.png',
            'assets/icons/5.png',
        ]
        for path in icon_paths:
            if os.path.exists(path):
                try:
                    icon = pygame.image.load(path)
                    pygame.display.set_icon(icon)
                    break
                except Exception as e:
                    print(f"Error loading icon from {path}: {e}")
                    
    def _handle_gui_event(self, name, value):
        """Handle events from the GUI."""
        if name == 'gravity':
            self.physics.set_gravity(value)
        elif name == 'damping':
            self.physics.set_damping(value)
        elif name == 'elasticity':
            self.physics.set_elasticity(value)
        elif name == 'scale':
            # Rebuild ragdoll with new scale
            current_pos = self.ragdoll.parts[0].get_position() if self.ragdoll.parts else (
                self.screen_width // 2, self.screen_height // 3
            )
            self.physics.create_ragdoll(position=current_pos, scale=value)
            self.ragdoll = self.physics.ragdoll
        elif name == 'color_head':
            self.ragdoll.set_color('head', value)
        elif name == 'color_torso':
            self.ragdoll.set_color('torso', value)
        elif name == 'reset':
            self._reset_ragdoll()
            
    def _reset_ragdoll(self):
        """Reset the ragdoll to initial position."""
        if self.ragdoll:
            self.ragdoll.destroy()
        scale = self.settings_panel.get_slider_value('scale') or 1.0
        self.ragdoll = self.physics.create_ragdoll(
            position=(self.screen_width // 2, self.screen_height // 3),
            scale=scale
        )
        
    def _toggle_settings(self):
        """Toggle the settings panel visibility."""
        self.settings_panel.toggle()
        
    def handle_events(self):
        """Process input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
                elif event.key == pygame.K_h:
                    self.show_help = not self.show_help
                    continue
                elif event.key == pygame.K_SPACE:
                    self._reset_ragdoll()
                    continue
                elif event.key == pygame.K_s:
                    self.settings_panel.toggle()
                    continue
                    
            # GUI events
            if self.settings_panel.handle_event(event):
                continue
                
            if not self.settings_panel.visible:
                if self.mini_button.handle_event(event):
                    continue
                    
            # Mouse events for dragging
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Don't start drag if clicking on GUI
                    if self.settings_panel.visible and self.settings_panel.rect.collidepoint(event.pos):
                        continue
                    
                    # Check for ragdoll part under mouse
                    part = self.physics.start_drag(event.pos)
                    if part:
                        self.dragging = True
                        self.dragged_part = part
                        # Disable click-through while dragging
                        if self.win_manager.is_windows():
                            self.win_manager.setup_click_through(False)
                            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.physics.end_drag()
                    self.dragging = False
                    self.dragged_part = None
                    # Re-enable click-through
                    if self.win_manager.is_windows():
                        self.win_manager.setup_click_through(True)
                        
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self.physics.update_drag(event.pos)
                    
    def update(self, dt):
        """Update the physics simulation."""
        self.physics.step(dt)
        
    def draw_ragdoll(self):
        """Draw the ragdoll with enhanced visuals."""
        if not self.ragdoll:
            return
            
        for part in self.ragdoll.parts:
            body = part.body
            shape = part.shape
            
            if isinstance(shape, pymunk.Circle):
                # Draw circle shape (head)
                pos = body.position
                radius = shape.radius
                angle = body.angle
                
                # Draw filled circle
                pygame.draw.circle(self.screen, part.color, (int(pos.x), int(pos.y)), int(radius))
                
                # Draw outline
                pygame.draw.circle(self.screen, (0, 0, 0), (int(pos.x), int(pos.y)), int(radius), 2)
                
                # Draw direction indicator
                end_x = pos.x + radius * 0.7 * math.cos(angle)
                end_y = pos.y + radius * 0.7 * math.sin(angle)
                pygame.draw.line(self.screen, (0, 0, 0), (pos.x, pos.y), (end_x, end_y), 2)
                
            elif isinstance(shape, pymunk.Poly):
                # Draw polygon shape (limbs, torso)
                vertices = shape.get_vertices()
                world_vertices = [body.local_to_world(v) for v in vertices]
                points = [(int(v.x), int(v.y)) for v in world_vertices]
                
                # Draw filled polygon
                if len(points) >= 3:
                    pygame.draw.polygon(self.screen, part.color, points)
                    pygame.draw.polygon(self.screen, (0, 0, 0), points, 2)
                    
        # Draw joints
        for joint in self.ragdoll.joints:
            if isinstance(joint, pymunk.PivotJoint):
                anchor_a = joint.a.local_to_world(joint.anchor_a)
                anchor_b = joint.b.local_to_world(joint.anchor_b)
                # Average position for visualization
                mid_x = (anchor_a.x + anchor_b.x) / 2
                mid_y = (anchor_a.y + anchor_b.y) / 2
                
                pygame.draw.circle(self.screen, (255, 255, 255), (int(mid_x), int(mid_y)), 4)
                pygame.draw.circle(self.screen, (0, 0, 0), (int(mid_x), int(mid_y)), 4, 1)
                
    def draw(self):
        """Render the frame."""
        # Fill with transparent color
        self.screen.fill(self.transparent_color)
        
        # Draw ragdoll
        self.draw_ragdoll()
        
        # Draw GUI
        self.settings_panel.draw(self.screen)
        if not self.settings_panel.visible:
            self.mini_button.draw(self.screen, self.gui_font)
            
        # Draw help text
        if self.show_help:
            self._draw_help()
            
        # Draw drag indicator
        if self.dragging and self.dragged_part:
            mouse_pos = pygame.mouse.get_pos()
            part_pos = self.dragged_part.get_position()
            pygame.draw.line(self.screen, (255, 255, 0), 
                (int(part_pos.x), int(part_pos.y)), mouse_pos, 2)
                
        # Update display
        pygame.display.flip()
        
    def _draw_help(self):
        """Draw help text overlay."""
        help_texts = [
            "Desktop Newton v1.0",
            "",
            "Controls:",
            "  Left Click + Drag - Grab and throw ragdoll",
            "  Space - Reset ragdoll",
            "  S - Toggle settings panel",
            "  H - Toggle this help",
            "  ESC - Exit",
        ]
        
        y_offset = self.screen_height - 180
        for i, text in enumerate(help_texts):
            if text == "":
                y_offset += 10
                continue
                
            # Draw shadow
            shadow = self.gui_font.render(text, True, (0, 0, 0))
            self.screen.blit(shadow, (12, y_offset + 2))
            
            # Draw text
            if i == 0:
                color = (100, 200, 255)
                surf = self.title_font.render(text, True, color)
            else:
                color = (255, 255, 255)
                surf = self.gui_font.render(text, True, color)
                
            self.screen.blit(surf, (10, y_offset))
            y_offset += 20 if i < 2 else 18
            
    def run(self):
        """Main application loop."""
        print("Desktop Newton started!")
        print("Controls:")
        print("  Left Click + Drag - Grab and throw ragdoll")
        print("  Space - Reset ragdoll")
        print("  S - Toggle settings panel")
        print("  H - Toggle help")
        print("  ESC - Exit")
        
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
        pygame.quit()
        sys.exit()


def main():
    """Application entry point."""
    app = DesktopNewton()
    app.run()


if __name__ == "__main__":
    main()
