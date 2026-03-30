#!/usr/bin/env python3
"""
Auto Clicker - Hybrid Edition
Single Target Mode Application
Windows/Linux/Mac Compatible

Main entry point for the application
No Firebase, no ads, no external monitoring
Pure local automation tool
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from gui import main

if __name__ == "__main__":
    print("=" * 60)
    print("Auto Clicker - Hybrid Edition (Single Target Mode)")
    print("=" * 60)
    print()
    print("Features:")
    print("  • Single target clicking automation")
    print("  • Configurable click intervals")
    print("  • Multiple stop conditions (time/cycles)")
    print("  • Anti-detection mode")
    print("  • CSV-based configuration storage")
    print()
    print("No External Services:")
    print("  • No Firebase")
    print("  • No Google Analytics")
    print("  • No Ads")
    print("  • No In-App Purchases")
    print("  • 100% Local Execution")
    print()
    print("=" * 60)
    print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
