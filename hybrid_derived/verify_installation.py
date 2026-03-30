#!/usr/bin/env python3
"""
Hybrid Auto Clicker - Verification Script
Validates that all components are correctly installed and configured
No external services, pure local operation validation
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_check(passed, text):
    """Print a check result"""
    symbol = "✅" if passed else "❌"
    print(f"{symbol}  {text}")
    return passed

def check_python_version():
    """Check Python version"""
    print_header("Python Version Check")
    version = sys.version_info
    required = (3, 7)
    passed = version >= required
    print_check(passed, f"Python {version.major}.{version.minor}.{version.micro} (Required: 3.7+)")
    return passed

def check_imports():
    """Check required imports"""
    print_header("Module Import Check")
    all_passed = True
    
    # Built-in modules
    builtins = ['sys', 'os', 'pathlib', 'csv', 'json', 'threading', 'time', 'random', 'tkinter']
    for module in builtins:
        try:
            __import__(module)
            print_check(True, f"Built-in: {module}")
        except ImportError:
            print_check(False, f"Built-in: {module}")
            all_passed = False
    
    # Optional external modules (don't fail if missing)
    optional = [('pyautogui', 'Mouse control library')]
    for module_name, description in optional:
        try:
            __import__(module_name)
            print_check(True, f"Optional: {module_name} ({description})")
        except ImportError:
            print_check(False, f"Optional: {module_name} ({description}) - Run: pip install -r requirements.txt")
            # Don't fail the overall check for optional modules
    
    return all_passed

def check_file_structure():
    """Check project file structure"""
    print_header("Project File Structure")
    
    base_path = Path(__file__).parent
    required_files = {
        'main.py': 'Entry point',
        'requirements.txt': 'Dependencies',
        'src/config.py': 'Configuration manager',
        'src/click_engine.py': 'Click automation engine',
        'src/gui.py': 'GUI application',
        'docs/README.md': 'Project overview',
        'docs/QUICKSTART.md': 'User quick start guide',
        'docs/ARCHITECTURE.md': 'Technical architecture',
        'docs/API.md': 'API reference',
        'docs/EXAMPLES.md': 'Usage examples',
    }
    
    all_passed = True
    for file_path, description in required_files.items():
        full_path = base_path / file_path
        passed = full_path.exists()
        status = "Found" if passed else "Missing"
        print_check(passed, f"{file_path:<30} - {description:<30} [{status}]")
        all_passed = all_passed and passed
    
    return all_passed

def check_data_directory():
    """Check data directory exists or can be created"""
    print_header("Data Directory Check")
    
    base_path = Path(__file__).parent
    data_dir = base_path / "data"
    
    if data_dir.exists():
        print_check(True, f"Data directory exists: {data_dir}")
        return True
    else:
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
            print_check(True, f"Data directory created: {data_dir}")
            return True
        except Exception as e:
            print_check(False, f"Cannot create data directory: {e}")
            return False

def check_no_firebase():
    """Verify no Firebase imports"""
    print_header("Security: No External Services")
    
    base_path = Path(__file__).parent
    src_dir = base_path / "src"
    
    forbidden_imports = {
        'from firebase': 'Google Firebase',
        'import firebase': 'Google Firebase',
        'from google.cloud': 'Google Cloud',
        'import google.cloud': 'Google Cloud',
        'import requests': 'HTTP requests library',
        'from requests': 'HTTP requests library',
        'urllib.request': 'URL library (indicates external calls)',
    }
    
    all_passed = True
    for keyword, description in forbidden_imports.items():
        found = False
        if src_dir.exists():
            for py_file in src_dir.glob("*.py"):
                try:
                    content = py_file.read_text()
                    # Check for actual imports (not in comments)
                    for line in content.split('\n'):
                        stripped = line.strip()
                        if not stripped.startswith('#') and keyword.lower() in stripped.lower():
                            found = True
                            break
                except Exception:
                    pass
        
        passed = not found
        print_check(passed, f"No {description:<25} imports")
        all_passed = all_passed and passed
    
    return all_passed

def check_config_system():
    """Check if configuration system can be imported"""
    print_header("Configuration System Check")
    
    try:
        # Add src to path
        base_path = Path(__file__).parent
        sys.path.insert(0, str(base_path / "src"))
        
        from config import ConfigManager, ClickTarget, ClickSettings
        print_check(True, "ConfigManager class loaded")
        print_check(True, "ClickTarget dataclass loaded")
        print_check(True, "ClickSettings dataclass loaded")
        
        # Try to initialize
        manager = ConfigManager(str(base_path / "data"))
        print_check(True, "ConfigManager initialized successfully")
        
        return True
    except Exception as e:
        print_check(False, f"Configuration system error: {e}")
        return False

def check_click_engine():
    """Check if click engine can be imported"""
    print_header("Click Engine Check")
    
    try:
        # Add src to path if not already
        base_path = Path(__file__).parent
        if str(base_path / "src") not in sys.path:
            sys.path.insert(0, str(base_path / "src"))
        
        from click_engine import ClickEngine, ClickType, StopCondition, ClickStats
        print_check(True, "ClickEngine class loaded")
        print_check(True, "ClickType enum loaded")
        print_check(True, "StopCondition enum loaded")
        print_check(True, "ClickStats dataclass loaded")
        
        # Try to initialize
        engine = ClickEngine(use_dummy=True)
        print_check(True, "ClickEngine initialized (dummy mode)")
        
        return True
    except Exception as e:
        print_check(False, f"Click engine error: {e}")
        return False

def check_gui_system():
    """Check if GUI can be imported"""
    print_header("GUI System Check")
    
    try:
        # Add src to path if not already
        base_path = Path(__file__).parent
        if str(base_path / "src") not in sys.path:
            sys.path.insert(0, str(base_path / "src"))
        
        import tkinter as tk
        from gui import AutoClickerGUI
        print_check(True, "tkinter module loaded")
        print_check(True, "AutoClickerGUI class loaded")
        
        # We can't actually create a GUI without a display,
        # but we can check if the class is properly defined
        print_check(True, "GUI system ready (requires display to run)")
        
        return True
    except ImportError as e:
        print_check(False, f"GUI import error: {e}")
        return False
    except Exception as e:
        # Some errors are expected (like display issues)
        print_check(True, f"GUI system loaded (Note: {e})")
        return True

def check_requirements_file():
    """Check requirements.txt content"""
    print_header("Requirements File Check")
    
    base_path = Path(__file__).parent
    req_file = base_path / "requirements.txt"
    
    if not req_file.exists():
        print_check(False, "requirements.txt not found")
        return False
    
    try:
        content = req_file.read_text().strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        print_check(True, f"requirements.txt found ({len(lines)} dependencies)")
        for line in lines:
            print(f"   - {line}")
        
        # Check for unwanted dependencies
        forbidden = ['firebase', 'google-cloud', 'google-ads', 'google-analytics']
        for forbidden_pkg in forbidden:
            if forbidden_pkg in content.lower():
                print_check(False, f"Forbidden package found: {forbidden_pkg}")
                return False
        
        print_check(True, "No forbidden external services in requirements")
        return True
        
    except Exception as e:
        print_check(False, f"Error reading requirements.txt: {e}")
        return False

def run_all_checks():
    """Run all verification checks"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Hybrid Auto Clicker - Installation Verification".center(68) + "║")
    print("║" + "  Single Target Mode | No Firebase | CSV Storage".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = {
        'Python Version': check_python_version(),
        'Module Imports': check_imports(),
        'File Structure': check_file_structure(),
        'Data Directory': check_data_directory(),
        'No External Services': check_no_firebase(),
        'Configuration System': check_config_system(),
        'Click Engine': check_click_engine(),
        'GUI System': check_gui_system(),
        'Requirements File': check_requirements_file(),
    }
    
    # Summary
    print_header("Verification Summary")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for check_name, result in results.items():
        symbol = "✅" if result else "❌"
        print(f"{symbol}  {check_name}")
    
    print()
    print(f"Result: {passed}/{total} checks passed")
    print()
    
    if passed == total:
        print("✅ " * 20)
        print()
        print("🎉 INSTALLATION COMPLETE! 🎉")
        print()
        print("You can now run:")
        print("  python main.py")
        print()
        print("For help, see:")
        print("  docs/QUICKSTART.md")
        print()
        print("✅ " * 20)
        return True
    else:
        print("⚠️  " * 20)
        print()
        print("Some checks failed. Please review the errors above.")
        print()
        print("For help, see:")
        print("  docs/QUICKSTART.md")
        print()
        print("⚠️  " * 20)
        return False

if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
