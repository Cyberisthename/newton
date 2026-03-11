# Desktop Newton

A modern recreation of the classic Desktop Newton ragdoll simulation, built with Python, Pymunk physics, and Pygame.

![Desktop Newton](assets/icons/7.png)

## Features

- **High-Fidelity Physics**: Powered by Pymunk for realistic rigid body dynamics
- **Interactive Ragdoll**: Click and drag to grab, throw, and play with the ragdoll
- **Real-Time Settings GUI**: Adjust physics parameters on the fly
  - Gravity control
  - Air resistance (damping)
  - Bounciness (elasticity)
  - Scale adjustment
  - Color customization
- **Desktop Integration**: Transparent, borderless, always-on-top window (Windows)
- **Original Icons**: Uses the original Desktop Newton v3.2 icons extracted from the legacy executable

## Controls

| Key | Action |
|-----|--------|
| Left Click + Drag | Grab and throw ragdoll parts |
| Space | Reset ragdoll to starting position |
| S | Toggle settings panel |
| H | Toggle help display |
| ESC | Exit application |

## Installation

### Requirements

- Python 3.8+
- Windows 7/8/10/11 (for desktop integration features)

### Setup

1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```

## Building Executable

To create a standalone Windows executable (.exe):

```bash
python build_exe.py
```

This will:
1. Install PyInstaller if not present
2. Build a single-file executable with the original icons
3. Create a distribution folder `DesktopNewton_v1.0/` ready for packaging

The built executable will be in `dist/DesktopNewton.exe`.

## Project Structure

```
├── main.py           # Application entry point
├── physics.py        # Ragdoll and Pymunk physics logic
├── gui.py            # Settings panel and UI components
├── win_utils.py      # Windows API integration for desktop features
├── build_exe.py      # PyInstaller build script
├── requirements.txt  # Python dependencies
├── assets/
│   └── icons/        # Original extracted icons (1.ico - 7.ico)
└── README.md         # This file
```

## Technical Details

### Physics Engine
- **Pymunk 7.2+**: 2D physics library built on Chipmunk
- Bodies: Head (circle), Torso/Limbs (polygons)
- Joints: PivotJoint for connections, RotaryLimitJoint for realistic limb constraints
- Mouse interaction: Temporary PivotJoint for smooth dragging

### Graphics
- **Pygame CE 2.5+**: Modern fork of Pygame with enhanced features
- Hardware-accelerated rendering
- Transparent window using colorkey (magenta)

### Desktop Integration (Windows)
- Layered window with `WS_EX_LAYERED` style
- Click-through areas using `WS_EX_TRANSPARENT`
- Always-on-top with `HWND_TOPMOST`

## Legacy Version

This is a recreation of the original **Desktop Newton v3.2** (2009), a lightweight Win32 application. The original executable and resources are preserved in the repository for reference.

- Original: MFC42-based Windows application with Direct3D rendering
- Recreation: Modern Python application with Pymunk physics and Pygame rendering

## License

This project recreates the functionality of Desktop Newton for educational purposes. The original application and its resources remain the property of their respective owners.

## Credits

- **Physics**: Pymunk (Chipmunk physics engine)
- **Graphics**: Pygame CE
- **Original Icons**: Extracted from Desktop Newton v3.2
