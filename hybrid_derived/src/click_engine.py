"""
Click Engine Module - Handles mouse click simulation on Windows
Pure local automation, no external services
"""

import time
import threading
import random
from enum import Enum
from typing import Callable, Optional
from dataclasses import dataclass

# Platform-specific mouse control
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import mouse
    MOUSE_AVAILABLE = True
except ImportError:
    MOUSE_AVAILABLE = False


class ClickType(Enum):
    """Types of mouse interactions"""
    SINGLE_CLICK = 0
    DOUBLE_CLICK = 1
    RIGHT_CLICK = 2


class StopCondition(Enum):
    """Stop conditions for clicking"""
    INDEFINITE = 0
    TIME_BASED = 1
    CYCLES_BASED = 2


@dataclass
class ClickStats:
    """Statistics for a clicking session"""
    total_clicks: int = 0
    elapsed_time: float = 0.0
    start_time: float = 0.0
    cycles_completed: int = 0


class ClickEngine:
    """
    Handles mouse click simulation on Windows/Linux/Mac
    Uses pyautogui for cross-platform compatibility
    """
    
    def __init__(self, use_dummy: bool = False):
        """
        Initialize click engine
        
        Args:
            use_dummy: If True, simulate clicks without actually moving mouse
                      (useful for testing/demo)
        """
        self.is_running = False
        self.is_paused = False
        self.use_dummy = use_dummy
        
        self.click_thread = None
        self.stats = ClickStats()
        
        # Callbacks
        self.on_click_callback = None
        self.on_stop_callback = None
        self.on_tick_callback = None
        
        # Current configuration
        self.x_pos = 0
        self.y_pos = 0
        self.click_interval = 500  # ms
        self.stop_condition = StopCondition.INDEFINITE
        self.stop_value = 0
        self.anti_detection = False
        self.anti_detection_offset = 5
        self.click_type = ClickType.SINGLE_CLICK
    
    def _check_pyautogui(self) -> bool:
        """Check if pyautogui is available"""
        if not PYAUTOGUI_AVAILABLE:
            print("Warning: pyautogui not installed. Install with: pip install pyautogui")
            return False
        return True
    
    def _get_click_position(self) -> tuple:
        """Get actual click position with optional anti-detection offset"""
        x, y = self.x_pos, self.y_pos
        
        if self.anti_detection:
            # Add random offset
            offset_x = random.randint(-self.anti_detection_offset, self.anti_detection_offset)
            offset_y = random.randint(-self.anti_detection_offset, self.anti_detection_offset)
            x += offset_x
            y += offset_y
            
            # Ensure position stays within reasonable bounds
            x = max(0, min(x, 65535))
            y = max(0, min(y, 65535))
        
        return x, y
    
    def _perform_click(self):
        """Perform a single click at the configured position"""
        if self.use_dummy:
            # Dummy mode - just log the click
            x, y = self._get_click_position()
            print(f"[DUMMY] Click at ({x}, {y})")
            self.stats.total_clicks += 1
            return
        
        try:
            x, y = self._get_click_position()
            
            print(f"[CLICK] Attempting click at ({x}, {y}) - Type: {self.click_type.name}")
            
            # Try pyautogui first
            if PYAUTOGUI_AVAILABLE:
                try:
                    pyautogui.FAILSAFE = False
                    pyautogui.PAUSE = 0.05
                    
                    # Move to position first
                    pyautogui.moveTo(x, y, duration=0.1)
                    
                    # Perform the click
                    if self.click_type == ClickType.SINGLE_CLICK:
                        pyautogui.mouseDown()
                        time.sleep(0.05)
                        pyautogui.mouseUp()
                    elif self.click_type == ClickType.DOUBLE_CLICK:
                        pyautogui.mouseDown()
                        time.sleep(0.05)
                        pyautogui.mouseUp()
                        time.sleep(0.05)
                        pyautogui.mouseDown()
                        time.sleep(0.05)
                        pyautogui.mouseUp()
                    elif self.click_type == ClickType.RIGHT_CLICK:
                        pyautogui.mouseDown(button='right')
                        time.sleep(0.05)
                        pyautogui.mouseUp(button='right')
                    
                    print(f"[CLICK] ✓ Click succeeded via pyautogui at ({x}, {y})")
                    self.stats.total_clicks += 1
                    
                    # Trigger callback
                    if self.on_click_callback:
                        self.on_click_callback({
                            'x': x,
                            'y': y,
                            'total_clicks': self.stats.total_clicks,
                            'timestamp': time.time()
                        })
                    return
                
                except Exception as e:
                    print(f"[WARNING] pyautogui failed: {e}, trying mouse library...")
            
            # Fallback to mouse library
            if MOUSE_AVAILABLE:
                try:
                    # Move and click using mouse library
                    mouse.move(x, y, duration=0.1)
                    
                    if self.click_type == ClickType.SINGLE_CLICK:
                        mouse.click()
                    elif self.click_type == ClickType.DOUBLE_CLICK:
                        mouse.click()
                        time.sleep(0.05)
                        mouse.click()
                    elif self.click_type == ClickType.RIGHT_CLICK:
                        mouse.click(button='right')
                    
                    print(f"[CLICK] ✓ Click succeeded via mouse library at ({x}, {y})")
                    self.stats.total_clicks += 1
                    
                    # Trigger callback
                    if self.on_click_callback:
                        self.on_click_callback({
                            'x': x,
                            'y': y,
                            'total_clicks': self.stats.total_clicks,
                            'timestamp': time.time()
                        })
                    return
                
                except Exception as e:
                    print(f"[ERROR] mouse library failed: {e}")
            
            print("[ERROR] No mouse control library available!")
        
        except Exception as e:
            print(f"[ERROR] Click failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_actual_interval(self) -> float:
        """Get click interval with optional random variation"""
        interval = self.click_interval / 1000.0  # Convert to seconds
        
        if self.anti_detection:
            # Add ±10% variation to interval
            variation = interval * 0.1
            interval += random.uniform(-variation, variation)
        
        return max(0.001, interval)  # Minimum 1ms
    
    def _check_stop_condition(self) -> bool:
        """Check if stop condition is met, return True if should stop"""
        if self.stop_condition == StopCondition.INDEFINITE:
            return False
        
        elif self.stop_condition == StopCondition.TIME_BASED:
            elapsed = time.time() - self.stats.start_time
            if elapsed >= self.stop_value:
                return True
        
        elif self.stop_condition == StopCondition.CYCLES_BASED:
            if self.stats.total_clicks >= self.stop_value:
                return True
        
        return False
    
    def _click_loop(self):
        """Main clicking loop running in separate thread"""
        self.stats.start_time = time.time()
        self.stats.total_clicks = 0
        self.stats.cycles_completed = 0
        
        # Initialize pyautogui settings
        if PYAUTOGUI_AVAILABLE:
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0.01  # Small pause between pyautogui calls
        
        try:
            while self.is_running:
                # Handle pause
                if self.is_paused:
                    time.sleep(0.1)
                    continue
                
                # Perform click
                self._perform_click()
                
                # Check stop condition
                if self._check_stop_condition():
                    break
                
                # Wait for next click
                interval = self._get_actual_interval()
                
                # Sleep in small increments to allow pause/stop
                sleep_time = interval
                while sleep_time > 0 and self.is_running and not self.is_paused:
                    sleep_chunk = min(sleep_time, 0.1)
                    time.sleep(sleep_chunk)
                    sleep_time -= sleep_chunk
                    
                    # Trigger tick callback
                    if self.on_tick_callback:
                        self.on_tick_callback({
                            'elapsed': time.time() - self.stats.start_time,
                            'total_clicks': self.stats.total_clicks
                        })
        
        finally:
            self.is_running = False
            self.stats.elapsed_time = time.time() - self.stats.start_time
            
            # Trigger stop callback
            if self.on_stop_callback:
                self.on_stop_callback({
                    'total_clicks': self.stats.total_clicks,
                    'elapsed_time': self.stats.elapsed_time,
                    'reason': 'stop_condition' if self._check_stop_condition() else 'user_stopped'
                })
    
    def start_clicking(self) -> bool:
        """Start the clicking loop"""
        if self.is_running:
            print("Clicking already in progress")
            return False
        
        self.is_running = True
        self.is_paused = False
        
        self.click_thread = threading.Thread(target=self._click_loop, daemon=True)
        self.click_thread.start()
        
        return True
    
    def stop_clicking(self) -> bool:
        """Stop the clicking loop"""
        if not self.is_running:
            return False
        
        self.is_running = False
        
        if self.click_thread:
            self.click_thread.join(timeout=2.0)
        
        return True
    
    def pause_clicking(self) -> bool:
        """Pause the clicking loop"""
        if not self.is_running:
            return False
        
        self.is_paused = True
        return True
    
    def resume_clicking(self) -> bool:
        """Resume the paused clicking loop"""
        if not self.is_running:
            return False
        
        self.is_paused = False
        return True
    
    def configure(self,
                  x_pos: int,
                  y_pos: int,
                  click_interval: int,
                  stop_condition: StopCondition,
                  stop_value: int,
                  anti_detection: bool = False,
                  click_type: ClickType = ClickType.SINGLE_CLICK):
        """Configure the click engine"""
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.click_interval = max(1, click_interval)  # Minimum 1ms
        self.stop_condition = stop_condition
        self.stop_value = stop_value
        self.anti_detection = anti_detection
        self.click_type = click_type
    
    def get_stats(self) -> ClickStats:
        """Get current clicking statistics"""
        if self.is_running:
            self.stats.elapsed_time = time.time() - self.stats.start_time
        return self.stats
    
    def reset_stats(self):
        """Reset clicking statistics"""
        self.stats = ClickStats()
    
    def set_on_click_callback(self, callback: Callable):
        """Set callback for each click"""
        self.on_click_callback = callback
    
    def set_on_stop_callback(self, callback: Callable):
        """Set callback for when clicking stops"""
        self.on_stop_callback = callback
    
    def set_on_tick_callback(self, callback: Callable):
        """Set callback for periodic updates (every 100ms)"""
        self.on_tick_callback = callback
    
    def is_clicking(self) -> bool:
        """Check if currently clicking"""
        return self.is_running and not self.is_paused
    
    def is_paused_state(self) -> bool:
        """Check if clicking is paused"""
        return self.is_paused
