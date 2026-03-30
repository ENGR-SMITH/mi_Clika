# Hybrid Single Target Clicker - API Reference

Complete developer API documentation for integrating Hybrid Clicker components.

## Quick API Overview

```python
from src.click_engine import ClickEngine, StopCondition, ClickType
from src.config import get_config_manager, ClickTarget, ClickSettings

# Initialize
engine = ClickEngine()
config = get_config_manager()

# Configure
engine.configure(
    x_pos=500,
    y_pos=300,
    click_interval=250,
    stop_condition=StopCondition.CYCLES_BASED,
    stop_value=100,
    anti_detection=True,
    click_type=ClickType.SINGLE_CLICK
)

# Run
engine.start_clicking()
```

---

## Click Engine API

### Class: `ClickEngine`

The core automation engine.

```python
from src.click_engine import ClickEngine, StopCondition, ClickType
```

#### Constructor

```python
engine = ClickEngine(use_dummy=False)
```

**Parameters:**
- `use_dummy` (bool, default=False) - If True, simulate clicks without actually moving mouse

#### Configuration

```python
engine.configure(
    x_pos: int,
    y_pos: int,
    click_interval: int,
    stop_condition: StopCondition,
    stop_value: int,
    anti_detection: bool = False,
    click_type: ClickType = ClickType.SINGLE_CLICK
)
```

**Parameters:**
- `x_pos` - X coordinate of target
- `y_pos` - Y coordinate of target
- `click_interval` - Milliseconds between clicks (min: 1)
- `stop_condition` - When to stop (see StopCondition enum)
- `stop_value` - Time (seconds) or cycles count
- `anti_detection` - Enable randomization
- `click_type` - Type of click to perform

**Example:**
```python
engine.configure(
    x_pos=500,
    y_pos=300,
    click_interval=500,
    stop_condition=StopCondition.TIME_BASED,
    stop_value=60,
    anti_detection=True,
    click_type=ClickType.SINGLE_CLICK
)
```

#### Control Methods

```python
# Start automated clicking
success: bool = engine.start_clicking()

# Stop clicking
success: bool = engine.stop_clicking()

# Pause without stopping
success: bool = engine.pause_clicking()

# Resume from pause
success: bool = engine.resume_clicking()
```

**Returns:**
- `bool` - True if operation successful, False if invalid state

**Example:**
```python
if engine.start_clicking():
    print("Clicking started")
else:
    print("Already clicking or invalid config")
```

#### Status Methods

```python
# Get current statistics
stats: ClickStats = engine.get_stats()

# Reset statistics
engine.reset_stats()

# Check if currently clicking
is_clicking: bool = engine.is_clicking()

# Check if paused
is_paused: bool = engine.is_paused_state()
```

**Example:**
```python
while engine.is_clicking():
    stats = engine.get_stats()
    print(f"Clicks: {stats.total_clicks}, Elapsed: {stats.elapsed_time:.1f}s")
    time.sleep(1)
```

#### Callbacks

```python
# Called when click occurs
engine.set_on_click_callback(callback_fn)

# Called periodically (~100ms)
engine.set_on_tick_callback(callback_fn)

# Called when automation stops
engine.set_on_stop_callback(callback_fn)
```

**Callback Parameters:**

`on_click` callback receives dict:
```python
{
    'x': int,              # Actual X clicked
    'y': int,              # Actual Y clicked
    'total_clicks': int,   # Total clicks so far
    'timestamp': float     # Unix timestamp
}
```

`on_tick` callback receives dict:
```python
{
    'elapsed': float,      # Seconds elapsed
    'total_clicks': int    # Total clicks so far
}
```

`on_stop` callback receives dict:
```python
{
    'total_clicks': int,    # Final click count
    'elapsed_time': float,  # Total seconds
    'reason': str          # 'stop_condition' or 'user_stopped'
}
```

**Example:**
```python
def on_click(data):
    print(f"Click #{data['total_clicks']} at ({data['x']}, {data['y']})")

def on_stop(data):
    print(f"Stopped: {data['total_clicks']} clicks in {data['elapsed_time']:.1f}s")

engine.set_on_click_callback(on_click)
engine.set_on_stop_callback(on_stop)
```

#### Statistics Data

```python
from dataclasses import dataclass

@dataclass
class ClickStats:
    total_clicks: int = 0      # Number of clicks
    elapsed_time: float = 0.0  # Seconds elapsed
    start_time: float = 0.0    # Unix timestamp of start
    cycles_completed: int = 0  # Completed cycles
```

**Access example:**
```python
stats = engine.get_stats()
print(f"Total clicks: {stats.total_clicks}")
print(f"Elapsed: {stats.elapsed_time:.1f} seconds")
print(f"Started: {time.ctime(stats.start_time)}")
```

#### Advanced Properties

