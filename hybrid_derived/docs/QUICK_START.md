# Quick Start Guide - Auto Clicker Hybrid

## 5-Minute Setup

### Step 1: Download and Run
- **Windows:** Double-click `auto_clicker_hybrid.exe`
- **Python:** Run `python main.py` from project folder

### Step 2: Set Target
1. Go to "Control Panel" tab
2. Click "Get Cursor Position"
3. Move mouse to where you want clicks
4. Coordinates auto-fill

### Step 3: Configure
1. Go to "Settings" tab
2. Set Click Interval (e.g., 500ms)
3. Choose Stop Condition
4. Click "Save Settings"

### Step 4: Click!
1. Click green **START** button
2. See clicks happening
3. Click red **STOP** to end

## Example Use Cases

### Use Case 1: Test an App Button
```
Target: Click a login button repeatedly
Steps:
  1. Set X=640, Y=360 (button location)
  2. Interval: 1000ms (1 second)
  3. Stop Condition: Time-based, 30 seconds
  4. Click START
```

### Use Case 2: Gaming Session
```
Target: Click game element continuously
Steps:
  1. Identify target location
  2. Interval: 100ms (fast clicking)
  3. Stop Condition: Cycles, 5000
  4. Enable Anti-Detection
  5. Click START
```

### Use Case 3: Idle Game
```
Target: Repeated tapping
Steps:
  1. Target Position: Game window center
  2. Interval: 200ms
  3. Stop Condition: Indefinite
  4. Click START when ready
  5. Click STOP when done
```

## File Locations

**Configuration Storage:**
```
hybrid_derived/data/targets.csv    ← Configurations here
hybrid_derived/data/settings.json  ← App settings here
```

**View/Edit Configurations:**
- Right-click `targets.csv` → Open with Notepad
- Edit directly if needed
- Save and reload in app

## Keyboard Tips

- **Tab:** Move between fields
- **Enter:** Activate button
- **Ctrl+C:** Stop clicking (emergency)

## Common Settings

| Scenario | Interval | Stop Condition | Anti-Detection |
|----------|----------|-----------------|----------------|
| Testing | 500ms | 10 cycles | No |
| Gaming | 100-200ms | Indefinite | Yes |
| App Testing | 1000ms | 30 seconds | No |
| Bot-protected | 300ms | 100 cycles | Yes |

## Emergency Stop

**If stuck:**
1. Press **STOP** button in GUI
2. Or press **Ctrl+C** in terminal
3. Or force-close application

**Note:** Application will stop immediately. No stuck clicks.

## Troubleshooting Checklist

- [ ] Did you set the target position?
- [ ] Is the interval at least 10ms?
- [ ] Did you click START (green button)?
- [ ] Is the target window visible?
- [ ] Are coordinates within screen bounds?

## Next Steps

1. **Save a Configuration**
   - Go to Configurations tab
   - Click "Save Current as..."
   - Name it and save

2. **Export Configuration**
   - Select in list
   - Click "Export"
   - Share or backup CSV file

3. **Try Anti-Detection**
   - Go to Settings
   - Enable "Anti-Detection"
   - Click "Save Settings"

## Data Backup

**Backup your configurations:**
1. Go to Configurations tab
2. Select each config
3. Click Export
4. Save to backup folder

**Restore from backup:**
1. Go to Configurations tab
2. Click Import
3. Select exported CSV file
4. Configuration restored

## Performance Tips

- Start with 500ms interval
- Increase if too slow
- Decrease if too fast
- Minimum: 10ms
- Maximum: 10,000ms (10 seconds)

## Security Reminder

✓ **Safe:**
- Clicking any application
- Storing local configurations
- Running offline

✗ **Not Safe:**
- Using for unauthorized access
- Bypassing security systems
- Violating app terms of service

---

**Need Help?** See the full README.md in the `docs/` folder.
