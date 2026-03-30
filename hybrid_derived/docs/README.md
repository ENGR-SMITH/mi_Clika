# Auto Clicker - Hybrid Edition v1.0

## Overview

**Auto Clicker - Hybrid Edition** is a cross-platform desktop application for Windows, Linux, and macOS that automates repetitive mouse clicks at a single target location.

**Key Difference from Original:**
- ✓ Single Target Mode ONLY (no multi-target sequences)
- ✓ NO Firebase integration
- ✓ NO Google Analytics or monitoring
- ✓ NO Ads or In-App Purchases
- ✓ CSV-based local storage
- ✓ 100% local execution - no external services
- ✓ Cross-platform (Windows/Linux/Mac)

---

## System Requirements

### Minimum Requirements
- **Python:** 3.7 or higher
- **OS:** Windows, Linux, or macOS
- **RAM:** 100 MB minimum
- **Disk Space:** 50 MB for application

### Dependencies
```
pyautogui==0.9.53
```

---

## Installation

### Option 1: Windows Executable (Recommended for Non-Programmers)

Download the pre-compiled executable from the `releases` folder:
```
auto_clicker_hybrid.exe
```

Simply double-click to run. No Python installation needed.

### Option 2: Python Installation

1. **Install Python 3.7+**
   - Download from: https://www.python.org/downloads/
   - Make sure "Add Python to PATH" is checked during installation

2. **Clone or Extract the Project**
   ```bash
   # Navigate to the project directory
   cd hybrid_derived
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

---

## Quick Start Guide

### 1. Setting Target Position

**Method A: Manual Entry**
1. Open the "Control Panel" tab
2. Enter X and Y coordinates in the "Target Position" section
3. Coordinates represent the screen position where clicks will occur

**Method B: Cursor Position**
1. Click the "Get Cursor Position" button
2. Move your mouse to the desired location
3. The coordinates will be automatically filled in

### 2. Configure Settings

**Click Interval**
- Minimum: 10 milliseconds
- Maximum: 10,000 milliseconds (10 seconds)
- Default: 500 milliseconds (0.5 seconds)
- This is the delay between consecutive clicks

**Stop Condition**
- **Indefinite:** Clicking continues until manually stopped
- **Time-based:** Specify duration in seconds (1-9999)
- **Cycles-based:** Specify number of clicks (1-9999)

**Anti-Detection Mode**
- Adds random variations to make clicking less detectable
- Random position offset: ±1-5 pixels
- Random interval variation: ±10%
- Useful for evading bot detection systems

### 3. Save Configuration

1. Go to "Settings" tab
2. Configure all parameters
3. Click "Save Settings"
4. Switch to "Configurations" tab
5. Click "Save Current as..."
6. Enter a name for the configuration
7. Click "Save"

### 4. Start Automation

1. Click the green **"▶ START"** button
2. Clicking will begin at the configured position
3. Watch the statistics update in real-time
4. Use **"⏸ PAUSE"** to temporarily stop
5. Use **"⏹ STOP"** to end automation

### 5. Manage Configurations

**Load Configuration**
1. Go to "Configurations" tab
2. Select a configuration from the list
3. Click "Load"
4. Settings are restored from the saved configuration

**Delete Configuration**
1. Select a configuration
2. Click "Delete"
3. Confirm deletion

**Export Configuration**
1. Select a configuration
2. Click "Export"
3. Save as CSV file
4. Share with others or backup

**Import Configuration**
1. Click "Import"
2. Select a CSV file
3. Configuration is imported with a new ID
4. Appears in the configuration list

---

## User Interface Tabs

### Control Panel
- **Status Display:** Shows current state (Running/Paused/Stopped)
- **Target Position:** Set X and Y coordinates
- **Get Cursor Position:** Helper to capture current mouse position
- **Statistics:** Real-time display of clicks and elapsed time
- **Control Buttons:** Start, Pause/Resume, Stop

### Settings
- **Click Interval:** Delay between clicks (milliseconds)
- **Stop Condition:** Choose when to stop clicking
- **Stop Value:** Duration or cycles (context-dependent)
- **Anti-Detection:** Toggle random variations
- **Anti-Detection Offset:** Maximum pixel offset
- **Save Settings:** Persist settings for next session

### Configurations
- **Saved Configurations:** List of all stored configurations
- **Load:** Restore settings from selected configuration
- **Save Current as:** Store current settings as new configuration
- **Delete:** Remove selected configuration
- **Export:** Save configuration to CSV file
- **Import:** Load configuration from CSV file

### About
- Application information
- Feature list
- Requirements
- Usage instructions
- No external service tracking

---

## Data Storage

### File Structure
```
hybrid_derived/
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── src/
│   ├── config.py       # Configuration management (CSV)
│   ├── click_engine.py # Click simulation engine
│   └── gui.py          # GUI application
└── data/               # Data directory (created automatically)
    ├── targets.csv     # Saved configurations
    └── settings.json   # Application settings
