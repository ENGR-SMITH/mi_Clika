# Hybrid Single Target Clicker - Quick Start Guide

## Installation

### Prerequisites
- Python 3.7 or higher
- Windows, Mac, or Linux

### Step 1: Install Python
Download from [python.org](https://www.python.org) if not already installed.

### Step 2: Install Dependencies
```bash
# Navigate to the hybrid_derived folder
cd hybrid_derived

# Install required packages
pip install -r requirements.txt
```

**What gets installed:**
- `pyautogui` - For mouse click simulation

tkinter comes built-in with Python, no separate installation needed.

---

## Running the App

### Windows
```bash
python main.py
```

### Mac/Linux
```bash
python3 main.py
```

The GUI window will appear with all controls ready to use.

---

## Basic Usage

### 1. Set Target Position
Two ways to specify where to click:

**Method A: Manual Entry**
- Enter X coordinate in "X Position" field
- Enter Y coordinate in "Y Position" field

**Method B: Auto-Capture**
- Click "Get Mouse Position" button
- Move your mouse to target location
- Click the button again (position auto-updates)

### 2. Configure Click Settings

**Click Interval**
- Time between consecutive clicks (milliseconds)
- Example: 500 = 500ms between each click
- Range: 1-60000ms

**Click Type**
- Single Click (left mouse button)
- Double Click (two rapid clicks)
- Right Click (right mouse button)

### 3. Set Stop Condition

Choose when clicking should stop:

**Indefinite**
- Clicking continues forever
- You must click STOP button to end
- Useful for: Unlimited grinding, continuous monitoring

**Stop After Time**
- Clicking stops after X seconds
- Enter number of seconds in "Value" field
- Useful for: Timed sessions, scheduled tasks

**Stop After Cycles**
- Clicking stops after X clicks
- Enter number of clicks in "Value" field
- Useful for: Fixed-count tasks, exact repetitions

### 4. Advanced Options

**Anti-Detection**
- Checkbox to enable randomization
- Makes clicking appear more "human-like"
- Adds random variations to:
  - Click position (±X pixels)
  - Click interval (±10%)
  - Click duration (±5-50ms)

**Anti-Detection Offset**
- Maximum pixel offset for position randomization
- Range: 0-10+ pixels
- Example: offset=5 means clicks can be 0-5 pixels away from target

### 5. Start Automation

1. Click **START** button
2. Clicking will begin at target position
3. Monitor **Statistics** section:
   - Clicks: Total clicks performed
   - Elapsed Time: Time running
   - Status: Current state (Running/Paused/Stopped)

### 6. Control Automation

**PAUSE Button**
- Temporarily pause clicking
- Button changes to RESUME
- Click again to resume

**STOP Button**
- Completely stop automation
- Statistics display final results
- Confirmation dialog shown

---

## Configuration Management

### Save Configuration

Save current settings for later use:

1. Configure all parameters
2. Click **Save Config** button
3. Enter a name for the configuration
4. Saved to internal database

### Load Configuration

Reload a previously saved configuration:

1. Click **Load Config** button
2. Select from list of saved configurations
3. All fields automatically populate
4. Ready to run

### Export Configuration

Share configuration with others:

1. Click **Export** button
2. File dialog appears
3. Choose location and filename
4. Saves as `.csv` file
5. Can email or transfer to another computer

### Import Configuration

Load a configuration file:

1. Click **Import** button
2. Select `.csv` file
3. Configuration loaded automatically
4. Assigned new ID to avoid conflicts
5. Ready to use

---

## Practical Examples

### Example 1: Game Auto-Clicker
**Goal:** Click "Attack" button repeatedly in game

1. Position game window on screen
2. Get mouse position of "Attack" button
3. Set:
   - Click Interval: 500ms (2 clicks/second)
   - Stop Condition: Indefinite
   - Click Type: Single Click
4. Click START
5. Click STOP when done

### Example 2: Timed Task
**Goal:** Click for exactly 60 seconds

1. Set target position
2. Set:
   - Click Interval: 100ms (10 clicks/second)
   - Stop Condition: Stop After Time
   - Value: 60 seconds
3. Click START
4. App automatically stops after 60 seconds

### Example 3: Exact Click Count
**Goal:** Click exactly 1000 times

1. Set target position
2. Set:
   - Click Interval: 250ms
   - Stop Condition: Stop After Cycles
   - Value: 1000
3. Click START
4. App stops at 1000 clicks with confirmation dialog

### Example 4: Anti-Bot Protection
**Goal:** Bypass bot detection in game

1. Set target position
2. Enable Anti-Detection checkbox
3. Set Anti-Detection Offset: 5 pixels
4. Set Click Interval: 500ms
5. Configure stop condition
6. Click START
7. Clicking appears randomized and human-like

---

## Statistics Explained

**Clicks**
- Total number of clicks performed
- Increments in real-time while running

**Elapsed Time**
- Seconds since START clicked
- Continues counting until STOP or stop condition met

**Status**
- Ready: App idle, ready to start
- Running: Currently clicking
- Paused: Paused but can resume
- Stopped: Automation ended
- Completed: Finished with results

---

## Keyboard Shortcuts

Currently, keyboard shortcuts not available. Use mouse to click buttons.

---

## Data Storage

### Configuration Files Location

**Windows:**
```
%USERPROFILE%/Desktop/hybrid_derived/data/
```

**Mac/Linux:**
```
~/Desktop/hybrid_derived/data/
```

### Files Created

**targets.csv**
- Contains all saved configurations
- Comma-separated values format
- Can be opened in Excel/LibreOffice

**settings.json**
- App preferences
- Click interval, anti-detection defaults
- Human-readable format

---

## Troubleshooting

### Issue: "pyautogui not installed"

**Solution:**
```bash
pip install pyautogui
```

### Issue: Clicks not working

**Check:**
1. Verify target coordinates are correct
2. Make sure target window has focus
3. Disable any UAC or permission prompts
4. Try clicking button in START interface first

### Issue: Wrong click position

**Solution:**
1. Click "Get Mouse Position" to recapture
2. Or manually enter correct coordinates
3. Use Windows Magnifier (Win+Plus) to find exact pixel location

### Issue: App crashes on start

**Solution:**
1. Reinstall Python
2. Run: `pip install -r requirements.txt`
3. Ensure tkinter installed: `python -m tkinter` (should show window)

### Issue: Configuration not saving

**Solution:**
1. Check folder permissions (data/ folder writeable)
2. Ensure filename not empty
3. Try different configuration name
4. Check disk space available

---

## Tips & Tricks

### Finding Exact Coordinates
- Use Windows Snipping Tool (Win+Shift+S) to measure
- Or use Magnifier (Win+Plus) for zoomed view
- Or open Developer Tools (F12) in browser to inspect elements

### Optimal Click Interval
- Game clicks: 500-1000ms (responsive feel)
- Web automation: 100-300ms (fast but not suspicious)
- Task automation: 250-500ms (balanced)
- Avoid <100ms (looks too robotic)

### Testing Without Clicking
- App has "dummy mode" (see code)
- Run with `use_dummy=True` to test without moving mouse
- Useful for testing configuration before actual use

### Batch Multiple Tasks
- Save each task as separate configuration
- Load each config when needed
- Use different intervals for variety

### Performance Optimization
- Disable Anti-Detection if not needed (faster)
- Increase click interval for battery savings
- Use Stop After Cycles for large batches

---

## Important Notes

⚠️ **Use Responsibly**
- Only automate tasks you own
- Respect game/website terms of service
- Some platforms ban automation
- Use anti-detection carefully to avoid bans

⚠️ **System Stability**
- Very rapid clicking can affect system responsiveness
- Set minimum 50ms interval if experiencing lag
- Pause if system seems overloaded

⚠️ **Monitoring**
- App does not auto-minimize or hide
- Visibility on screen while running
- Other users can see automation happening

---

## Getting Help

### Documentation Files
- `README.md` - Project overview
- `ARCHITECTURE.md` - Technical architecture
- `API.md` - Developer API reference

### Code Comments
- Check source code in `src/` folder
- Detailed comments explaining each section
- Well-documented functions and classes

---

## Next Steps

1. ✓ Install and run the app
2. ✓ Try first auto-click task
3. ✓ Save a configuration
4. ✓ Load and run saved config
5. ✓ Test anti-detection features
6. ✓ Export config for backup

---

## Version Info

- **App Name:** Hybrid Single Target Clicker
- **Version:** 1.0
- **Platform:** Windows, Mac, Linux
- **Python:** 3.7+
- **License:** Open Source (no firebase/ads/monitoring)
- **Dependencies:** Minimal (only pyautogui)

---

Enjoy automated clicking! 🚀

For technical details, see `ARCHITECTURE.md`  
For API usage, see `API.md`
