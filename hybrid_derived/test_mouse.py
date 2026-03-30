#!/usr/bin/env python3
"""
Test script to verify mouse control is working
"""

import time
import sys

print("=" * 60)
print("MOUSE CONTROL TEST")
print("=" * 60)

# Test pyautogui
print("\n1. Testing pyautogui...")
try:
    import pyautogui
    print("   ✓ pyautogui imported successfully")
    
    # Get current position
    x, y = pyautogui.position()
    print(f"   ✓ Current mouse position: ({x}, {y})")
    
    # Try to move mouse
    print("   → Moving mouse to (100, 100)...")
    pyautogui.moveTo(100, 100, duration=1)
    x, y = pyautogui.position()
    print(f"   ✓ Mouse moved to: ({x}, {y})")
    
    # Try a click
    print("   → Performing test click at (100, 100)...")
    pyautogui.FAILSAFE = False
    pyautogui.mouseDown()
    time.sleep(0.05)
    pyautogui.mouseUp()
    print("   ✓ Click performed!")
    
    print("\n   SUCCESS: pyautogui is working!")
    pyautogui_works = True
    
except Exception as e:
    print(f"   ✗ pyautogui error: {e}")
    pyautogui_works = False

# Test mouse library
print("\n2. Testing mouse library...")
try:
    import mouse
    print("   ✓ mouse library imported successfully")
    
    # Get current position
    x, y = mouse.get_position()
    print(f"   ✓ Current mouse position: ({x}, {y})")
    
    # Try to move mouse
    print("   → Moving mouse to (200, 200)...")
    mouse.move(200, 200, duration=1)
    x, y = mouse.get_position()
    print(f"   ✓ Mouse moved to: ({x}, {y})")
    
    # Try a click
    print("   → Performing test click at (200, 200)...")
    mouse.click()
    print("   ✓ Click performed!")
    
    print("\n   SUCCESS: mouse library is working!")
    mouse_works = True
    
except Exception as e:
    print(f"   ✗ mouse library error: {e}")
    mouse_works = False

print("\n" + "=" * 60)
print("TEST RESULTS:")
print("=" * 60)
print(f"pyautogui: {'✓ WORKING' if pyautogui_works else '✗ FAILED'}")
print(f"mouse:     {'✓ WORKING' if mouse_works else '✗ FAILED'}")

if not pyautogui_works and not mouse_works:
    print("\n⚠️  WARNING: Neither library can control the mouse!")
    print("This might require:")
    print("  • Administrator privileges (run as Admin)")
    print("  • Different security/permissions settings")
    sys.exit(1)
elif pyautogui_works or mouse_works:
    print("\n✓ Mouse control is available!")
    sys.exit(0)

print("=" * 60)