```

### CSV Format (targets.csv)

```csv
id,name,x_pos,y_pos,click_interval,stop_condition,stop_value,anti_detection,is_active
1,My Config,500,300,500,1,60,false,true
2,Gaming Setup,1000,500,100,2,1000,true,true
```

**Columns:**
- `id`: Unique identifier (auto-incremented)
- `name`: Configuration name
- `x_pos`: X coordinate for clicks
- `y_pos`: Y coordinate for clicks
- `click_interval`: Milliseconds between clicks
- `stop_condition`: 0=Indefinite, 1=Time, 2=Cycles
- `stop_value`: Duration (seconds) or clicks
- `anti_detection`: true/false
- `is_active`: true/false

### JSON Format (settings.json)

```json
{
  "click_interval": 500,
  "stop_condition": 0,
  "stop_value": 0,
  "anti_detection": false,
  "anti_detection_max_offset": 5
}
```

---

## Architecture

### Component Structure

```
┌─────────────────────────────────────┐
│         GUI Application (gui.py)    │
│  ├─ Control Panel                   │
│  ├─ Settings                        │
│  ├─ Configuration Manager           │
│  └─ About                           │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
   ┌───▼────┐      ┌───▼────────────┐
   │ Config  │      │ Click Engine   │
   │ Manager │      │ (click_engine) │
   │(config) │      │                │
   └────┬────┘      └────┬───────────┘
        │                │
   ┌────▼──────┐     ┌───▼────────────┐
   │ CSV Files │     │ PyAutoGUI      │
   │ (targets) │     │ (Mouse Control)│
   └───────────┘     └────────────────┘
```

### Data Flow

```
User Input (GUI)
      ↓
Config Manager (Validation)
      ↓
Click Engine (Configuration)
      ↓
Mouse Control Library (PyAutoGUI)
      ↓
System Mouse Driver
      ↓
Screen Clicks Executed
      ↓
Statistics Updated in GUI
```

---

## Configuration Examples

### Example 1: Game Farming
```
Configuration Name: Farming Bot
Target Position: X=640, Y=360
Click Interval: 200ms
Stop Condition: Cycles (5000 clicks)
Anti-Detection: Enabled
```

### Example 2: Repetitive Task
```
Configuration Name: Data Entry
Target Position: X=1000, Y=200
Click Interval: 1000ms
Stop Condition: Time-based (60 seconds)
Anti-Detection: Disabled
```

### Example 3: Idle Game
```
Configuration Name: Clicker Game
Target Position: X=500, Y=500
Click Interval: 50ms
Stop Condition: Indefinite
Anti-Detection: Enabled (offset: 10)
```

---

## Anti-Detection System

### How It Works

When enabled, anti-detection adds randomization:

1. **Position Randomization**
   - Offset range: ±1 to ±5 pixels (configurable)
   - Prevents exact coordinate patterns
   - Example: 500,300 → randomly clicks within 495-505, 295-305

2. **Interval Randomization**
   - Variation: ±10% of configured interval
   - Example: 500ms interval → 450-550ms actual
   - Avoids mechanical timing patterns

3. **Gesture Randomization**
   - Click duration varies by ±5-50ms
   - Makes clicking less detectable as bot

### When to Enable
- Gaming with anti-cheat detection
- Apps with bot detection
- Frequent clicking at same coordinates
- When evading detection is desired

### Limitations
- Advanced ML-based detection may still identify patterns
- Not foolproof against sophisticated systems
- Use responsibly and legally

---

## Command Line Usage

### Run with Default Settings
```bash
python main.py
```

### Run in Dummy Mode (Testing)
```bash
# Modify main.py to use: ClickEngine(use_dummy=True)
# Simulates clicks without moving mouse (for testing)
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Q | Close application |
| Tab | Navigate between tabs |
| Enter | Activate focused button |

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'pyautogui'"

**Solution:**
```bash
pip install pyautogui
```

### Problem: Clicks not appearing at correct location

**Solution:**
1. Use "Get Cursor Position" button to verify coordinates
2. Check for multi-monitor setup (coordinate offset)
3. Try slightly offset position (+10-20 pixels)

### Problem: Clicking too slow

**Solution:**
1. Reduce click interval (minimum: 10ms)
2. Disable anti-detection (if enabled)
3. Check system performance

### Problem: Application crashes when clicking

**Solution:**
1. Ensure pyautogui is properly installed
2. Check for conflicting mouse software
3. Try running as Administrator (Windows)

### Problem: Can't select target position

**Solution:**
1. Check display scaling (Windows 10+)
2. Try "Get Cursor Position" button instead
3. Verify screen resolution in display settings

---

## Performance Considerations

