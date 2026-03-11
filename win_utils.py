"""
Desktop Newton - Windows Utility Module
Handles Windows-specific API calls for desktop integration.
"""
import pygame
import sys

# Try to import win32 modules (only available on Windows)
try:
    import win32gui
    import win32con
    import win32api
    import ctypes
    from ctypes import wintypes
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


# Window style constants
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080
WS_BORDER = 0x00800000
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000

# Layered window constants
LWA_COLORKEY = 0x00000001
LWA_ALPHA = 0x00000002


def get_window_handle():
    """Get the window handle for the current pygame window."""
    if not WIN32_AVAILABLE:
        return None
    
    try:
        # Get the window handle from pygame
        window_info = pygame.display.get_wm_info()
        hwnd = window_info.get('window')
        return hwnd
    except Exception as e:
        print(f"Error getting window handle: {e}")
        return None


def setup_layered_window(hwnd, transparent_color=(255, 0, 255)):
    """
    Set up the window as a layered window with transparency.
    This allows the desktop to show through transparent areas.
    """
    if not WIN32_AVAILABLE or hwnd is None:
        return False
    
    try:
        # Get current window style
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        
        # Add layered and transparent extended styles
        new_style = style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST | WS_EX_TOOLWINDOW
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
        
        # Set the color key for transparency
        # Pixels with this color will be transparent
        color_key = win32api.RGB(*transparent_color)
        win32gui.SetLayeredWindowAttributes(hwnd, color_key, 255, LWA_COLORKEY)
        
        return True
    except Exception as e:
        print(f"Error setting up layered window: {e}")
        return False


def set_click_through(hwnd, enable=True):
    """
    Enable or disable click-through behavior.
    When enabled, mouse clicks pass through to the desktop except on opaque areas.
    """
    if not WIN32_AVAILABLE or hwnd is None:
        return False
    
    try:
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        
        if enable:
            style |= WS_EX_TRANSPARENT
        else:
            style &= ~WS_EX_TRANSPARENT
            
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
        return True
    except Exception as e:
        print(f"Error setting click-through: {e}")
        return False


def set_always_on_top(hwnd, enable=True):
    """Set the window to always stay on top."""
    if not WIN32_AVAILABLE or hwnd is None:
        return False
    
    try:
        # Use SetWindowPos to set the Z-order
        flags = win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        if enable:
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, flags)
        else:
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, flags)
        return True
    except Exception as e:
        print(f"Error setting always-on-top: {e}")
        return False


def remove_window_border(hwnd):
    """Remove the window border and title bar."""
    if not WIN32_AVAILABLE or hwnd is None:
        return False
    
    try:
        # Remove standard window styles
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style &= ~(WS_BORDER | WS_CAPTION | WS_THICKFRAME)
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
        
        # Force window update
        win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 
            win32con.SWP_FRAMECHANGED | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
        return True
    except Exception as e:
        print(f"Error removing window border: {e}")
        return False


def set_window_position(hwnd, x, y, width, height):
    """Set the window position and size."""
    if not WIN32_AVAILABLE or hwnd is None:
        return False
    
    try:
        win32gui.SetWindowPos(hwnd, 0, x, y, width, height, 
            win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)
        return True
    except Exception as e:
        print(f"Error setting window position: {e}")
        return False


def get_screen_size():
    """Get the primary screen size."""
    if WIN32_AVAILABLE:
        try:
            # Use Windows API to get screen size
            user32 = ctypes.windll.user32
            return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        except Exception as e:
            print(f"Error getting screen size: {e}")
    
    # Fallback to pygame display info
    info = pygame.display.Info()
    return info.current_w, info.current_h


class WindowManager:
    """Manages window state for desktop integration."""
    
    TRANSPARENT_COLOR = (255, 0, 255)  # Magenta - used as transparency key
    
    def __init__(self):
        self.hwnd = None
        self.click_through_enabled = True
        self.always_on_top = True
        
    def initialize(self):
        """Initialize the window manager and get the window handle."""
        if not WIN32_AVAILABLE:
            print("Warning: Win32 modules not available. Running in compatibility mode.")
            return False
            
        self.hwnd = get_window_handle()
        if self.hwnd:
            # Remove border first
            remove_window_border(self.hwnd)
            
            # Set up layered window for transparency
            setup_layered_window(self.hwnd, self.TRANSPARENT_COLOR)
            
            # Set always on top
            set_always_on_top(self.hwnd, True)
            
            return True
        return False
        
    def setup_click_through(self, enable):
        """Enable or disable click-through."""
        self.click_through_enabled = enable
        return set_click_through(self.hwnd, enable)
        
    def toggle_click_through(self):
        """Toggle click-through state."""
        self.click_through_enabled = not self.click_through_enabled
        return self.setup_click_through(self.click_through_enabled)
        
    def set_position(self, x, y, width, height):
        """Set the window position."""
        return set_window_position(self.hwnd, x, y, width, height)
        
    def get_transparent_color(self):
        """Get the color used for transparency."""
        return self.TRANSPARENT_COLOR
        
    def is_windows(self):
        """Check if running on Windows with win32 support."""
        return WIN32_AVAILABLE and sys.platform == 'win32'
