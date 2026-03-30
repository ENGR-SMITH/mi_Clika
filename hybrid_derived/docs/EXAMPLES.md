# Hybrid Auto Clicker - Usage Examples

Practical examples for common automation scenarios.

---

## Example 1: Simple Game Clicker

Click at a fixed position 1000 times with 250ms intervals (fast clicking).

### Setup

1. Open the app: `python main.py`
2. Use "Get Mouse Position" to find the click button in your game
3. Enter coordinates: `X: 500`, `Y: 300`
4. Click Settings:
   - Interval: `250` ms
   - Click Type: `Single Click`
5. Stop Condition:
   - Select: `Cycles Based`
   - Value: `1000`
6. Advanced Options:
   - Enable: `Anti-Detection Mode`
   - Offset: `5` pixels

### Click START

The app will:
- Click 1000 times at (500, 300)
- Each click separated by ~250ms
- Add random ±5px offset to coordinates
- Add ±10% variation to interval timing

### Monitor Progress

Watch the Statistics section update in real-time:
- Total clicks counter
- Elapsed time
- Current status

### Result

After ~4 minutes, the automation stops automatically and shows:
- Total clicks: 1000
- Elapsed time: ~4:10 (250ms × 1000 + overhead)
- Success confirmation

---

## Example 2: Timed Task (60 seconds)

Perform repeated actions for exactly 60 seconds. Useful for:
- Time-limited game events
- Automatic form filling
- Background task automation

### Setup

1. Position your click target
2. Click Settings:
   - Interval: `500` ms
   - Click Type: `Single Click`
3. Stop Condition:
   - Select: `Time Based`
   - Value: `60` (seconds)
4. Advanced:
   - Anti-Detection: `Enabled`

### Start

Click START. The app will:
- Click every 500ms for exactly 60 seconds
- Display countdown in status
- Auto-stop after 60s

### Statistics Result

After 60 seconds:
- Total clicks: ~120 (60,000ms ÷ 500ms)
- Elapsed time: 60.0s
- Stops automatically

### Use Case

Perfect for:
- 1-minute event windows in games
- Timed farming/grinding
- Scheduled automation tasks

---

## Example 3: Exact Click Count (1000 clicks)

Precise automation for a specific number of interactions.

### Setup

1. Find target: Use "Get Mouse Position"
2. Click Settings:
   - Interval: `100` ms (fast)
   - Click Type: `Double Click`
3. Stop Condition:
   - Select: `Cycles Based`
   - Value: `1000`
4. Advanced:
   - Anti-Detection: `Disabled` (for maximum speed)

### Why Double Click?

Good for:
- Opening items twice in interfaces
- Double-clicking text fields
- Rapid interaction games

### Start and Wait

Click START. Monitor:
```
Clicks: 0 → 100 → 200 → 500 → 1000
Time: 2s → 5s → 10s → 15-20s → ~20s
```

### Notes

- Double clicks are faster (2 clicks per "cycle")
- Total actual mouse clicks: 2000
- Time: ~10 seconds at 100ms interval

---

## Example 4: Anti-Bot Protection (Randomized)

Simulate human clicking with maximum randomization to avoid detection.

### Setup

1. Target position: `(750, 450)`
2. Click Settings:
   - Interval: `800` ms
   - Click Type: `Single Click`
3. Stop Condition:
   - Select: `Indefinite`
   - (Will run forever until you click STOP)
4. Advanced Options:
   - Anti-Detection: **ENABLED** (critical)
   - Offset: **10 pixels** (maximum)

### Anti-Detection Features Active

When enabled with 10px offset:

1. **Position Jitter**
   - Target: (750, 450)
   - Actual clicks: (745, 440) to (755, 460)
   - Creates human-like slight misalignment

2. **Interval Variation**
   - Set interval: 800ms
   - Actual intervals: 720ms to 880ms (±10%)
   - Never exactly consistent

3. **Duration Variation**
   - Click gesture: 5-50ms random duration
   - Mimics real mouse button press

### Expected Behavior

```
Click 1: (747, 452) at 785ms
Click 2: (751, 448) at 850ms
Click 3: (749, 451) at 750ms
Click 4: (753, 449) at 825ms
...
```

### Monitor Activity

The Statistics show:
- Total clicks: continuously increasing
- Elapsed time: counting up
- Status: "Clicking..."

### When to Stop

Click PAUSE to temporarily halt, or STOP to end completely.

---

## Example 5: Form Filling Automation

Click through a form with multiple fields.

### Scenario

Web form with:
1. Name field: (200, 100)
2. Email field: (200, 150)
3. Submit button: (200, 300)

### Solution: Multiple Configurations

Save 3 separate configurations:

**Config 1: Name Field**
```
Name: Form - Name Field
Position: (200, 100)
Interval: 500ms
Cycles: 1
```

**Config 2: Email Field**
```
Name: Form - Email Field
Position: (200, 150)
Interval: 500ms
Cycles: 1
```

**Config 3: Submit Button**
```
Name: Form - Submit
Position: (200, 300)
Interval: 500ms
Cycles: 1
```

