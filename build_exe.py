"""
Desktop Newton - Build Script
Builds the application as a Windows executable using PyInstaller.
"""
import subprocess
import sys
import os
import shutil


def main():
    """Build the Desktop Newton executable."""
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Icon path - use the highest quality extracted icon (converted format)
    icon_path = "assets/icons/7_converted.ico"
    if not os.path.exists(icon_path):
        # Try to find any .ico file
        icon_files = []
        for root, dirs, files in os.walk("assets/icons"):
            for f in files:
                if f.endswith(".ico"):
                    icon_files.append(os.path.join(root, f))
        
        if icon_files:
            # Sort to get the highest resolution (7.ico is 128x128)
            icon_files.sort()
            icon_path = icon_files[-1]
        else:
            icon_path = None
            print("Warning: No icon files found. Using default PyInstaller icon.")
    
    print(f"Using icon: {icon_path}")
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # Single executable file
        "--noconsole",         # No console window
        "--name", "DesktopNewton",
        "--clean",             # Clean PyInstaller cache
    ]
    
    if icon_path and os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])
    
    # Add data files (icons)
    cmd.extend(["--add-data", f"assets/icons{os.pathsep}assets/icons"])
    
    # Main script
    cmd.append("main.py")
    
    print("Building executable with command:")
    print(" ".join(cmd))
    print()
    
    # Run PyInstaller
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print("\n" + "="*50)
        print("Build successful!")
        print("="*50)
        print("\nExecutable location: dist/DesktopNewton.exe")
        
        # Create a distribution folder
        dist_dir = "DesktopNewton_v1.0"
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
        os.makedirs(dist_dir)
        
        # Copy executable
        exe_source = "dist/DesktopNewton.exe"
        exe_dest = os.path.join(dist_dir, "DesktopNewton.exe")
        if os.path.exists(exe_source):
            shutil.copy2(exe_source, exe_dest)
            print(f"Copied to: {exe_dest}")
        
        # Copy assets
        assets_dest = os.path.join(dist_dir, "assets")
        if os.path.exists("assets"):
            shutil.copytree("assets", assets_dest)
            print(f"Copied assets to: {assets_dest}")
        
        # Create README
        readme_content = """Desktop Newton v1.0
==================

A modern recreation of the classic Desktop Newton ragdoll simulation.

Features:
- High-fidelity Pymunk physics
- Interactive mouse dragging
- Real-time settings GUI
- Desktop integration with transparency

Controls:
  Left Click + Drag  - Grab and throw the ragdoll
  Space              - Reset ragdoll position
  S                  - Toggle settings panel
  H                  - Toggle help display
  ESC                - Exit application

Settings:
  - Gravity: Adjust the downward force
  - Air Resistance: Control damping
  - Bounciness: Set elasticity of ragdoll parts
  - Scale: Change the size of the ragdoll
  - Colors: Customize head and torso colors

System Requirements:
  - Windows 7 or later
  - No installation required (portable executable)

Enjoy!
"""
        with open(os.path.join(dist_dir, "README.txt"), "w") as f:
            f.write(readme_content)
        
        print(f"\nDistribution folder created: {dist_dir}/")
        print("\nTo package for release, zip the folder:")
        print(f"  zip -r DesktopNewton_v1.0.zip {dist_dir}/")
        
    else:
        print("\nBuild failed!")
        print("Check the output above for errors.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