```python
# Anti-detection offset in pixels
engine.anti_detection_offset = 5

# Current configuration
engine.x_pos = 500
engine.y_pos = 300
engine.click_interval = 250
engine.stop_condition = StopCondition.INDEFINITE
engine.stop_value = 0
```

---

## Enumerations

### StopCondition

```python
from src.click_engine import StopCondition

class StopCondition(Enum):
    INDEFINITE = 0      # Run forever
    TIME_BASED = 1      # Stop after N seconds
    CYCLES_BASED = 2    # Stop after N clicks
```

**Usage:**
```python
# Run indefinitely
engine.configure(..., stop_condition=StopCondition.INDEFINITE)

# Stop after 60 seconds
engine.configure(..., stop_condition=StopCondition.TIME_BASED, stop_value=60)

# Stop after 1000 clicks
engine.configure(..., stop_condition=StopCondition.CYCLES_BASED, stop_value=1000)
```

### ClickType

```python
from src.click_engine import ClickType

class ClickType(Enum):
    SINGLE_CLICK = 0    # Single left click
    DOUBLE_CLICK = 1    # Two rapid clicks
    RIGHT_CLICK = 2     # Right mouse button
```

**Usage:**
```python
engine.configure(..., click_type=ClickType.DOUBLE_CLICK)
```

---

## Configuration Manager API

### Class: `ConfigManager`

Manages CSV-based configuration storage.

```python
from src.config import get_config_manager, ConfigManager

config = get_config_manager()  # Singleton instance
# or
config = ConfigManager(data_dir="/custom/path")
```

#### Save/Load Targets

```python
# Save a configuration
success: bool = config.save_target(target: ClickTarget)

# Load all configurations
targets: List[ClickTarget] = config.load_all_targets()

# Get specific target
target: Optional[ClickTarget] = config.get_target_by_id(target_id: int)

# Delete target
success: bool = config.delete_target(target_id: int)

# Get next available ID
next_id: int = config.get_next_target_id()
```

**Example:**
```python
from src.config import ClickTarget

target = ClickTarget(
    id=1,
    name="Game Clicker",
    x_pos=500,
    y_pos=300,
    click_interval=250,
    stop_condition=2,        # 0=inf, 1=time, 2=cycles
    stop_value=100,
    anti_detection=True
)

if config.save_target(target):
    print("Saved successfully")

# Load all
all_targets = config.load_all_targets()
for t in all_targets:
    print(f"{t.name}: ({t.x_pos}, {t.y_pos})")
```

#### Import/Export

```python
# Export single target to CSV
success: bool = config.export_target_to_csv(
    target_id: int,
    output_file: str
)

# Import target from CSV
success: bool = config.import_target_from_csv(
    input_file: str
)
```

**Example:**
```python
# Export
config.export_target_to_csv(1, "backup.csv")

# Import
config.import_target_from_csv("backup.csv")
```

#### Settings Management

```python
# Save settings
success: bool = config.save_settings(settings: ClickSettings)

# Load settings
settings: ClickSettings = config.load_settings()
```

**Example:**
```python
from src.config import ClickSettings

settings = ClickSettings(
    click_interval=500,
    stop_condition=0,
    anti_detection=True,
    anti_detection_max_offset=5
)

config.save_settings(settings)

# Load
loaded = config.load_settings()
print(f"Interval: {loaded.click_interval}ms")
```

#### Utility Methods

```python
# Get data directory path
data_dir: str = config.get_data_dir()

# Get targets CSV file path
csv_path: str = config.get_targets_file_path()
```

---

## Data Models

### ClickTarget

Represents a saved configuration.

```python
from dataclasses import dataclass

@dataclass
class ClickTarget:
    id: int                    # Unique identifier
    name: str                  # Configuration name
    x_pos: int                 # X coordinate
    y_pos: int                 # Y coordinate
    click_interval: int        # Milliseconds
    stop_condition: int        # 0=inf, 1=time, 2=cycles
    stop_value: int            # Duration or count
    anti_detection: bool = False
    is_active: bool = True
```

### ClickSettings

Represents application settings.

```python
@dataclass
class ClickSettings:
    click_interval: int = 500
    stop_condition: int = 0
    stop_value: int = 0
    anti_detection: bool = False
    anti_detection_max_offset: int = 5
```

---

## Complete Example