### Execution

1. Load Config 1, Click START
2. When it stops, Load Config 2, Click START
3. When it stops, Load Config 3, Click START
4. Form submitted!

### Workflow

```
Load "Name Field" → START → WAIT → STOP
Load "Email Field" → START → WAIT → STOP
Load "Submit" → START → WAIT → STOP
Done!
```

---

## Example 6: Infinite Clicker (Indefinite)

Continuous clicking for as long as needed. Useful for:
- Farm games
- Idle clickers
- Background automation

### Setup

1. Position: `(640, 360)` (center of screen)
2. Click Settings:
   - Interval: `200` ms
   - Click Type: `Single Click`
3. Stop Condition:
   - Select: `Indefinite`
4. Advanced:
   - Anti-Detection: `Enabled`
   - Offset: `3` pixels

### Start

Click START. The app will:
- Click continuously
- Never stop on its own
- Keep updating statistics

### Monitor

Statistics update every 100ms:
```
0s: 0 clicks
10s: 50 clicks
30s: 150 clicks
60s: 300 clicks
300s (5min): 1500 clicks
```

### Stop When Ready

Click STOP button when:
- You want to end automation
- Target is no longer visible
- Task is complete

### Check Results

Final statistics show:
- Total clicks: 1500 (at 5 minutes)
- Elapsed time: 5:00.2
- Average: 5.0 clicks/second

---

## Example 7: Batch Operations (Multiple Targets)

Execute multiple saved configurations in sequence.

### Create Configurations

```
Config A: Task 1 @ (100, 100) - 500 clicks
Config B: Task 2 @ (200, 200) - 300 clicks
Config C: Task 3 @ (300, 300) - 200 clicks
```

### Batch Script (Manual Execution)

1. **Load → START → STOP**
   ```
   Load "Task 1"
   Click START
   Wait for auto-stop (after 500 cycles)
   ```

2. **Next Task**
   ```
   Load "Task 2"
   Click START
   Wait for auto-stop (after 300 cycles)
   ```

3. **Final Task**
   ```
   Load "Task 3"
   Click START
   Wait for auto-stop (after 200 cycles)
   ```

### Total Results

- Total clicks: 500 + 300 + 200 = 1000 clicks
- Total time: ~8-10 minutes
- All saved with results

### Python Script Alternative

For programmatic batch execution:

```python
from src.config import get_config_manager
from src.click_engine import ClickEngine, StopCondition
import time

config = get_config_manager()
engine = ClickEngine()

task_ids = [1, 2, 3]

for task_id in task_ids:
    target = config.get_target_by_id(task_id)
    
    engine.configure(
        target.x_pos,
        target.y_pos,
        target.click_interval,
        StopCondition(target.stop_condition),
        target.stop_value,
        target.anti_detection
    )
    
    print(f"Executing: {target.name}")
    engine.start_clicking()
    
    while engine.is_clicking():
        time.sleep(1)
    
    stats = engine.get_stats()
    print(f"Completed: {stats.total_clicks} clicks in {stats.elapsed_time:.1f}s")
    
    engine.reset_stats()
    time.sleep(2)  # Pause between tasks

print("All tasks completed!")
```

---

## Example 8: Right-Click Menu Automation

Use right-click to interact with context menus.

### Scenario

Game with right-click context menu:
- Right-click to open menu at (640, 360)
- Menu appears with 3 options
- Click "Use Item" option at (700, 380)

### Setup Configuration 1 (Right-Click)

```
Name: Game - Right Click Menu
Position: (640, 360)
Interval: 1000 ms
Click Type: RIGHT CLICK
Stop Condition: Cycles - 1
```

### Setup Configuration 2 (Select Item)

```
Name: Game - Select Use Item
Position: (700, 380)
Interval: 500 ms
Click Type: SINGLE CLICK
Stop Condition: Cycles - 1
```

### Execute

1. Load "Right Click Menu" → START
2. Wait for menu to appear and click closes
3. Load "Select Use Item" → START
4. Item used!

### Repeat

For repeated use:
```
Load "Right Click Menu" → START
Load "Select Use Item" → START
← Loop
```

---

## Example 9: Export/Import Configuration

Share or backup your configurations.

### Export Your Setup

1. Create a configuration you like
2. Click "Save" to save it first
3. Click "Export Config"
4. Choose location: `Desktop/my_clicker_config.csv`
5. File saved with your settings

### Backup Multiple Configs

Export each configuration:
```
Config 1 → export1.csv
Config 2 → export2.csv
Config 3 → export3.csv
```

Keep them safe!

### Import on New Computer

1. Copy CSV file to new computer
2. Open the app
3. Click "Import Config"
4. Select your `exported.csv` file
5. Configuration loaded and ready to use!

### Share with Others

Export and send the CSV file to others:
- They can import into their own app
- Configuration is portable
- No Firebase or cloud needed

---

## Example 10: Monitoring Long Tasks

Track a 1-hour clicking session.

### Setup

