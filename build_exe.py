#!/usr/bin/env python3
"""
Local build script to create DungeonCrawlerAI executable.
Run: python build_exe.py
"""

import subprocess
import sys
import os
import shutil

def main():
    print("=" * 50)
    print("  DungeonCrawlerAI - Build Executable")
    print("=" * 50)
    print()

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")

    # Build command
    print("\nBuilding executable...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "DungeonCrawlerAI",
        "--console",  # Keep console for text-based game
        "main_enhanced.py"
    ]

    # Add icon if exists
    if os.path.exists("icon.ico"):
        cmd.extend(["--icon", "icon.ico"])

    try:
        subprocess.check_call(cmd)
        print("\n✓ Build successful!")
        
        # Check output
        exe_path = os.path.join("dist", "DungeonCrawlerAI.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n  Output: {exe_path}")
            print(f"  Size: {size_mb:.1f} MB")
            
            # Create release folder
            release_dir = "release"
            if os.path.exists(release_dir):
                shutil.rmtree(release_dir)
            os.makedirs(release_dir)
            
            # Copy files
            shutil.copy(exe_path, release_dir)
            shutil.copy("README.md", release_dir)
            if os.path.exists("README_ENHANCED.md"):
                shutil.copy("README_ENHANCED.md", release_dir)
            
            print(f"\n  Release folder created: {release_dir}/")
            print("\n  You can now distribute the 'release' folder!")
        else:
            print("\n✗ Executable not found!")
            return 1

    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        return 1

    print("\n" + "=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())