```python
#!/usr/bin/env python3
"""
Example: Automate 1000 clicks at (500, 300) with anti-detection
"""

from src.click_engine import ClickEngine, StopCondition, ClickType
from src.config import get_config_manager, ClickTarget
import time

def on_click(data):
    """Called after each click"""
    if data['total_clicks'] % 100 == 0:
        print(f"Progress: {data['total_clicks']} clicks")

def on_stop(data):
    """Called when automation stops"""
    print(f"\nAutomation complete!")
    print(f"Total clicks: {data['total_clicks']}")
    print(f"Elapsed time: {data['elapsed_time']:.2f} seconds")
    print(f"Average: {data['total_clicks'] / data['elapsed_time']:.1f} clicks/sec")

# Initialize
engine = ClickEngine()
config = get_config_manager()

# Configure
engine.configure(
    x_pos=500,
    y_pos=300,
    click_interval=250,
    stop_condition=StopCondition.CYCLES_BASED,
    stop_value=1000,
    anti_detection=True,
    click_type=ClickType.SINGLE_CLICK
)
engine.anti_detection_offset = 5

# Setup callbacks
engine.set_on_click_callback(on_click)
engine.set_on_stop_callback(on_stop)

# Save configuration
target = ClickTarget(
    id=config.get_next_target_id(),
    name="Example 1000 Clicks",
    x_pos=500,
    y_pos=300,
    click_interval=250,
    stop_condition=2,
    stop_value=1000,
    anti_detection=True
)
config.save_target(target)
print(f"Configuration saved: {target.name}")

# Start automation
print("Starting automation...")
engine.start_clicking()

# Wait for completion
while engine.is_clicking():
    time.sleep(1)

print("Done!")
```

---

## Testing

### Dummy Mode

Test without actual clicks:

```python
engine = ClickEngine(use_dummy=True)
engine.configure(500, 300, 100, StopCondition.CYCLES_BASED, 10)
engine.start_clicking()  # Simulates without moving mouse
```

### Programmatic Testing

```python
import time

engine = ClickEngine(use_dummy=True)
engine.configure(500, 300, 100, StopCondition.CYCLES_BASED, 10)

stats = engine.get_stats()
assert stats.total_clicks == 0

engine.start_clicking()
time.sleep(2)

assert engine.is_clicking()

engine.stop_clicking()
assert not engine.is_clicking()

final_stats = engine.get_stats()
assert final_stats.total_clicks > 0
```

---

## File Format Reference

### CSV Format (targets.csv)

```csv
id,name,x_pos,y_pos,click_interval,stop_condition,stop_value,anti_detection,is_active
1,"Game Click",500,300,250,2,1000,true,true
2,"Web Form",100,200,500,1,60,false,true
3,"Test Click",0,0,100,0,0,false,true
```

**Fields:**
- `id` - Unique integer
- `name` - String (may contain commas if quoted)
- `x_pos` - Integer
- `y_pos` - Integer
- `click_interval` - Integer (milliseconds)
- `stop_condition` - 0, 1, or 2
- `stop_value` - Integer
- `anti_detection` - "true" or "false"
- `is_active` - "true" or "false"

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

## Performance Tips

1. **Callback Overhead**
   - Keep callbacks lightweight
   - Don't perform heavy I/O in callbacks

2. **Optimal Intervals**
   - Minimum: 50ms (may cause lag)
   - Normal: 100-500ms
   - Safe: 250ms+

3. **Anti-Detection Cost**
   - Adds ~5-10% CPU overhead
   - Only enable if needed

4. **Large Cycles**
   - 1000+ cycles: Use time-based for better control
   - Consider breaking into multiple runs

---

## Common Patterns

### Pattern 1: Click Until Event

```python
def on_stop(data):
    if should_continue():
        engine.start_clicking()

engine.set_on_stop_callback(on_stop)
engine.start_clicking()
```

### Pattern 2: Multiple Sequences

```python
targets = config.load_all_targets()
for target in targets:
    engine.configure(
        target.x_pos,
        target.y_pos,
        target.click_interval,
        # ... etc
    )
    engine.start_clicking()
    while engine.is_clicking():
        time.sleep(0.1)
```

### Pattern 3: Adaptive Intervals

```python
def on_tick(data):
    if data['elapsed'] > 10:
        engine.click_interval = 300  # Slow down after 10s
    elif data['elapsed'] > 30:
        engine.click_interval = 100  # Speed up after 30s

engine.set_on_tick_callback(on_tick)
```

---

## Troubleshooting

### Clicks Not Registering

Check coordinates:
```python
import pyautogui
x, y = pyautogui.position()
print(f"Current mouse: {x}, {y}")
```

### Performance Issues

Monitor stats:
```python
stats = engine.get_stats()
clicks_per_sec = stats.total_clicks / max(stats.elapsed_time, 1)
print(f"Performance: {clicks_per_sec:.1f} clicks/sec")
```

### Configuration Not Saving

Verify path:
```python
import os
path = config.get_data_dir()
print(f"Data dir: {path}")
print(f"Writable: {os.access(path, os.W_OK)}")
```

---

## Version Compatibility

- **Python:** 3.7+
- **pyautogui:** 0.9.53+
- **tkinter:** Built-in

---

For more information, see `ARCHITECTURE.md` and `QUICKSTART.md`