```
Position: (500, 300)
Interval: 1000 ms (1 second)
Stop Condition: Time Based - 3600 seconds (1 hour)
Anti-Detection: Enabled (5px offset)
```

### Start

1. Click START
2. Minimize app if needed
3. Monitor Statistics panel

### Expected Results

**After 10 minutes:**
- Total clicks: ~600
- Elapsed time: 10:00
- Status: "Clicking..."

**After 30 minutes:**
- Total clicks: ~1800
- Elapsed time: 30:00
- Status: "Clicking..."

**After 60 minutes:**
- Total clicks: ~3600
- Elapsed time: 60:00
- Status: "Ready" (auto-stopped)

### View Results

Final statistics dialog shows:
- **Total Clicks: 3600**
- **Duration: 1:00:00** (1 hour)
- **Average: 1.0 clicks/sec**

### Tips

- Save config before running long tasks
- Keep computer plugged in
- Don't move mouse manually (interferes)
- Use PAUSE if you need to intervene
- Resume with PAUSE again

---

## CSV Configuration Examples

### Example CSV Data

Save in `data/targets.csv`:

```csv
id,name,x_pos,y_pos,click_interval,stop_condition,stop_value,anti_detection,is_active
1,Game Clicker,500,300,250,2,1000,true,true
2,Web Task,100,200,500,1,60,false,true
3,Idle Game,640,360,200,0,0,true,true
```

### Fields Explained

- `id`: Unique number (1, 2, 3, ...)
- `name`: Descriptive name for config
- `x_pos`: X coordinate
- `y_pos`: Y coordinate
- `click_interval`: Milliseconds between clicks
- `stop_condition`: 0=indefinite, 1=time, 2=cycles
- `stop_value`: Seconds or cycle count
- `anti_detection`: "true" or "false"
- `is_active`: "true" or "false"

---

## Common Patterns

### Pattern 1: Fast Clicking

```
Interval: 50-100 ms
Anti-Detection: Disabled
Use Case: Games with reaction time
```

### Pattern 2: Slow, Stealthy

```
Interval: 2000-5000 ms (2-5 seconds)
Anti-Detection: Enabled (10px)
Use Case: Avoiding detection
```

### Pattern 3: Balanced

```
Interval: 500-1000 ms (0.5-1 second)
Anti-Detection: Enabled (5px)
Use Case: Most games and web apps
```

### Pattern 4: Double-Click Heavy

```
Click Type: Double Click
Interval: 300 ms (per double-click)
Use Case: Menu navigation, text selection
```

---

## Troubleshooting Examples

### Issue: Clicks Not Registering

**Check Your Setup:**
1. Click "Get Mouse Position"
2. Move to target and click the button
3. Note the coordinates displayed
4. Use those coordinates

**Example:**
```
Current position: (487, 312)
Enter: X=487, Y=312
```

### Issue: Offset Too Large

**Symptom:** Clicks landing too far from target

**Fix:**
```
Old: Anti-Detection Offset = 10
New: Anti-Detection Offset = 2
```

Test with smaller offsets first.

### Issue: Interval Too Fast

**Symptom:** Missing clicks or jittery behavior

**Fix:**
```
Old: Interval = 50 ms
New: Interval = 200 ms
```

Slower is more reliable.

---

## Performance Notes

### Expected Speeds

| Interval | Clicks/Sec | Notes |
|----------|-----------|-------|
| 50ms     | 20/s      | Maximum speed, may miss |
| 100ms    | 10/s      | Very fast, reliable |
| 250ms    | 4/s       | Typical gaming |
| 500ms    | 2/s       | Slow, safe |
| 1000ms   | 1/s       | Very slow, stealthy |

### CPU Usage

- **Idle**: <1%
- **Clicking**: 1-3%
- **With Anti-Detection**: 3-5%

### Memory Usage

- **App**: ~30-50 MB
- **Per configuration**: <1 KB

---

## Tips & Tricks

### Tip 1: Find Exact Coordinates
Use "Get Mouse Position" button to capture exact pixel location of target button or area.

### Tip 2: Test Before Running
- Set Stop Condition to 1 cycle
- Click START
- Watch for success
- Then increase cycles

### Tip 3: Save After Testing
Once configuration works, click "Save Config" to store it permanently.

### Tip 4: Use Meaningful Names
```
Good: "Game - Forest Farm Click"
Bad: "config1"
```

### Tip 5: Export Backups
Before major changes, export your configurations as CSV backup files.

### Tip 6: Monitor First Run
Watch the first 10 seconds to ensure clicks are landing correctly.

### Tip 7: Use Pause When Needed
Click PAUSE to halt, fix something, then PAUSE again to resume.

### Tip 8: Anti-Detection for Games
Always enable anti-detection when automating actual games to reduce detection risk.

---

## Responsible Use

- Use only on games/apps you own
- Check Terms of Service
- Don't distribute automation configs
- Use for legitimate automation only
- Stop if account shows warnings
- Respect other players

---

For more information, see:
- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
- [API.md](API.md) - Developer API reference