### CPU Usage
- Idle: <1%
- Clicking (10ms interval): 5-15%
- Clicking (1000ms interval): <5%

### Memory Usage
- Base application: 30-50 MB
- With multiple configurations: 50-100 MB

### Network Usage
- NONE - 100% local execution
- No external communication
- No data transmission

---

## Security Notes

### Data Privacy
- All data stored locally in `data/` folder
- No data sent to external servers
- No analytics collection
- No monitoring whatsoever

### File System
- CSV files are plain text (readable)
- Settings stored in JSON format
- No encryption (for simplicity)
- Users can edit CSV files directly if needed

### System Security
- Does not require administrator rights (usually)
- Does not modify system files
- Can be uninstalled cleanly
- No registry modifications (Windows)

---

## Development

### For Developers

**Project Structure:**
```
hybrid_derived/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── src/
│   ├── __init__.py      # Package initialization
│   ├── config.py        # Config management module
│   ├── click_engine.py  # Click simulation module
│   └── gui.py           # GUI application module
├── data/
│   ├── targets.csv      # Saved configurations
│   └── settings.json    # Application settings
└── docs/
    └── README.md        # This file
```

**Adding New Features:**

1. **New Click Type:** Modify `ClickEngine` class
2. **New Stop Condition:** Add to `StopCondition` enum
3. **New Configuration Field:** Update CSV columns and models
4. **New GUI Element:** Add to appropriate tab in `AutoClickerGUI`

**Testing:**

```python
# Test in dummy mode (no actual clicking)
engine = ClickEngine(use_dummy=True)
engine.configure(500, 500, 100, StopCondition.CYCLES_BASED, 10)
engine.start_clicking()
```

---

## Version History

### v1.0 (Current)
- Initial release
- Single Target Mode
- CSV configuration storage
- Anti-detection features
- Cross-platform support

---

## License & Usage

**Disclaimer:**

This application is provided "as-is" for educational and legitimate automation purposes. Users are responsible for:

- Ensuring legal use in their jurisdiction
- Complying with terms of service of target applications
- Not using for unauthorized access or fraud
- Responsible and ethical automation practices

**Prohibited Uses:**
- Circumventing security systems
- Unauthorized access to accounts
- Violating terms of service
- Illegal automation activities

---

## Support & Contact

### Getting Help

1. Check the Troubleshooting section above
2. Review configuration examples
3. Test with dummy mode to isolate issues

### Common Questions

**Q: Can this click websites?**
A: Yes, it clicks any screen position regardless of application.

**Q: Does it work on Mac?**
A: Yes, pyautogui supports macOS with coordinate system adjustments.

**Q: Can I run multiple instances?**
A: Not recommended - may cause coordinate conflicts.

**Q: Is this detectable as a bot?**
A: Anti-detection mode reduces detectability but not foolproof.

**Q: How long can it run?**
A: Indefinitely, until manually stopped or stop condition met.

---

## Comparison with Original Android Version

| Feature | Original (Android) | Hybrid (Desktop) |
|---------|-------------------|--------------------|
| Platform | Android only | Windows/Linux/Mac |
| Single Mode | ✓ | ✓ |
| Multi Mode | ✓ | ✗ |
| Firebase | ✓ | ✗ |
| Analytics | ✓ | ✗ |
| Ads | ✓ | ✗ |
| In-App Purchase | ✓ | ✗ |
| CSV Storage | ✗ | ✓ |
| Local Only | ✗ | ✓ |
| GUI Framework | Android Material | Tkinter |
| Dependencies | Android SDK | Python + PyAutoGUI |

---

## FAQ

**Q: Will this harm my computer?**
A: No. It only moves the mouse and clicks. No files are modified.

**Q: Can I run it without Python?**
A: Yes, use the compiled executable (Windows).

**Q: Is my data safe?**
A: Yes, data never leaves your computer. All storage is local.

**Q: Can I use this for automation at work?**
A: Check with your employer. Some organizations prohibit automation.

**Q: How accurate is the clicking?**
A: ±5 pixels (or configured offset) with anti-detection enabled.

**Q: Can I use for testing my own app?**
A: Yes, this is a legitimate use case for UI testing.

---

## Conclusion

Auto Clicker - Hybrid Edition is a lightweight, privacy-respecting automation tool for legitimate desktop clicking tasks. With no external services, no monitoring, and 100% local execution, it provides complete control and transparency.

**Key Benefits:**
- ✓ Cross-platform (Windows/Linux/Mac)
- ✓ No external dependencies or services
- ✓ Privacy-focused (local storage only)
- ✓ Easy to use GUI
- ✓ Flexible configuration management
- ✓ Anti-detection capabilities
- ✓ Open and transparent operation

---

**Last Updated:** February 2024  
**Version:** 1.0  
**Status:** Production Ready
