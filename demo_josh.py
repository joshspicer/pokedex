#!/usr/bin/env python3
"""
Demonstration script showing that Pokemon Josh (ID: 1026) works correctly
Usage: python demo_josh.py
"""

import sys
import os
sys.path.append('src')

# Mock tkinter modules for headless testing
import unittest.mock as mock
sys.modules['tkinter'] = mock.MagicMock()
sys.modules['tkinter.ttk'] = mock.MagicMock()
sys.modules['tkinter.messagebox'] = mock.MagicMock()
sys.modules['tkinter.filedialog'] = mock.MagicMock()

from app import PokedexApp

def demo_josh():
    print("🔍 Pokemon Josh Demo")
    print("=" * 30)
    
    # Create app instance
    app = PokedexApp.__new__(PokedexApp)
    app.root = None
    
    # Get Josh's data
    print("📊 Getting Pokemon data for Josh (ID: 1026)...")
    josh_data = app.get_pokemon_data(1026)
    
    if josh_data:
        print(f"✅ Name: {josh_data['name']}")
        print(f"✅ GIF URL: {josh_data['gif_url'] or 'None (custom Pokemon)'}")
    else:
        print("❌ Failed to get Josh data")
        return
    
    # Get Josh's image
    print("\n🖼️  Loading Pokemon image for Josh...")
    josh_image = app.get_pokemon_image(1026)
    
    if josh_image:
        print(f"✅ Image loaded successfully!")
        print(f"✅ Image size: {josh_image.size}")
        print(f"✅ Image mode: {josh_image.mode}")
    else:
        print("❌ Failed to load Josh image")
        return
    
    print("\n🎉 Pokemon Josh is fully functional in the Pokedex!")
    print("   - You can search for Pokemon #1026 to find Josh")
    print("   - Josh has a custom image and appears like any other Pokemon")
    print("   - The app now supports Pokemon numbers 1-1026 (was 1-1025)")

if __name__ == "__main__":
    demo_josh()