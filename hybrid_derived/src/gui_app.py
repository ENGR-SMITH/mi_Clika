"""
Hybrid Single Target Click Automation App for Windows/Linux/Mac
Pure local automation - No Firebase, No ads, No external monitoring
Uses CSV for configuration storage
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config_manager, ClickTarget, ClickSettings
from click_engine import ClickEngine, StopCondition, ClickType


class HybridClickerApp:
    """Main application class with tkinter GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Hybrid Single Target Clicker")
        self.root.geometry("500x700")
        self.root.resizable(False, False)
        
        # Initialize components
        self.config_manager = get_config_manager()
        self.click_engine = ClickEngine(use_dummy=False)
        
        # Setup callbacks
        self.click_engine.set_on_click_callback(self._on_click)
        self.click_engine.set_on_stop_callback(self._on_stop)
        self.click_engine.set_on_tick_callback(self._on_tick)
        
        # Load saved settings
        self.settings = self.config_manager.load_settings()
        
        # Build UI
        self._build_ui()
        
        # Status message
        self.status_message = "Ready"
    
    def _build_ui(self):
        """Build the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Single Target Mode", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # --- Target Position Section ---
        position_frame = ttk.LabelFrame(main_frame, text="Target Position", padding="10")
        position_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(position_frame, text="X Position:").grid(row=0, column=0, sticky=tk.W)
        self.x_var = tk.StringVar(value="0")
        ttk.Entry(position_frame, textvariable=self.x_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(position_frame, text="Y Position:").grid(row=1, column=0, sticky=tk.W)
        self.y_var = tk.StringVar(value="0")
        ttk.Entry(position_frame, textvariable=self.y_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Button(position_frame, text="Get Mouse Position", 
                  command=self._get_mouse_position).grid(row=0, column=2, padx=5)
        
        # --- Click Settings Section ---
        settings_frame = ttk.LabelFrame(main_frame, text="Click Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(settings_frame, text="Click Interval (ms):").grid(row=0, column=0, sticky=tk.W)
        self.interval_var = tk.StringVar(value=str(self.settings.click_interval))
        ttk.Entry(settings_frame, textvariable=self.interval_var, width=15).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(settings_frame, text="Click Type:").grid(row=1, column=0, sticky=tk.W)
        self.click_type_var = tk.StringVar(value="Single Click")
        click_type_combo = ttk.Combobox(settings_frame, textvariable=self.click_type_var, 
                                       values=["Single Click", "Double Click", "Right Click"], 
                                       state="readonly", width=12)
        click_type_combo.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # --- Stop Condition Section ---
        stop_frame = ttk.LabelFrame(main_frame, text="Stop Condition", padding="10")
        stop_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.stop_condition_var = tk.StringVar(value="Indefinite")
        
        ttk.Radiobutton(stop_frame, text="Run Indefinitely", 
                       variable=self.stop_condition_var, value="Indefinite",
                       command=self._update_stop_ui).pack(anchor=tk.W)
        
        ttk.Radiobutton(stop_frame, text="Stop After Time (seconds)", 
                       variable=self.stop_condition_var, value="Time",
                       command=self._update_stop_ui).pack(anchor=tk.W)
        
        ttk.Radiobutton(stop_frame, text="Stop After Cycles", 
                       variable=self.stop_condition_var, value="Cycles",
                       command=self._update_stop_ui).pack(anchor=tk.W)
        
        time_frame = ttk.Frame(stop_frame)
        time_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(time_frame, text="Value:").pack(side=tk.LEFT, padx=20)
        self.stop_value_var = tk.StringVar(value="60")
        ttk.Entry(time_frame, textvariable=self.stop_value_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # --- Anti-Detection ---
        anti_frame = ttk.LabelFrame(main_frame, text="Advanced Options", padding="10")
        anti_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.anti_detection_var = tk.BooleanVar(value=self.settings.anti_detection)
        ttk.Checkbutton(anti_frame, text="Enable Anti-Detection (random offsets)", 
                       variable=self.anti_detection_var).pack(anchor=tk.W)
        
        ttk.Label(anti_frame, text="Anti-Detection Offset (pixels):").pack(anchor=tk.W)
        self.offset_var = tk.StringVar(value=str(self.settings.anti_detection_max_offset))
        ttk.Entry(anti_frame, textvariable=self.offset_var, width=10).pack(anchor=tk.W, padx=20)
        
        # --- Control Buttons ---
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        
        self.start_button = ttk.Button(control_frame, text="START", command=self._start_clicking)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="STOP", command=self._stop_clicking, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = ttk.Button(control_frame, text="PAUSE", command=self._pause_clicking, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        # --- Statistics ---
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(stats_frame, text="Clicks:").grid(row=0, column=0, sticky=tk.W)
        self.clicks_label = ttk.Label(stats_frame, text="0", foreground="blue")
        self.clicks_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(stats_frame, text="Elapsed Time:").grid(row=1, column=0, sticky=tk.W)
        self.elapsed_label = ttk.Label(stats_frame, text="0s", foreground="blue")
        self.elapsed_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(stats_frame, text="Status:").grid(row=2, column=0, sticky=tk.W)
        self.status_label = ttk.Label(stats_frame, text="Ready", foreground="green")
        self.status_label.grid(row=2, column=1, sticky=tk.W)
        
        # --- Configuration Buttons ---
        config_frame = ttk.Frame(main_frame)
        config_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(config_frame, text="Save Config", command=self._save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(config_frame, text="Load Config", command=self._load_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(config_frame, text="Export", command=self._export_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(config_frame, text="Import", command=self._import_config).pack(side=tk.LEFT, padx=5)
        
        # --- Info Label ---
        info_label = ttk.Label(main_frame, text="Version 1.0 | No Firebase | CSV Storage | Local Only", 
                              font=("Arial", 8), foreground="gray")
        info_label.grid(row=8, column=0, columnspan=2, pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        self._update_stop_ui()
    
    def _update_stop_ui(self):
        """Update stop UI based on selected condition"""
        condition = self.stop_condition_var.get()
        if condition == "Indefinite":
            self.stop_value_var.config(state=tk.DISABLED)
        else:
            self.stop_value_var.config(state=tk.NORMAL)
    
    def _get_mouse_position(self):
        """Get current mouse position"""
        try:
            import pyautogui
            x, y = pyautogui.position()
            self.x_var.set(str(x))
            self.y_var.set(str(y))
            messagebox.showinfo("Success", f"Position captured: ({x}, {y})")
        except ImportError:
            messagebox.showerror("Error", "pyautogui not installed. Install with: pip install pyautogui")
    
    def _validate_inputs(self) -> bool:
        """Validate user inputs"""
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            interval = int(self.interval_var.get())
            offset = int(self.offset_var.get())
            stop_value = int(self.stop_value_var.get()) if self.stop_condition_var.get() != "Indefinite" else 0
            
            if interval < 1:
                messagebox.showerror("Error", "Click interval must be at least 1ms")
                return False
            
            if offset < 0:
                messagebox.showerror("Error", "Anti-detection offset cannot be negative")
                return False
            
            if self.stop_condition_var.get() != "Indefinite" and stop_value < 1:
                messagebox.showerror("Error", "Stop value must be at least 1")
                return False
            
            return True
        except ValueError:
            messagebox.showerror("Error", "Invalid input values")
            return False
    
    def _start_clicking(self):
        """Start the clicking automation"""
        if not self._validate_inputs():
            return
        
        # Get values
        x = int(self.x_var.get())
        y = int(self.y_var.get())
        interval = int(self.interval_var.get())
        offset = int(self.offset_var.get())
        anti_detection = self.anti_detection_var.get()
        
        # Determine stop condition
        stop_condition = {
            "Indefinite": StopCondition.INDEFINITE,
            "Time": StopCondition.TIME_BASED,
            "Cycles": StopCondition.CYCLES_BASED
        }[self.stop_condition_var.get()]
        
        stop_value = 0
        if stop_condition == StopCondition.TIME_BASED:
            stop_value = int(self.stop_value_var.get())
        elif stop_condition == StopCondition.CYCLES_BASED:
            stop_value = int(self.stop_value_var.get())
        
        # Determine click type
        click_type_map = {
            "Single Click": ClickType.SINGLE_CLICK,
            "Double Click": ClickType.DOUBLE_CLICK,
            "Right Click": ClickType.RIGHT_CLICK
        }
        click_type = click_type_map[self.click_type_var.get()]
        
        # Configure engine
        self.click_engine.configure(
            x_pos=x,
            y_pos=y,
            click_interval=interval,
            stop_condition=stop_condition,
            stop_value=stop_value,
            anti_detection=anti_detection,
            click_type=click_type
        )
        self.click_engine.anti_detection_offset = offset
        
        # Update UI
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)
        self.status_label.config(text="Running...", foreground="green")
        
        # Start clicking
        self.click_engine.start_clicking()
    
    def _stop_clicking(self):
        """Stop the clicking automation"""
        self.click_engine.stop_clicking()
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped", foreground="red")
    
    def _pause_clicking(self):
        """Pause/Resume clicking"""
        if self.click_engine.is_paused_state():
            self.click_engine.resume_clicking()
            self.pause_button.config(text="PAUSE")
            self.status_label.config(text="Running...", foreground="green")
        else:
            self.click_engine.pause_clicking()
            self.pause_button.config(text="RESUME")
            self.status_label.config(text="Paused", foreground="orange")
    
    def _on_click(self, data):
        """Callback when a click is performed"""
        self.clicks_label.config(text=str(data['total_clicks']))
    
    def _on_tick(self, data):
        """Callback for periodic updates"""
        elapsed = int(data['elapsed'])
        self.elapsed_label.config(text=f"{elapsed}s")
    
    def _on_stop(self, data):
        """Callback when clicking stops"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.pause_button.config(text="PAUSE")
        
        total_clicks = data['total_clicks']
        elapsed = f"{data['elapsed_time']:.1f}s"
        
        self.status_label.config(text=f"Completed: {total_clicks} clicks in {elapsed}", foreground="blue")
        messagebox.showinfo("Automation Complete", f"Total Clicks: {total_clicks}\nElapsed Time: {elapsed}")
    
    def _save_config(self):
        """Save current configuration"""
        name = self._get_config_name("Save Configuration")
        if not name:
            return
        
        try:
            target = ClickTarget(
                id=self.config_manager.get_next_target_id(),
                name=name,
                x_pos=int(self.x_var.get()),
                y_pos=int(self.y_var.get()),
                click_interval=int(self.interval_var.get()),
                stop_condition={
                    "Indefinite": 0,
                    "Time": 1,
                    "Cycles": 2
                }[self.stop_condition_var.get()],
                stop_value=int(self.stop_value_var.get()) if self.stop_condition_var.get() != "Indefinite" else 0,
                anti_detection=self.anti_detection_var.get()
            )
            
            if self.config_manager.save_target(target):
                messagebox.showinfo("Success", f"Configuration saved: {name}")
            else:
                messagebox.showerror("Error", "Failed to save configuration")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving: {str(e)}")
    
    def _load_config(self):
        """Load a saved configuration"""
        targets = self.config_manager.load_all_targets()
        if not targets:
            messagebox.showwarning("No Configs", "No saved configurations found")
            return
        
        # Create selection dialog
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Load Configuration")
        selection_window.geometry("300x400")
        
        ttk.Label(selection_window, text="Select Configuration:", font=("Arial", 10, "bold")).pack(pady=10)
        
        listbox = tk.Listbox(selection_window, height=15)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for target in targets:
            listbox.insert(tk.END, f"{target.name} (X:{target.x_pos}, Y:{target.y_pos})")
        
        def load_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Error", "Please select a configuration")
                return
            
            target = targets[selection[0]]
            self.x_var.set(str(target.x_pos))
            self.y_var.set(str(target.y_pos))
            self.interval_var.set(str(target.click_interval))
            self.anti_detection_var.set(target.anti_detection)
            
            stop_cond = ["Indefinite", "Time", "Cycles"][target.stop_condition]
            self.stop_condition_var.set(stop_cond)
            self.stop_value_var.set(str(target.stop_value))
            
            self._update_stop_ui()
            selection_window.destroy()
            messagebox.showinfo("Success", f"Loaded: {target.name}")
        
        ttk.Button(selection_window, text="Load", command=load_selected).pack(pady=10)
    
    def _export_config(self):
        """Export current configuration to CSV"""
        try:
            target_id = self.config_manager.get_next_target_id() - 1
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")]
            )
            
            if file_path:
                # Save current config as temporary target
                temp_target = ClickTarget(
                    id=999,
                    name="Export",
                    x_pos=int(self.x_var.get()),
                    y_pos=int(self.y_var.get()),
                    click_interval=int(self.interval_var.get()),
                    stop_condition={
                        "Indefinite": 0,
                        "Time": 1,
                        "Cycles": 2
                    }[self.stop_condition_var.get()],
                    stop_value=int(self.stop_value_var.get()) if self.stop_condition_var.get() != "Indefinite" else 0,
                    anti_detection=self.anti_detection_var.get()
                )
                
                import csv
                with open(file_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        'id', 'name', 'x_pos', 'y_pos', 'click_interval',
                        'stop_condition', 'stop_value', 'anti_detection', 'is_active'
                    ])
                    writer.writeheader()
                    from dataclasses import asdict
                    writer.writerow(asdict(temp_target))
                
                messagebox.showinfo("Success", f"Configuration exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def _import_config(self):
        """Import configuration from CSV"""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            if self.config_manager.import_target_from_csv(file_path):
                messagebox.showinfo("Success", "Configuration imported successfully")
            else:
                messagebox.showerror("Error", "Failed to import configuration")
    
    def _get_config_name(self, title: str) -> str:
        """Get configuration name from user"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Configuration Name:").pack(pady=10)
        entry = ttk.Entry(dialog, width=30)
        entry.pack(pady=5)
        entry.focus()
        
        result = [None]
        
        def save():
            name = entry.get().strip()
            if not name:
                messagebox.showwarning("Error", "Please enter a name")
                return
            result[0] = name
            dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save).pack(pady=10)
        
        dialog.wait_window()
        return result[0]


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = HybridClickerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
