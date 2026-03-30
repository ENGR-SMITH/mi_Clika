"""
Main GUI Application for Hybrid Auto Clicker
Single Target Mode only - Windows/Linux/Mac compatible
No Firebase, no ads, no external monitoring
Pure local automation
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import csv
import os
from datetime import datetime
import os
import sys
from pathlib import Path
import ctypes
from ctypes import windll, wintypes
from PIL import Image, ImageGrab

from config import get_config_manager, ClickTarget, ClickSettings
from click_engine import ClickEngine, StopCondition, ClickType


class PointSelectorOverlay:
    """Draggable point selector overlay for visual coordinate selection"""
    
    def __init__(self, callback):
        """
        Initialize point selector
        
        Args:
            callback: Function to call with selected (x, y) coordinates
        """
        self.callback = callback
        self.selected_x = None
        self.selected_y = None
        
        # Create transparent overlay window
        self.overlay = tk.Tk()
        self.overlay.attributes('-alpha', 0.3)
        self.overlay.attributes('-topmost', True)
        self.overlay.geometry(f"{self.overlay.winfo_screenwidth()}x{self.overlay.winfo_screenheight()}+0+0")
        self.overlay.configure(bg='blue')
        
        # Create canvas for drawing crosshair
        self.canvas = tk.Canvas(
            self.overlay,
            bg='blue',
            highlightthickness=0,
            cursor='crosshair'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind('<Motion>', self._on_mouse_move)
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<Escape>', self._on_escape)
        
        # Draw initial instructions
        self._draw_instructions()
    
    def _draw_instructions(self):
        """Draw instructions on overlay"""
        self.canvas.delete('all')
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Instructions text
        self.canvas.create_text(
            w // 2, 30,
            text="Click on the position where you want clicks to occur",
            font=("Arial", 14, "bold"),
            fill='white'
        )
        self.canvas.create_text(
            w // 2, 60,
            text="Press ESC to cancel",
            font=("Arial", 11),
            fill='yellow'
        )
    
    def _on_mouse_move(self, event):
        """Draw crosshair at current mouse position"""
        self.canvas.delete('crosshair')
        
        # Convert canvas coordinates to absolute screen coordinates
        # event.x and event.y are relative to the canvas, so we add the canvas's screen position
        screen_x = self.canvas.winfo_rootx() + event.x
        screen_y = self.canvas.winfo_rooty() + event.y
        
        # Draw crosshair lines
        crosshair_size = 50
        self.canvas.create_line(
            event.x - crosshair_size, event.y,
            event.x + crosshair_size, event.y,
            fill='red', width=2, tags='crosshair'
        )
        self.canvas.create_line(
            event.x, event.y - crosshair_size,
            event.x, event.y + crosshair_size,
            fill='red', width=2, tags='crosshair'
        )
        
        # Draw center circle
        radius = 8
        self.canvas.create_oval(
            event.x - radius, event.y - radius,
            event.x + radius, event.y + radius,
            outline='red', width=2, tags='crosshair'
        )
        
        # Display coordinates - show absolute screen coordinates
        self.canvas.delete('coords')
        self.canvas.create_text(
            event.x + 20, event.y - 20,
            text=f"X: {screen_x}  Y: {screen_y}",
            font=("Arial", 10, "bold"),
            fill='white',
            tags='coords'
        )
        
        # Store screen coordinates for potential use
        self.current_screen_x = screen_x
        self.current_screen_y = screen_y
    
    def _on_click(self, event):
        """Handle click - select this point and close"""
        # Convert canvas coordinates to absolute screen coordinates
        screen_x = self.canvas.winfo_rootx() + event.x
        screen_y = self.canvas.winfo_rooty() + event.y
        self.selected_x = screen_x
        self.selected_y = screen_y
        self._close()
    
    def _on_escape(self, event):
        """Handle ESC key - cancel selection"""
        self._close()
    
    def _close(self):
        """Close overlay and call callback if point was selected"""
        self.overlay.destroy()
        
        if self.selected_x is not None and self.selected_y is not None:
            # Call callback first - GUI will handle showing the indicator
            self.callback(self.selected_x, self.selected_y)
    
    
    def show(self):
        """Show the overlay window"""
        self.overlay.mainloop()


class AutoClickerGUI:
    """Main GUI application for Single Target Mode clicking"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("")
        self.root.geometry("700x750")
        self.root.minsize(700, 750)
        self.root.resizable(True, True)
        
        # Set style
        self.root.configure(bg='#f0f0f0')
        
        # Set close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Initialize components
        self.config_manager = get_config_manager()
        self.click_engine = ClickEngine(use_dummy=False)
        self.current_config = None
        self.point_indicator = None  # Reference to indicator window
        
        # Control panel state variables - Multi-target support (2 or 1 targets)
        self.num_targets_var = tk.StringVar(value="2")
        self.target1_x_var = tk.StringVar(value="500")
        self.target1_y_var = tk.StringVar(value="500")
        self.target2_x_var = tk.StringVar(value="600")
        self.target2_y_var = tk.StringVar(value="600")
        self.target_frames = []  # Store frames for dynamic show/hide
        self.target_indicator_windows = {}  # Store indicator windows for each target {1: [windows], 2: [windows]}
        
        # Input section state variables (integrated into Control Panel)
        self.input_x_pos_var = tk.StringVar(value="500")
        self.input_y_pos_var = tk.StringVar(value="500")
        self.input_text_var = tk.StringVar()
        self.input_mode_active = False
        self.input_indicator_windows = []
        self.input_text_area = None
        self.input_setup_status = False  # Track if input section is set up
        self.input_selector_btn = None  # Reference to input selector button
        
        # Digit buttons setup status (0-9) - True when setup is complete
        self.digit_setup_status = {i: False for i in range(10)}
        self.digit_buttons = {}  # Store references to digit buttons
        self.digit_positions = {i: {"x": 0, "y": 0} for i in range(10)}  # Store positions for each digit
        
        # Match setup status
        self.match_setup_status = False
        self.match_x_pos_var = tk.StringVar(value="0")
        self.match_y_pos_var = tk.StringVar(value="0")
        self.match_btn = None
        
        # Setup selection dropdown to select which setup to apply
        self.selected_setup_var = tk.StringVar(value="0")  # Default to digit 0
        
        # Setup callbacks
        self.click_engine.set_on_click_callback(self._on_click)
        self.click_engine.set_on_stop_callback(self._on_stop)
        self.click_engine.set_on_tick_callback(self._on_tick)
        
        # Build UI
        self._build_ui()
        self._load_config()
    
    def _build_ui(self):
        """Build the user interface with modern styling"""
        # Configure root window
        self.root.configure(bg='#f5f5f5')
        
        # Title with improved styling
        title_frame = tk.Frame(self.root, bg='#1e3a5f', height=0)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        # Title label removed
        
        # Main notebook (tabbed interface) with styled tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Bind tab change event to handle page switching
        notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
        # Configure notebook style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#f5f5f5', borderwidth=0)
        style.configure('TNotebook.Tab', padding=[20, 10])
        
        # Tab 1: Control Panel (includes Input section)
        self.control_frame = tk.Frame(notebook, bg='#f5f5f5')
        notebook.add(self.control_frame, text="Control Panel")
        self._build_control_panel()
        
        # Tab 2: Settings
        self.settings_frame = tk.Frame(notebook, bg='#f5f5f5')
        notebook.add(self.settings_frame, text="Settings")
        self._build_settings_panel()
    
    def _build_control_panel(self):
        """Build the main control panel - includes digit buttons, Match, Input section, and 2/1 targets"""
        # Create scrollable frame
        canvas = tk.Canvas(self.control_frame, bg='#f5f5f5', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.control_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f5f5f5')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Status section
        status_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.FLAT, bd=1)
        status_frame.pack(fill=tk.X, pady=(15, 15), padx=15)
        status_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
        
        status_label_title = tk.Label(status_frame, text="STATUS", font=("Arial", 9, "bold"), bg='white', fg='#666666')
        status_label_title.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        self.status_label = tk.Label(status_frame, text="STOPPED", font=("Arial", 16, "bold"), fg='#e74c3c', bg='white')
        self.status_label.pack(anchor=tk.W, padx=15, pady=(5, 10))
        
        # DIGIT BUTTONS section (0-9)
        digit_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.FLAT, bd=1)
        digit_frame.pack(fill=tk.X, pady=(0, 15), padx=15)
        digit_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
        
        digit_label = tk.Label(digit_frame, text="DIGIT SETUP (0-9)", font=("Arial", 9, "bold"), bg='white', fg='#666666')
        digit_label.pack(anchor=tk.W, padx=15, pady=(10, 10))
        
        digits_container = tk.Frame(digit_frame, bg='white')
        digits_container.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        def setup_digit(digit_num):
            def on_point_selected(x, y):
                self.digit_setup_status[digit_num] = True
                self.digit_positions[digit_num]["x"] = x
                self.digit_positions[digit_num]["y"] = y
                self._update_digit_button_color(digit_num)
                self.root.after(0, lambda: self._show_point_indicator(x, y, digit_num + 10))
            selector = PointSelectorOverlay(on_point_selected)
            selector.show()
        
        def delete_digit(digit_num):
            """Delete digit setup and reset to red"""
            self.digit_setup_status[digit_num] = False
            self.digit_positions[digit_num]["x"] = 0
            self.digit_positions[digit_num]["y"] = 0
            if digit_num in self.digit_buttons:
                self.digit_buttons[digit_num].config(bg='#e74c3c')  # Turn back to red
            # Close indicator if shown
            if digit_num + 10 in self.target_indicator_windows:
                for window in self.target_indicator_windows[digit_num + 10]:
                    try:
                        window.destroy()
                    except:
                        pass
                self.target_indicator_windows[digit_num + 10] = []
        
        def toggle_digit_setup(d):
            """Toggle between setup and delete"""
            if self.digit_setup_status.get(d, False):
                delete_digit(d)
            else:
                setup_digit(d)
        
        for row in range(2):
            row_frame = tk.Frame(digits_container, bg='white')
            row_frame.pack(fill=tk.X, pady=3)
            for col in range(5):
                digit_num = row * 5 + col
                btn = tk.Button(row_frame, text=str(digit_num), command=lambda d=digit_num: toggle_digit_setup(d),
                               font=("Arial", 10, "bold"), bg='#e74c3c', fg='white', relief=tk.FLAT, padx=15, pady=5,
                               cursor="hand2", width=5)
                btn.pack(side=tk.LEFT, padx=3, expand=True)
                self.digit_buttons[digit_num] = btn
        
        # MATCH button
        match_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.FLAT, bd=1)
        match_frame.pack(fill=tk.X, pady=(0, 15), padx=15)
        match_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
        
        match_label = tk.Label(match_frame, text="MATCH SETUP", font=("Arial", 9, "bold"), bg='white', fg='#666666')
        match_label.pack(anchor=tk.W, padx=15, pady=(10, 10))
        
        match_button_container = tk.Frame(match_frame, bg='white')
        match_button_container.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        def setup_match():
            def on_point_selected(x, y):
                self.match_setup_status = True
                self.match_x_pos_var.set(str(x))
                self.match_y_pos_var.set(str(y))
                self._update_match_button_color()
                self.root.after(0, lambda: self._show_point_indicator(x, y, 999))
            selector = PointSelectorOverlay(on_point_selected)
            selector.show()
        
        def delete_match():
            """Delete match setup and reset to red"""
            self.match_setup_status = False
            self.match_x_pos_var.set("0")
            self.match_y_pos_var.set("0")
            if self.match_btn:
                self.match_btn.config(bg='#e74c3c')  # Turn back to red
            # Close indicator if shown
            if 999 in self.target_indicator_windows:
                for window in self.target_indicator_windows[999]:
                    try:
                        window.destroy()
                    except:
                        pass
                self.target_indicator_windows[999] = []
        
        def toggle_match_setup():
            """Toggle between setup and delete"""
            if self.match_setup_status:
                delete_match()
            else:
                setup_match()
        
        self.match_btn = tk.Button(match_button_container, text="SET MATCH", command=toggle_match_setup,
                                  font=("Arial", 11, "bold"), bg='#e74c3c', fg='white', relief=tk.FLAT, padx=20, pady=8, cursor="hand2")
        self.match_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        # SETUP SELECTION dropdown
        setup_select_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.FLAT, bd=1)
        setup_select_frame.pack(fill=tk.X, pady=(0, 15), padx=15)
        setup_select_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
        
        setup_label = tk.Label(setup_select_frame, text="SELECT SETUP TO APPLY", font=("Arial", 9, "bold"), bg='white', fg='#666666')
        setup_label.pack(anchor=tk.W, padx=15, pady=(10, 10))
        
        setup_combo_frame = tk.Frame(setup_select_frame, bg='white')
        setup_combo_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Create dropdown with digits 0-9 and "match"
        setup_options = [str(i) for i in range(10)] + ["match"]
        setup_combo = ttk.Combobox(setup_combo_frame, textvariable=self.selected_setup_var, values=setup_options,
                                   state="readonly", width=25, font=("Arial", 10))
        setup_combo.pack(side=tk.LEFT, padx=5)
        
        # INPUT SECTION
        input_section_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.FLAT, bd=1)
        input_section_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15), padx=15)
        input_section_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
        
        input_sec_label = tk.Label(input_section_frame, text="INPUT SECTION", font=("Arial", 9, "bold"), bg='white', fg='#666666')
        input_sec_label.pack(anchor=tk.W, padx=15, pady=(10, 10))
        
        pos_input_frame = tk.Frame(input_section_frame, bg='white')
        pos_input_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        self.input_selector_btn = tk.Button(pos_input_frame, text="SELECTOR", command=self._toggle_input_setup,
                                           bg='#e74c3c', fg='white', font=("Arial", 10, "bold"), relief=tk.FLAT, padx=15, pady=5, cursor="hand2")
        self.input_selector_btn.pack(side=tk.LEFT, padx=5)
        
        text_label = tk.Label(input_section_frame, text="Text to Type:", font=("Arial", 9, "bold"), bg='white', fg='#666666')
        text_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        self.input_text_area = tk.Text(input_section_frame, font=("Arial", 10), height=3, width=50, wrap=tk.WORD, fg='#333333')
        self.input_text_area.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        input_btn_frame = tk.Frame(input_section_frame, bg='white')
        input_btn_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        self.input_start_btn = tk.Button(input_btn_frame, text="START INPUT", command=self._start_input_automation,
                                        font=("Arial", 10, "bold"), bg='#27ae60', fg='white', relief=tk.FLAT, padx=15, pady=5, cursor="hand2")
        self.input_start_btn.pack(side=tk.LEFT, padx=5)
        
        self.input_stop_btn = tk.Button(input_btn_frame, text="STOP INPUT", command=self._stop_input_automation,
                                       font=("Arial", 10, "bold"), bg='#e74c3c', fg='white', relief=tk.FLAT, padx=15, pady=5, cursor="hand2")
        self.input_stop_btn.pack_forget()
        
        # Statistics section
        stats_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.FLAT, bd=1)
        stats_frame.pack(fill=tk.X, pady=(0, 15), padx=15)
        stats_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
        
        stats_label = tk.Label(stats_frame, text="STATISTICS", font=("Arial", 9, "bold"), bg='white', fg='#666666')
        stats_label.pack(anchor=tk.W, padx=15, pady=(10, 10))
        
        stats_content = tk.Frame(stats_frame, bg='white')
        stats_content.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        clicks_container = tk.Frame(stats_content, bg='white')
        clicks_container.pack(fill=tk.X, pady=5)
        tk.Label(clicks_container, text="Clicks:", font=("Arial", 10), bg='white', fg='#555').pack(side=tk.LEFT)
        self.clicks_label = tk.Label(clicks_container, text="0", font=("Arial", 12, "bold"), bg='white', fg='#2ecc71')
        self.clicks_label.pack(side=tk.LEFT, padx=(10, 0))
        
        time_container = tk.Frame(stats_content, bg='white')
        time_container.pack(fill=tk.X, pady=5)
        tk.Label(time_container, text="Elapsed:", font=("Arial", 10), bg='white', fg='#555').pack(side=tk.LEFT)
        self.elapsed_label = tk.Label(time_container, text="0.0s", font=("Arial", 12, "bold"), bg='white', fg='#9b59b6')
        self.elapsed_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Control buttons
        button_frame = tk.Frame(scrollable_frame, bg='#f5f5f5')
        button_frame.pack(fill=tk.X, pady=10, padx=15)
        
        self.start_btn = tk.Button(button_frame, text="START", command=self._start_clicking,
                                  font=("Arial", 12, "bold"), bg='#27ae60', fg='white', relief=tk.FLAT, padx=20, pady=10, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.pause_btn = tk.Button(button_frame, text="PAUSE", command=self._pause_clicking,
                                  font=("Arial", 12, "bold"), bg='#f39c12', fg='white', relief=tk.FLAT, padx=20, pady=10, cursor="hand2")
        self.pause_btn.pack_forget()
        
        self.stop_btn = tk.Button(button_frame, text="STOP", command=self._stop_clicking,
                                 font=("Arial", 12, "bold"), bg='#e74c3c', fg='white', relief=tk.FLAT, padx=20, pady=10, cursor="hand2")
        self.stop_btn.pack_forget()
    
    def _build_input_panel(self):
        """Build the Input panel - Click once at target, then type text"""
        # Scrollable frame for better organization
        scroll_frame = tk.Frame(self.input_frame, bg='#f5f5f5')
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Status section
        status_frame = tk.Frame(scroll_frame, bg='white', relief=tk.FLAT, bd=1)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        status_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
        
        status_label_title = tk.Label(
            status_frame,
            text="STATUS",
            font=("Arial", 9, "bold"),
            bg='white',
            fg='#666666'
        )
        status_label_title.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        self.input_status_label = tk.Label(
            status_frame,
            text="STOPPED",
            font=("Arial", 16, "bold"),
            fg='#e74c3c',
            bg='white'
        )
        self.input_status_label.pack(anchor=tk.W, padx=15, pady=(5, 10))
        
        # Target position section
        target_frame = tk.Frame(scroll_frame, bg='white', relief=tk.FLAT, bd=1)
        target_frame.pack(fill=tk.X, pady=(0, 15))
        target_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
        
        target_label = tk.Label(
            target_frame,
            text="TARGET POSITION",
            font=("Arial", 9, "bold"),
            bg='white',
            fg='#666666'
        )
        target_label.pack(anchor=tk.W, padx=15, pady=(10, 10))
        
        # Position inputs
        pos_input_frame = tk.Frame(target_frame, bg='white')
        pos_input_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Label(pos_input_frame, text="X:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 5))
        x_entry = tk.Entry(pos_input_frame, textvariable=self.input_x_pos_var, width=10, font=("Arial", 10))
        x_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(pos_input_frame, text="Y:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(15, 5))
        y_entry = tk.Entry(pos_input_frame, textvariable=self.input_y_pos_var, width=10, font=("Arial", 10))
        y_entry.pack(side=tk.LEFT, padx=5)
        
        # SELECTOR button for Input page
        input_selector_btn = tk.Button(
            pos_input_frame,
            text="SELECTOR",
            command=self._open_input_point_selector,
            bg='#3498db',
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        input_selector_btn.pack(side=tk.RIGHT, padx=(15, 0))
        
        # Text input section
        text_frame = tk.Frame(scroll_frame, bg='white', relief=tk.FLAT, bd=1)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        text_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
        
        text_label = tk.Label(
            text_frame,
            text="TEXT TO TYPE",
            font=("Arial", 9, "bold"),
            bg='white',
            fg='#666666'
        )
        text_label.pack(anchor=tk.W, padx=15, pady=(10, 10))
        
        # Text area
        self.input_text_area = tk.Text(
            text_frame,
            font=("Arial", 10),
            height=4,
            width=50,
            wrap=tk.WORD,
            fg='red'
        )
        self.input_text_area.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        # Control buttons
        button_frame = tk.Frame(scroll_frame, bg='#f5f5f5')
        button_frame.pack(fill=tk.X, pady=10)
        
        self.input_start_btn = tk.Button(
            button_frame,
            text="START",
            command=self._start_input_automation,
            font=("Arial", 12, "bold"),
            bg='#27ae60',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.input_start_btn.pack_forget()
        
        self.input_stop_btn = tk.Button(
            button_frame,
            text="STOP",
            command=self._stop_input_automation,
            font=("Arial", 12, "bold"),
            bg='#e74c3c',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.input_stop_btn.pack_forget()
    
    def _open_input_point_selector(self):
        """Open draggable point selector for Input page"""
        def on_point_selected(x, y):
            """Callback when point is selected"""
            self.input_x_pos_var.set(str(x))
            self.input_y_pos_var.set(str(y))
            self.input_setup_status = True  # Mark input section as set up
            self._update_input_selector_button_color()  # Change button to green
            # Schedule indicator display on main thread
            self.root.after(0, lambda: self._show_input_point_indicator(x, y))
            # Show the START button after point selection
            self.root.after(0, lambda: self.input_start_btn.pack(side=tk.LEFT, padx=5, expand=True))
        
        # Create and show selector
        selector = PointSelectorOverlay(on_point_selected)
        selector.show()
    
    def _delete_input_setup(self):
        """Delete input setup and reset to red"""
        self.input_setup_status = False
        self.input_x_pos_var.set("0")
        self.input_y_pos_var.set("0")
        if self.input_selector_btn:
            self.input_selector_btn.config(bg='#e74c3c')  # Turn back to red
        # Close indicator if shown
        for window in self.input_indicator_windows:
            try:
                window.destroy()
            except:
                pass
        self.input_indicator_windows = []
    
    def _toggle_input_setup(self):
        """Toggle between setup and delete for input"""
        if self.input_setup_status:
            self._delete_input_setup()
        else:
            self._open_input_point_selector()
    
    def _show_input_point_indicator(self, x, y):
        """Show a persistent indicator at the selected point for Input page"""
        # Close previous indicators if they exist
        for window in self.input_indicator_windows:
            try:
                window.destroy()
            except:
                pass
        self.input_indicator_windows = []
        
        try:
            gap_distance = 10
            line_length = 5
            line_width = 2
            offset_x = x  # Center exactly at click position
            offset_y = y  # Center exactly at click position
            top_window = tk.Toplevel(self.root)
            top_window.attributes('-alpha', 0.9)
            top_window.attributes('-topmost', True)
            top_window.overrideredirect(True)
            top_window.geometry(f"{line_length * 2}x{line_width}+{offset_x - line_length}+{offset_y - gap_distance - line_width // 2}")
            top_window.configure(bg='#ff0000')
            
            canvas_top = tk.Canvas(
                top_window,
                bg='#ff0000',
                highlightthickness=0,
                width=line_length * 2,
                height=line_width
            )
            canvas_top.pack(fill=tk.BOTH, expand=True)
            self.input_indicator_windows.append(top_window)
            self._make_window_click_through(top_window)
            
            # BOTTOM line - centered at (offset_x, offset_y + gap_distance)
            bottom_window = tk.Toplevel(self.root)
            bottom_window.attributes('-alpha', 0.9)
            bottom_window.attributes('-topmost', True)
            bottom_window.overrideredirect(True)
            bottom_window.geometry(f"{line_length * 2}x{line_width}+{offset_x - line_length}+{offset_y + gap_distance - line_width // 2}")
            bottom_window.configure(bg='#ff0000')
            
            canvas_bottom = tk.Canvas(
                bottom_window,
                bg='#ff0000',
                highlightthickness=0,
                width=line_length * 2,
                height=line_width
            )
            canvas_bottom.pack(fill=tk.BOTH, expand=True)
            self.input_indicator_windows.append(bottom_window)
            self._make_window_click_through(bottom_window)
            
            # LEFT line - centered at (offset_x - gap_distance, offset_y)
            left_window = tk.Toplevel(self.root)
            left_window.attributes('-alpha', 0.9)
            left_window.attributes('-topmost', True)
            left_window.overrideredirect(True)
            left_window.geometry(f"{line_width}x{line_length * 2}+{offset_x - gap_distance - line_width // 2}+{offset_y - line_length}")
            left_window.configure(bg='#ff0000')
            
            canvas_left = tk.Canvas(
                left_window,
                bg='#ff0000',
                highlightthickness=0,
                width=line_width,
                height=line_length * 2
            )
            canvas_left.pack(fill=tk.BOTH, expand=True)
            self.input_indicator_windows.append(left_window)
            self._make_window_click_through(left_window)
            
            # RIGHT line - centered at (offset_x + gap_distance, offset_y)
            right_window = tk.Toplevel(self.root)
            right_window.attributes('-alpha', 0.9)
            right_window.attributes('-topmost', True)
            right_window.overrideredirect(True)
            right_window.geometry(f"{line_width}x{line_length * 2}+{offset_x + gap_distance - line_width // 2}+{offset_y - line_length}")
            right_window.configure(bg='#ff0000')
            
            canvas_right = tk.Canvas(
                right_window,
                bg='#ff0000',
                highlightthickness=0,
                width=line_width,
                height=line_length * 2
            )
            canvas_right.pack(fill=tk.BOTH, expand=True)
            self.input_indicator_windows.append(right_window)
            self._make_window_click_through(right_window)
            
            print("[INPUT INDICATOR] 4 separate line windows indicator ready - centered at ({}, {})".format(x, y))
            
        except Exception as e:
            print(f"Error showing input indicator: {e}")
    
    def _start_input_automation(self):
        """Start the input automation - click once then type text"""
        try:
            x_pos = int(self.input_x_pos_var.get())
            y_pos = int(self.input_y_pos_var.get())
            text_to_type = self.input_text_area.get("1.0", tk.END).strip()
            
            if not text_to_type:
                messagebox.showwarning("Warning", "Please enter text to type")
                return
            
            self.input_mode_active = True
            self.input_start_btn.pack_forget()
            self.input_stop_btn.pack(side=tk.LEFT, padx=5, expand=True)
            
            # Run automation in thread
            thread = threading.Thread(
                target=self._input_automation_loop,
                args=(x_pos, y_pos, text_to_type),
                daemon=True
            )
            thread.start()
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error starting automation: {e}")
    
    def _input_automation_loop(self, x_pos, y_pos, text_to_type):
        """Main loop for input automation"""
        try:
            import pyautogui
            import time
            
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0.05
            
            while self.input_mode_active:
                # Move to position
                pyautogui.moveTo(x_pos, y_pos, duration=0.1)
                time.sleep(0.1)
                
                # Click once
                pyautogui.mouseDown()
                time.sleep(0.05)
                pyautogui.mouseUp()
                time.sleep(0.1)
                
                # Clear the input field: Ctrl+A to select all, then type (which replaces)
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.1)
                
                # Type the text
                pyautogui.typewrite(text_to_type, interval=0.05)
                time.sleep(0.2)
                
                # Only do this once per click
                self.input_mode_active = False
                
        except Exception as e:
            print(f"Error in input automation: {e}")
        finally:
            # Stop automation
            self.root.after(0, self._stop_input_automation)
    
    def _stop_input_automation(self):
        """Stop the input automation"""
        self.input_mode_active = False
        self.input_stop_btn.pack_forget()
        self.input_start_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        # Destroy indicator windows
        for window in self.input_indicator_windows:
            try:
                window.destroy()
            except:
                pass
        self.input_indicator_windows = []
    
    def _build_scan_panel(self):
        """Build the SCAN panel - Square indicator for scanning areas"""
        # Scrollable frame for better organization
        scroll_frame = tk.Frame(self.scan_frame, bg='#f5f5f5')
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Status section
        status_frame = tk.Frame(scroll_frame, bg='white', relief=tk.FLAT, bd=1)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        status_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
        
        status_label_title = tk.Label(
            status_frame,
            text="STATUS",
            font=("Arial", 9, "bold"),
            bg='white',
            fg='#666666'
        )
        status_label_title.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        self.scan_status_label = tk.Label(
            status_frame,
            text="READY",
            font=("Arial", 16, "bold"),
            fg='#27ae60',
            bg='white'
        )
        self.scan_status_label.pack(anchor=tk.W, padx=15, pady=(5, 10))
        
        # Target position section
        target_frame = tk.Frame(scroll_frame, bg='white', relief=tk.FLAT, bd=1)
        target_frame.pack(fill=tk.X, pady=(0, 15))
        target_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
        
        target_label = tk.Label(
            target_frame,
            text="TARGET POSITION",
            font=("Arial", 9, "bold"),
            bg='white',
            fg='#666666'
        )
        target_label.pack(anchor=tk.W, padx=15, pady=(10, 10))
        
        # Position inputs
        pos_input_frame = tk.Frame(target_frame, bg='white')
        pos_input_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Label(pos_input_frame, text="X:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 5))
        x_entry = tk.Entry(pos_input_frame, textvariable=self.scan_x_pos_var, width=10, font=("Arial", 10))
        x_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(pos_input_frame, text="Y:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(15, 5))
        y_entry = tk.Entry(pos_input_frame, textvariable=self.scan_y_pos_var, width=10, font=("Arial", 10))
        y_entry.pack(side=tk.LEFT, padx=5)
        
        # SELECTOR button for Scan page
        scan_selector_btn = tk.Button(
            pos_input_frame,
            text="SELECTOR",
            command=self._open_scan_point_selector,
            bg='#3498db',
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        scan_selector_btn.pack(side=tk.RIGHT, padx=(15, 0))
        
        # OCR Model Selection section
        ocr_model_frame = tk.Frame(scroll_frame, bg='white', relief=tk.FLAT, bd=1)
        ocr_model_frame.pack(fill=tk.X, pady=(0, 15))
        ocr_model_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
        
        ocr_label = tk.Label(
            ocr_model_frame,
            text="OCR MODEL",
            font=("Arial", 9, "bold"),
            bg='white',
            fg='#666666'
        )
        ocr_label.pack(anchor=tk.W, padx=15, pady=(10, 10))
        
        # OCR model input
        ocr_input_frame = tk.Frame(ocr_model_frame, bg='white')
        ocr_input_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Label(ocr_input_frame, text="Select Model:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 5))
        ocr_model_combo = ttk.Combobox(
            ocr_input_frame,
            textvariable=self.scan_ocr_model_var,
            values=["Tesseract", "PaddleOCR", "Docext"],
            state="readonly",
            width=20,
            font=("Arial", 10)
        )
        ocr_model_combo.pack(side=tk.LEFT, padx=5)
        
        # Capture interval section
        interval_frame = tk.Frame(scroll_frame, bg='white', relief=tk.FLAT, bd=1)
        interval_frame.pack(fill=tk.X, pady=(0, 15))
        interval_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
        
        interval_label = tk.Label(
            interval_frame,
            text="CAPTURE INTERVAL",
            font=("Arial", 9, "bold"),
            bg='white',
            fg='#666666'
        )
        interval_label.pack(anchor=tk.W, padx=15, pady=(10, 10))
        
        # Interval input
        interval_input_frame = tk.Frame(interval_frame, bg='white')
        interval_input_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Label(interval_input_frame, text="Seconds (min 5):", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 5))
        interval_spin = tk.Spinbox(
            interval_input_frame,
            from_=5,
            to=300,
            textvariable=self.scan_capture_interval,
            width=10,
            font=("Arial", 10)
        )
        interval_spin.pack(side=tk.LEFT, padx=5)
        
        # Output section
        output_frame = tk.Frame(scroll_frame, bg='white', relief=tk.FLAT, bd=1)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        output_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
        
        output_label = tk.Label(
            output_frame,
            text="CAPTURED TEXT OUTPUT",
            font=("Arial", 9, "bold"),
            bg='white',
            fg='#666666'
        )
        output_label.pack(anchor=tk.W, padx=15, pady=(10, 10))
        
        # Text area for captured output
        self.scan_output_text = tk.Text(
            output_frame,
            font=("Arial", 10),
            height=8,
            width=50,
            wrap=tk.WORD
        )
        self.scan_output_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        # Control buttons
        button_frame = tk.Frame(scroll_frame, bg='#f5f5f5')
        button_frame.pack(fill=tk.X, pady=10)
        
        self.scan_extract_btn = tk.Button(
            button_frame,
            text="EXTRACT (ML Kit style)",
            command=self._toggle_extract_capture,
            font=("Arial", 12, "bold"),
            bg='#009688',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        # Pack the button so it's visible
        self.scan_extract_btn.pack(side=tk.LEFT, padx=5, expand=True)
    
    def _build_settings_panel(self):
        """Build the settings panel"""
        settings_frame = ttk.LabelFrame(self.settings_frame, text="Click Configuration", padding=15)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Click interval
        tk.Label(settings_frame, text="Click Interval (milliseconds):").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.interval_var = tk.StringVar(value="500")
        interval_spin = tk.Spinbox(
            settings_frame,
            from_=10,
            to=10000,
            textvariable=self.interval_var,
            width=15
        )
        interval_spin.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Stop condition
        tk.Label(settings_frame, text="Stop Condition:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.stop_condition_var = tk.StringVar(value="0")
        stop_options = ttk.Combobox(
            settings_frame,
            textvariable=self.stop_condition_var,
            values=["Indefinite", "Time-based", "Cycles-based"],
            state="readonly",
            width=25
        )
        stop_options.current(0)
        stop_options.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        stop_options.bind('<<ComboboxSelected>>', self._on_stop_condition_change)
        
        # Stop value (for time or cycles)
        tk.Label(settings_frame, text="Stop Value:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.stop_value_var = tk.StringVar(value="60")
        self.stop_value_label = tk.Label(settings_frame, text="(seconds)")
        stop_value_spin = tk.Spinbox(
            settings_frame,
            from_=1,
            to=9999,
            textvariable=self.stop_value_var,
            width=15
        )
        stop_value_spin.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
        self.stop_value_label.grid(row=2, column=2, sticky=tk.W, padx=5, pady=10)
        
        # Anti-detection
        tk.Label(settings_frame, text="Anti-Detection:").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.anti_detection_var = tk.BooleanVar(value=False)
        anti_det_check = tk.Checkbutton(
            settings_frame,
            text="Enable random variations",
            variable=self.anti_detection_var
        )
        anti_det_check.grid(row=3, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Anti-detection offset
        tk.Label(settings_frame, text="Anti-Detection Offset (pixels):").grid(row=4, column=0, sticky=tk.W, pady=10)
        self.offset_var = tk.StringVar(value="5")
        offset_spin = tk.Spinbox(
            settings_frame,
            from_=1,
            to=50,
            textvariable=self.offset_var,
            width=15
        )
        offset_spin.grid(row=4, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Save settings button
        save_btn = tk.Button(
            settings_frame,
            text="Save Settings",
            command=self._save_settings,
            bg='#3498db',
            fg='white',
            width=20
        )
        save_btn.grid(row=5, column=0, columnspan=2, pady=20, sticky=tk.W)
    
    def _build_config_panel(self):
        """Build the configuration management panel"""
        # Config listbox
        list_frame = ttk.LabelFrame(self.config_frame, text="Saved Configurations", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.config_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.config_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.config_listbox.yview)
        
        # Button frame
        btn_frame = tk.Frame(self.config_frame, bg='#f0f0f0')
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            btn_frame,
            text="Load",
            command=self._load_selected_config,
            bg='#3498db',
            fg='white',
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Save Current as",
            command=self._save_config_dialog,
            bg='#27ae60',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Delete",
            command=self._delete_selected_config,
            bg='#e74c3c',
            fg='white',
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Export",
            command=self._export_config,
            bg='#9b59b6',
            fg='white',
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Import",
            command=self._import_config,
            bg='#9b59b6',
            fg='white',
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        # Refresh list
        self._refresh_config_list()
    

    
    def _get_cursor_position(self):
        """Get current cursor position and update fields"""
        try:
            import pyautogui
            x, y = pyautogui.position()
            self.x_pos_var.set(str(x))
            self.y_pos_var.set(str(y))
        except Exception as e:
            messagebox.showerror("Error", f"Could not get cursor position: {e}")
    
    def _open_point_selector(self, target_num=1):
        """Open draggable point selector overlay for specified target"""
        def on_point_selected(x, y):
            """Callback when point is selected"""
            # Set the appropriate target coordinates
            if target_num == 1:
                self.target1_x_var.set(str(x))
                self.target1_y_var.set(str(y))
            elif target_num == 2:
                self.target2_x_var.set(str(x))
                self.target2_y_var.set(str(y))
            elif target_num == 3:
                self.target3_x_var.set(str(x))
                self.target3_y_var.set(str(y))
            
            # Schedule indicator display on main thread (tkinter is not thread-safe)
            self.root.after(0, lambda tn=target_num: self._show_point_indicator(x, y, tn))
            # Show the START button after point selection
            self.root.after(0, lambda: self.start_btn.pack(side=tk.LEFT, padx=5, expand=True))
        
        # Create and show selector in a separate thread to not block UI
        selector = PointSelectorOverlay(on_point_selected)
        
        # Show selector (this will block until selection is made or cancelled)
        selector.show()
    
    def _show_point_indicator(self, x, y, target_num=1):
        """Show a persistent indicator at the selected point on screen for a specific target
        
        4 separate indicator windows per target:
        - Each line in its own separate window (not in a container)
        - Top line, Bottom line, Left line, Right line
        - Each window positioned independently with 20 pixels distance from center
        - Completely click-through to the target
        - Each target (1, 2, 3) has its own independent set of indicators
        """
        # Initialize storage for this target if needed
        if target_num not in self.target_indicator_windows:
            self.target_indicator_windows[target_num] = []
        
        # Close previous indicators for this target if they exist
        for window in self.target_indicator_windows[target_num]:
            try:
                window.destroy()
            except:
                pass
        self.target_indicator_windows[target_num] = []
        
        try:
            gap_distance = 10
            line_length = 5
            line_width = 2
            offset_x = x  # Center exactly at click position
            offset_y = y  # Center exactly at click position
            
            # TOP line (horizontal, above center) - centered at (offset_x, offset_y - gap_distance)
            top_window = tk.Toplevel(self.root)
            top_window.attributes('-alpha', 0.9)
            top_window.attributes('-topmost', True)
            top_window.overrideredirect(True)
            top_window.geometry(f"{line_length * 2}x{line_width}+{offset_x - line_length}+{offset_y - gap_distance - line_width // 2}")
            top_window.configure(bg='#0074d4')
            
            canvas_top = tk.Canvas(
                top_window,
                bg='#0074d4',
                highlightthickness=0,
                width=line_length * 2,
                height=line_width
            )
            canvas_top.pack(fill=tk.BOTH, expand=True)
            
            self.target_indicator_windows[target_num].append(top_window)
            
            # Apply click-through to TOP window
            self._make_window_click_through(top_window)
            
            # BOTTOM line (horizontal, below center) - centered at (offset_x, offset_y + gap_distance)
            bottom_window = tk.Toplevel(self.root)
            bottom_window.attributes('-alpha', 0.9)
            bottom_window.attributes('-topmost', True)
            bottom_window.overrideredirect(True)
            bottom_window.geometry(f"{line_length * 2}x{line_width}+{offset_x - line_length}+{offset_y + gap_distance - line_width // 2}")
            bottom_window.configure(bg='#0074d4')
            
            canvas_bottom = tk.Canvas(
                bottom_window,
                bg='#0074d4',
                highlightthickness=0,
                width=line_length * 2,
                height=line_width
            )
            canvas_bottom.pack(fill=tk.BOTH, expand=True)
            
            self.target_indicator_windows[target_num].append(bottom_window)
            
            # Apply click-through to BOTTOM window
            self._make_window_click_through(bottom_window)
            
            # LEFT line (vertical, left of center) - centered at (offset_x - gap_distance, offset_y)
            left_window = tk.Toplevel(self.root)
            left_window.attributes('-alpha', 0.9)
            left_window.attributes('-topmost', True)
            left_window.overrideredirect(True)
            left_window.geometry(f"{line_width}x{line_length * 2}+{offset_x - gap_distance - line_width // 2}+{offset_y - line_length}")
            left_window.configure(bg='#0074d4')
            
            canvas_left = tk.Canvas(
                left_window,
                bg='#0074d4',
                highlightthickness=0,
                width=line_width,
                height=line_length * 2
            )
            canvas_left.pack(fill=tk.BOTH, expand=True)
            
            self.target_indicator_windows[target_num].append(left_window)
            
            # Apply click-through to LEFT window
            self._make_window_click_through(left_window)
            
            # RIGHT line (vertical, right of center) - centered at (offset_x + gap_distance, offset_y)
            right_window = tk.Toplevel(self.root)
            right_window.attributes('-alpha', 0.9)
            right_window.attributes('-topmost', True)
            right_window.overrideredirect(True)
            right_window.geometry(f"{line_width}x{line_length * 2}+{offset_x + gap_distance - line_width // 2}+{offset_y - line_length}")
            right_window.configure(bg='#0074d4')
            
            canvas_right = tk.Canvas(
                right_window,
                bg='#0074d4',
                highlightthickness=0,
                width=line_width,
                height=line_length * 2
            )
            canvas_right.pack(fill=tk.BOTH, expand=True)
            
            self.target_indicator_windows[target_num].append(right_window)
            
            # Apply click-through to RIGHT window
            self._make_window_click_through(right_window)
            
            print(f"[INDICATOR] Target {target_num} - 4 separate line windows indicator ready - centered at ({x}, {y})")
            
        except Exception as e:
            print(f"Error showing indicator: {e}")
    
    def _make_window_click_through(self, window):
        """Make a window completely click-through using Windows API"""
        if sys.platform == 'win32':
            try:
                window.update_idletasks()
                hwnd = int(window.winfo_id())
                # WS_EX_TRANSPARENT = 0x00000020 - Makes window click-through
                WS_EX_TRANSPARENT = 0x00000020
                GWL_EXSTYLE = -20
                
                # Get current style and add transparent flag
                current_style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                new_style = current_style | WS_EX_TRANSPARENT
                windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
                
                # Update window to apply changes
                windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0001 | 0x0002)
            except Exception as e:
                print(f"[WARNING] Could not make window click-through: {e}")
    
    def _open_scan_point_selector(self):
        """Open draggable point selector for SCAN page"""
        def on_point_selected(x, y):
            """Callback when point is selected"""
            self.scan_x_pos_var.set(str(x))
            self.scan_y_pos_var.set(str(y))
            self.scan_square_set = True  # Mark square as set
            # Show Extract button now
            if not self.scan_extract_btn.winfo_manager():
                self.scan_extract_btn.pack(side=tk.LEFT, padx=5, expand=True)
            # Schedule indicator display on main thread
            self.root.after(0, lambda: self._show_scan_square_indicator(x, y))
        
        # Create and show selector
        selector = PointSelectorOverlay(on_point_selected)
        selector.show()
    
    def _show_scan_square_indicator(self, x, y):
        """Show a square indicator at the selected point for SCAN page"""
        # Close previous indicator if it exists
        if self.scan_indicator_window:
            try:
                self.scan_indicator_window.destroy()
            except:
                pass
        self.scan_indicator_window = None
        
        try:
            width = int(self.scan_width_var.get())
            height = int(self.scan_height_var.get())
            
            # Calculate top-left corner (square centered at x, y)
            top_x = x - width // 2
            top_y = y - height // 2
            
            # Create square window
            square_window = tk.Toplevel(self.root)
            square_window.attributes('-alpha', 0.7)
            square_window.attributes('-topmost', True)
            square_window.overrideredirect(True)  # Remove window bar
            square_window.geometry(f"{width}x{height}+{top_x}+{top_y}")
            square_window.configure(bg='#2ecc71')
            
            # Create canvas
            canvas = tk.Canvas(
                square_window,
                bg='#2ecc71',
                highlightthickness=0,
                width=width,
                height=height,
                relief=tk.FLAT,
                bd=0
            )
            canvas.pack(fill=tk.BOTH, expand=True)
            
            # Draw rectangle border
            canvas.create_rectangle(
                0, 0,
                width - 1, height - 1,
                outline='#27ae60',
                width=2
            )
            
            self.scan_indicator_window = square_window
            self.scan_current_center = (x, y)
            self.scan_current_x_pos = top_x
            self.scan_current_y_pos = top_y
            
            # Add resize and move handlers
            self._add_square_resize_handlers(canvas, square_window, x, y)
            
            print(f"[SCAN INDICATOR] Square ready at ({x}, {y}), Size {width}x{height}")
            
        except Exception as e:
            print(f"Error showing scan indicator: {e}")
    
    def _add_square_resize_handlers(self, canvas, window, center_x, center_y):
        """Add mouse handlers for resizing and moving the square"""
        resize_state = {
            'dragging': False,
            'edge': None,
            'start_x': 0,
            'start_y': 0,
            'mode': None,
            'center_x': center_x,
            'center_y': center_y,
            'window': window
        }
        
        edge_threshold = 15
        
        def get_edge_at_position(rel_x, rel_y):
            """Get which edge/corner the cursor is near"""
            try:
                w = int(self.scan_width_var.get())
                h = int(self.scan_height_var.get())
            except:
                return None
            
            near_left = rel_x < edge_threshold
            near_right = rel_x > w - edge_threshold
            near_top = rel_y < edge_threshold
            near_bottom = rel_y > h - edge_threshold
            
            if near_left and near_top:
                return 'tl'
            elif near_right and near_top:
                return 'tr'
            elif near_left and near_bottom:
                return 'bl'
            elif near_right and near_bottom:
                return 'br'
            elif near_left:
                return 'l'
            elif near_right:
                return 'r'
            elif near_top:
                return 't'
            elif near_bottom:
                return 'b'
            return None
        
        def motion_handler(event):
            """Update cursor based on position"""
            edge = get_edge_at_position(event.x, event.y)
            if edge in ['tl', 'br']:
                canvas.config(cursor='sizing')
            elif edge in ['tr', 'bl']:
                canvas.config(cursor='sizing')
            elif edge in ['l', 'r']:
                canvas.config(cursor='sb_h_double_arrow')
            elif edge in ['t', 'b']:
                canvas.config(cursor='sb_v_double_arrow')
            else:
                canvas.config(cursor='fleur')
        
        def press_handler(event):
            """Start drag operation"""
            edge = get_edge_at_position(event.x, event.y)
            resize_state['dragging'] = True
            resize_state['start_x'] = event.x_root
            resize_state['start_y'] = event.y_root
            resize_state['edge'] = edge
            resize_state['mode'] = 'resize' if edge else 'move'
        
        def release_handler(event):
            """End drag operation"""
            resize_state['dragging'] = False
        
        def drag_handler(event):
            """Handle dragging"""
            if not resize_state['dragging']:
                return
            
            dx = event.x_root - resize_state['start_x']
            dy = event.y_root - resize_state['start_y']
            
            try:
                w = int(self.scan_width_var.get())
                h = int(self.scan_height_var.get())
                win = resize_state['window']
            except:
                return
            
            edge = resize_state['edge']
            
            if resize_state['mode'] == 'resize' and edge:
                # Resizing logic - update geometry directly
                new_w = w
                new_h = h
                new_cx = resize_state['center_x']
                new_cy = resize_state['center_y']
                
                if 'r' in edge:
                    new_w = max(20, w + dx)
                if 'l' in edge:
                    new_w = max(20, w - dx)
                    new_cx = resize_state['center_x'] - dx // 2
                
                if 'b' in edge:
                    new_h = max(20, h + dy)
                if 't' in edge:
                    new_h = max(20, h - dy)
                    new_cy = resize_state['center_y'] - dy // 2
                
                new_top_x = new_cx - new_w // 2
                new_top_y = new_cy - new_h // 2
                
                # Update window geometry
                try:
                    win.geometry(f"{new_w}x{new_h}+{new_top_x}+{new_top_y}")
                    
                    # Update vars and state
                    self.scan_width_var.set(str(new_w))
                    self.scan_height_var.set(str(new_h))
                    resize_state['center_x'] = new_cx
                    resize_state['center_y'] = new_cy
                    
                    # Redraw canvas
                    canvas.delete('all')
                    canvas.create_rectangle(
                        0, 0,
                        new_w - 1, new_h - 1,
                        outline='#27ae60',
                        width=2
                    )
                except:
                    pass
                
            elif resize_state['mode'] == 'move':
                # Moving logic - update geometry directly
                new_cx = resize_state['center_x'] + dx
                new_cy = resize_state['center_y'] + dy
                new_top_x = new_cx - w // 2
                new_top_y = new_cy - h // 2
                
                # Update window geometry
                try:
                    win.geometry(f"{w}x{h}+{new_top_x}+{new_top_y}")
                    
                    # Update vars and state
                    self.scan_x_pos_var.set(str(new_cx))
                    self.scan_y_pos_var.set(str(new_cy))
                    resize_state['center_x'] = new_cx
                    resize_state['center_y'] = new_cy
                except:
                    pass
            
            # Update tracking
            resize_state['start_x'] = event.x_root
            resize_state['start_y'] = event.y_root
        
        # Bind all events to canvas
        canvas.bind('<Motion>', motion_handler)
        canvas.bind('<Button-1>', press_handler)
        canvas.bind('<ButtonRelease-1>', release_handler)
        canvas.bind('<B1-Motion>', drag_handler)
    
    def _update_scan_indicator(self):
        """Update the scan indicator when width/height changes"""
        try:
            if self.scan_indicator_window and self.scan_indicator_window.winfo_exists():
                x = int(self.scan_x_pos_var.get())
                y = int(self.scan_y_pos_var.get())
                self._show_scan_square_indicator(x, y)
        except:
            pass
    
    def _start_scan_capture(self):
        """Start capturing and processing the square area at intervals"""
        try:
            interval = int(self.scan_capture_interval.get())
            if interval < 10:
                messagebox.showwarning("Invalid Interval", "Minimum interval is 10 seconds")
                return
            
            x = int(self.scan_x_pos_var.get())
            y = int(self.scan_y_pos_var.get())
            w = int(self.scan_width_var.get())
            h = int(self.scan_height_var.get())
            
            if w < 20 or h < 20:
                messagebox.showwarning("Invalid Dimensions", "Square must be at least 20x20 pixels")
                return
            
            self.scan_capture_active = True
            self.scan_capture_start_btn.pack_forget()
            self.scan_capture_stop_btn.pack(side=tk.LEFT, padx=5, expand=True)
            self.scan_output_text.delete(1.0, tk.END)
            self.scan_output_text.insert(1.0, "Capture started...\n")
            
            # Start capture thread
            thread = threading.Thread(
                target=self._scan_capture_loop,
                args=(x, y, w, h, interval),
                daemon=True
            )
            thread.start()
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for position and dimensions")
    
    def _toggle_extract_capture(self):
        """Toggle between extract and stop for continuous ML Kit extraction"""
        if self.scan_capture_active:
            # Stop extraction
            self.scan_capture_active = False
            self.scan_extract_btn.config(text="EXTRACT (ML Kit style)", bg='#009688')
            # Clear the CSV file and output when stopping
            self._clear_scan_csv()
            self._clear_scan_output()
        else:
            # Start extraction
            try:
                x = int(self.scan_x_pos_var.get())
                y = int(self.scan_y_pos_var.get())
                w = int(self.scan_width_var.get())
                h = int(self.scan_height_var.get())
                
                if w < 20 or h < 20:
                    messagebox.showwarning("Invalid Dimensions", "Square must be at least 20x20 pixels")
                    return
                
                interval = int(self.scan_capture_interval.get())
                if interval < 10:
                    messagebox.showwarning("Invalid Interval", "Minimum interval is 10 seconds")
                    return
                
                self.scan_capture_active = True
                self.scan_extract_btn.config(text="STOP EXTRACTION", bg='#e74c3c')
                
                # Start capture thread
                import threading
                thread = threading.Thread(target=self._scan_capture_loop, args=(x, y, w, h, interval), daemon=True)
                thread.start()
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid numbers for position and dimensions")
    
    def _stop_scan_capture(self):
        """Stop the capture process"""
        self.scan_capture_active = False
        self.scan_capture_stop_btn.pack_forget()
        self.scan_capture_start_btn.pack(side=tk.LEFT, padx=5, expand=True)
    
    def _scan_capture_loop(self, x, y, w, h, interval):
        """Main loop for capturing and processing the square area using ML Kit style preprocessing"""
        try:
            import pyautogui
            import time
            from PIL import ImageGrab, Image
            import pytesseract
            import cv2
            import numpy as np
            
            # Calculate capture region (top-left corner)
            left = x - w // 2
            top = y - h // 2
            right = left + w
            bottom = top + h
            
            self.root.after(0, lambda: self.scan_output_text.insert(tk.END, f"Capturing region: ({left}, {top}) to ({right}, {bottom})\n"))
            
            while self.scan_capture_active:
                try:
                    # Capture the square region
                    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
                    
                    # Convert PIL Image to numpy array
                    screenshot_array = np.array(screenshot)
                    
                    # Convert to OpenCV format (BGR)
                    image = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2BGR)
                    
                    # Apply ML Kit style preprocessing (exactly like _extract_scan_square)
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    
                    # Enhanced contrast and brightness for better text detection
                    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                    enhanced = clahe.apply(gray)
                    
                    # Apply thresholding for crisp text edges
                    _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    
                    # Normalize to 0-255 range
                    normalized = cv2.normalize(thresh, None, 0, 255, cv2.NORM_MINMAX)
                    
                    # Ultra high-resolution upscaling for better OCR accuracy (8x upscaling for small text)
                    height_img, width_img = image_rgb.shape[:2]
                    scale_factor = 8.0  # 8x upscaling for maximum OCR accuracy with small text
                    upscaled_height = int(height_img * scale_factor)
                    upscaled_width = int(width_img * scale_factor)
                    image_rgb = cv2.resize(image_rgb, (upscaled_width, upscaled_height), interpolation=cv2.INTER_CUBIC)
                    
                    # Convert to PIL for Tesseract
                    pil_image = Image.fromarray(image_rgb)
                    
                    # Extract text using selected OCR model
                    text = self._extract_with_ocr_model(pil_image, image)
                    
                    # Get full timestamp for CSV
                    from datetime import datetime
                    timestamp_full = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    timestamp_display = time.strftime("%H:%M:%S")
                    
                    # Save to CSV
                    self.root.after(0, lambda t=text, ts=timestamp_full: self._save_extraction_to_csv(t, ts))
                    
                    # Update output
                    output = f"[{timestamp_display}] Extracted:\n{text}\n\n" if text.strip() else f"[{timestamp_display}] No text detected\n\n"
                    
                    self.root.after(0, lambda o=output: self._append_scan_output(o))
                    
                    # Wait for next capture
                    for _ in range(interval):
                        if not self.scan_capture_active:
                            break
                        time.sleep(1)
                    
                except Exception as e:
                    error_msg = f"Capture error: {str(e)}\n"
                    self.root.after(0, lambda msg=error_msg: self._append_scan_output(msg))
                    time.sleep(1)
        
        except ImportError as e:
            self.root.after(0, lambda: self._append_scan_output(f"Missing dependency: {str(e)}\nPlease install: pytesseract, opencv-python, Pillow\n"))
    
    def _append_scan_output(self, text):
        """Safely append text to scan output from thread"""
        try:
            self.scan_output_text.insert(tk.END, text)
            self.scan_output_text.see(tk.END)
        except:
            pass
    
    def _clear_scan_csv(self):
        """Clear the scan_extractions.csv file content (keep file, clear content)"""
        try:
            data_dir = os.path.join(os.getcwd(), 'data')
            csv_file = os.path.join(data_dir, 'scan_extractions.csv')
            
            if os.path.exists(csv_file):
                # Truncate the file (clear content)
                with open(csv_file, 'w') as f:
                    f.write('')
                print(f"Cleared scan extractions file content: {csv_file}")
        except Exception as e:
            print(f"Error clearing CSV file: {str(e)}")
    
    def _clear_scan_output(self):
        """Clear the scan output text widget"""
        try:
            if hasattr(self, 'scan_output_text'):
                self.scan_output_text.delete(1.0, tk.END)
                print("Cleared scan output text")
        except Exception as e:
            print(f"Error clearing scan output: {str(e)}")
    
    def _on_closing(self):
        """Handle window closing - clear CSV, output and cleanup"""
        # Stop any active capture
        if self.scan_capture_active:
            self.scan_capture_active = False
        
        # Clear the scan CSV file and output
        self._clear_scan_csv()
        self._clear_scan_output()
        
        # Destroy window
        self.root.destroy()
    
    def _on_tab_changed(self, event=None):
        """Handle tab switching - clear CSV and output when leaving SCAN tab"""
        try:
            # Get the currently selected tab
            selected_tab = event.widget.select()
            tab_text = event.widget.tab(selected_tab, "text")
            
            # No longer need to handle SCAN tab
        except Exception as e:
            print(f"Error in tab change handler: {str(e)}")
    
    def _save_extraction_to_csv(self, extracted_text, timestamp):
        """Save extracted text to CSV file"""
        try:
            # Create data directory in the workspace root
            # Get the current working directory
            data_dir = os.path.join(os.getcwd(), 'data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # Define CSV file path
            csv_file = os.path.join(data_dir, 'scan_extractions.csv')
            
            # Check if file exists to determine if we need to write headers
            file_exists = os.path.exists(csv_file)
            
            # Prepare data
            row_data = {
                'Timestamp': timestamp,
                'X': int(self.scan_x_pos_var.get()),
                'Y': int(self.scan_y_pos_var.get()),
                'Width': int(self.scan_width_var.get()),
                'Height': int(self.scan_height_var.get()),
                'Extracted_Text': extracted_text
            }
            
            # Write to CSV
            with open(csv_file, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Timestamp', 'X', 'Y', 'Width', 'Height', 'Extracted_Text']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(row_data)
            
            print(f"Extraction saved to {csv_file}")
        except Exception as e:
            print(f"Error saving to CSV: {str(e)}")
            messagebox.showerror("CSV Save Error", f"Could not save extraction to CSV:\n{str(e)}")
    
    def _extract_scan_square(self):
        """Extract text from the current square using ML Kit style preprocessing"""
        try:
            import cv2
            import numpy as np
            import pytesseract
            import time
            from PIL import ImageGrab
            
            x = int(self.scan_x_pos_var.get())
            y = int(self.scan_y_pos_var.get())
            w = int(self.scan_width_var.get())
            h = int(self.scan_height_var.get())
            
            if w < 20 or h < 20:
                messagebox.showwarning("Invalid Dimensions", "Square must be at least 20x20 pixels")
                return
            
            # Calculate capture region (top-left corner)
            left = x - w // 2
            top = y - h // 2
            right = left + w
            bottom = top + h
            
            # Capture the square region
            screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
            
            # Convert PIL Image to numpy array
            screenshot_array = np.array(screenshot)
            
            # Convert to OpenCV format (BGR)
            image = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2BGR)
            
            # Apply ML Kit style preprocessing
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Enhanced contrast and brightness for better text detection
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Apply thresholding for crisp text edges
            _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Normalize to 0-255 range
            normalized = cv2.normalize(thresh, None, 0, 255, cv2.NORM_MINMAX)
            
            # Ultra high-resolution upscaling for better OCR accuracy (8x upscaling for small text)
            height_img, width_img = image_rgb.shape[:2]
            scale_factor = 8.0  # 8x upscaling for maximum OCR accuracy with small text
            upscaled_height = int(height_img * scale_factor)
            upscaled_width = int(width_img * scale_factor)
            image_rgb = cv2.resize(image_rgb, (upscaled_width, upscaled_height), interpolation=cv2.INTER_CUBIC)
            
            # Convert to PIL for Tesseract
            pil_image = Image.fromarray(image_rgb)
            
            # Extract text using selected OCR model
            text = self._extract_with_ocr_model(pil_image, image_rgb)
            
            # Get current datetime for CSV storage
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save to CSV
            self._save_extraction_to_csv(text, timestamp)
            
            # Update output in GUI
            time_display = datetime.now().strftime("%H:%M:%S")
            output = f"[{time_display}] Extracted:\n{text}\n\n" if text.strip() else f"[{time_display}] No text detected\n\n"
            
            self.scan_output_text.insert(tk.END, output)
            self.scan_output_text.see(tk.END)
            
            print(f"Text extracted and saved: {text[:50]}...") if text else print("No text detected")
            
        except ImportError as e:
            messagebox.showerror("Missing Dependency", f"Please install required packages:\npip install pytesseract opencv-python Pillow numpy")
        except Exception as e:
            messagebox.showerror("Extraction Error", f"Error: {str(e)}")
    
    def _extract_with_ocr_model(self, pil_image, cv_image):
        """Extract text using the selected OCR model"""
        model = self.scan_ocr_model_var.get()
        
        try:
            if model == "Tesseract":
                return self._extract_tesseract(pil_image)
            elif model == "PaddleOCR":
                return self._extract_paddle_ocr(cv_image)
            elif model == "Doctr":
                return self._extract_doctr(pil_image)
            else:
                return self._extract_tesseract(pil_image)  # Default fallback
        except Exception as e:
            print(f"Error with {model}: {str(e)}. Falling back to Tesseract...")
            try:
                return self._extract_tesseract(pil_image)
            except:
                return ""
    
    def _extract_tesseract(self, pil_image):
        """Extract text using Tesseract OCR"""
        import pytesseract
        text = pytesseract.image_to_string(pil_image)
        return text.strip()
    
    def _extract_paddle_ocr(self, cv_image):
        """Extract text using PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            
            # Initialize PaddleOCR (downloads model on first use)
            # Suppress verbosity output
            import os
            os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
            
            ocr = PaddleOCR(use_angle_cls=True, lang='en')
            
            # Perform OCR on the image
            result = ocr.ocr(cv_image, cls=True)
            
            # Extract and concatenate all detected text
            text_lines = []
            for line in result:
                if line:
                    for word_info in line:
                        text_lines.append(word_info[1][0])  # word_info[1][0] is the text
            
            return '\n'.join(text_lines)
        except ImportError as e:
            raise ImportError(f"PaddleOCR not installed: {e}")
        except Exception as e:
            raise Exception(f"PaddleOCR error: {e}")
    
    def _extract_docext(self, pil_image):
        """Extract text using Docext (document text recognition)"""
        try:
            from doctr.io import DocumentFile
            from doctr.models import ocr_predictor
            
            # Load pretrained model
            model = ocr_predictor(pretrained=True)
            
            # Convert PIL to bytes for docext
            import io
            byte_stream = io.BytesIO()
            pil_image.save(byte_stream, format='PNG')
            byte_stream.seek(0)
            
            # Create document and perform OCR
            doc = DocumentFile.from_pdf(byte_stream) if hasattr(DocumentFile, 'from_pdf') else DocumentFile.from_images([byte_stream])
            result = model(doc)
            
            # Extract text
            text_lines = []
            for page in result.pages:
                for block in page.blocks:
                    for line in block.lines:
                        for word in line.words:
                            text_lines.append(word.value)
            
            return ' '.join(text_lines)
        except ImportError as e:
            raise ImportError(f"Docext not installed: {e}")
        except Exception as e:
            raise Exception(f"Docext error: {e}")
    
    def _on_stop_condition_change(self, event=None):
        """Handle stop condition change"""
        condition = int(self.stop_condition_var.get() if self.stop_condition_var.get().isdigit() else 0)
        
        if condition == 0:
            self.stop_value_label.config(text="(disabled)")
        elif condition == 1:
            self.stop_value_label.config(text="(seconds)")
        else:  # condition == 2
            self.stop_value_label.config(text="(clicks)")
    
    def _start_clicking(self):
        """Start the clicking automation with the selected setup (digit 0-9 or match)"""
        try:
            selected_setup = self.selected_setup_var.get()
            
            # Get position based on selected setup
            if selected_setup == "match":
                if not self.match_setup_status:
                    messagebox.showwarning("Setup Required", "Please set up MATCH first")
                    return
                x_pos = int(self.match_x_pos_var.get())
                y_pos = int(self.match_y_pos_var.get())
            else:
                # It's a digit (0-9)
                digit_num = int(selected_setup)
                if not self.digit_setup_status.get(digit_num, False):
                    messagebox.showwarning("Setup Required", f"Please set up Digit {digit_num} first")
                    return
                # Get position from the stored digit position
                x_pos = self.digit_positions[digit_num]["x"]
                y_pos = self.digit_positions[digit_num]["y"]
            
            interval = int(self.interval_var.get())
            stop_cond = int(self.stop_condition_var.get() if self.stop_condition_var.get().isdigit() else 0)
            stop_val = int(self.stop_value_var.get())
            anti_det = self.anti_detection_var.get()
            offset = int(self.offset_var.get())
            
            # Configure click engine with selected position
            self.click_engine.configure(
                x_pos=x_pos,
                y_pos=y_pos,
                click_interval=interval,
                stop_condition=StopCondition(stop_cond),
                stop_value=stop_val,
                anti_detection=anti_det,
                click_type=ClickType.SINGLE_CLICK
            )
            self.click_engine.anti_detection_offset = offset
            
            # Start clicking
            if self.click_engine.start_clicking():
                self.status_label.config(text="RUNNING", fg='green')
                self.start_btn.pack_forget()  # Hide START button
                self.pause_btn.pack(side=tk.LEFT, padx=5, expand=True)  # Show PAUSE
                self.stop_btn.pack(side=tk.LEFT, padx=5, expand=True)   # Show STOP
            else:
                messagebox.showerror("Error", "Could not start clicking")
        
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error starting clicking: {e}")
    
    def _pause_clicking(self):
        """Pause the clicking automation"""
        if self.click_engine.pause_clicking():
            self.status_label.config(text="PAUSED", fg='orange')
            self.pause_btn.config(text="▶ RESUME", command=self._resume_clicking)
    
    def _resume_clicking(self):
        """Resume paused clicking"""
        if self.click_engine.resume_clicking():
            self.status_label.config(text="RUNNING", fg='green')
            self.pause_btn.config(text="⏸ PAUSE", command=self._pause_clicking)
    
    def _stop_clicking(self):
        """Stop the clicking automation and reset everything"""
        if self.click_engine.stop_clicking():
            self.status_label.config(text="STOPPED", fg='red')
            self.pause_btn.pack_forget()  # Hide PAUSE
            self.stop_btn.pack_forget()   # Hide STOP
            self.start_btn.pack(side=tk.LEFT, padx=5, expand=True)  # Show START
            self.pause_btn.config(text="⏸ PAUSE", command=self._pause_clicking)  # Reset pause button text
        
        # Destroy indicator windows
        if hasattr(self, 'indicator_windows'):
            for window in self.indicator_windows:
                try:
                    window.destroy()
                except:
                    pass
            self.indicator_windows = []
        
        # Reset statistics labels directly
        self.clicks_label.config(text="0")
        self.elapsed_label.config(text="0.0s")
    
    def _update_digit_button_color(self, digit_num):
        """Update digit button color to green when setup is complete"""
        if digit_num in self.digit_buttons:
            self.digit_buttons[digit_num].config(bg='#2ecc71')  # Green
    
    def _update_match_button_color(self):
        """Update Match button color to green when setup is complete"""
        if self.match_btn:
            self.match_btn.config(bg='#2ecc71')  # Green
    
    def _update_input_selector_button_color(self):
        """Update Input selector button color to green when setup is complete"""
        if self.input_selector_btn:
            self.input_selector_btn.config(bg='#2ecc71')  # Green
    
    def _on_click(self, data):
        """Callback when a click occurs"""
        self.root.after(0, lambda: self._update_stats())
    
    def _on_stop(self, data):
        """Callback when clicking stops"""
        self.root.after(0, self._stop_clicking)
    
    def _on_tick(self, data):
        """Callback for periodic updates"""
        self.root.after(0, lambda: self._update_stats())
    
    def _update_stats(self):
        """Update statistics display"""
        stats = self.click_engine.get_stats()
        self.clicks_label.config(text=str(stats.total_clicks))
        self.elapsed_label.config(text=f"{stats.elapsed_time:.1f}s")
    
    def _save_settings(self):
        """Save current settings"""
        try:
            interval = int(self.interval_var.get())
            stop_cond = int(self.stop_condition_var.get() if self.stop_condition_var.get().isdigit() else 0)
            stop_val = int(self.stop_value_var.get())
            anti_det = self.anti_detection_var.get()
            offset = int(self.offset_var.get())
            
            settings = ClickSettings(
                click_interval=interval,
                stop_condition=stop_cond,
                stop_value=stop_val,
                anti_detection=anti_det,
                anti_detection_max_offset=offset
            )
            
            if self.config_manager.save_settings(settings):
                pass  # Settings saved
            else:
                messagebox.showerror("Error", "Could not save settings")
        except ValueError:
            messagebox.showerror("Input Error", "Invalid input values")
    
    def _refresh_config_list(self):
        """Refresh the configuration list"""
        self.config_listbox.delete(0, tk.END)
        targets = self.config_manager.load_all_targets()
        for target in targets:
            self.config_listbox.insert(tk.END, f"{target.id}: {target.name} ({target.x_pos}, {target.y_pos})")
    
    def _load_selected_config(self):
        """Load selected configuration"""
        selection = self.config_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection", "Please select a configuration")
            return
        
        targets = self.config_manager.load_all_targets()
        target = targets[selection[0]]
        
        self.x_pos_var.set(str(target.x_pos))
        self.y_pos_var.set(str(target.y_pos))
        self.interval_var.set(str(target.click_interval))
        self.stop_condition_var.set(str(target.stop_condition))
        self.stop_value_var.set(str(target.stop_value))
        self.anti_detection_var.set(target.anti_detection)
        
        self.current_config = target
    
    def _save_config_dialog(self):
        """Save current settings as new configuration"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Save Configuration")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Configuration Name:").pack(pady=10)
        name_entry = tk.Entry(dialog, width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        def save_it():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Please enter a name")
                return
            
            try:
                target_id = self.config_manager.get_next_target_id()
                target = ClickTarget(
                    id=target_id,
                    name=name,
                    x_pos=int(self.x_pos_var.get()),
                    y_pos=int(self.y_pos_var.get()),
                    click_interval=int(self.interval_var.get()),
                    stop_condition=int(self.stop_condition_var.get() if self.stop_condition_var.get().isdigit() else 0),
                    stop_value=int(self.stop_value_var.get()),
                    anti_detection=self.anti_detection_var.get()
                )
                
                if self.config_manager.save_target(target):
                    self._refresh_config_list()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Could not save configuration")
            except ValueError:
                messagebox.showerror("Error", "Invalid input values")
        
        tk.Button(dialog, text="Save", command=save_it, bg='#27ae60', fg='white').pack(pady=10)
    
    def _delete_selected_config(self):
        """Delete selected configuration"""
        selection = self.config_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection", "Please select a configuration to delete")
            return
        
        targets = self.config_manager.load_all_targets()
        target = targets[selection[0]]
        
        if messagebox.askyesno("Confirm", f"Delete configuration '{target.name}'?"):
            if self.config_manager.delete_target(target.id):
                self._refresh_config_list()
                messagebox.showinfo("Success", "Configuration deleted")
            else:
                messagebox.showerror("Error", "Could not delete configuration")
    
    def _export_config(self):
        """Export selected configuration to CSV"""
        selection = self.config_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection", "Please select a configuration to export")
            return
        
        targets = self.config_manager.load_all_targets()
        target = targets[selection[0]]
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"{target.name}.csv"
        )
        
        if file_path:
            if self.config_manager.export_target_to_csv(target.id, file_path):
                messagebox.showinfo("Success", f"Configuration exported to {file_path}")
            else:
                messagebox.showerror("Error", "Could not export configuration")
    
    def _import_config(self):
        """Import configuration from CSV"""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.config_manager.import_target_from_csv(file_path):
                self._refresh_config_list()
                messagebox.showinfo("Success", "Configuration imported successfully")
            else:
                messagebox.showerror("Error", "Could not import configuration")
    
    def _load_config(self):
        """Load last configuration on startup"""
        settings = self.config_manager.load_settings()
        self.interval_var.set(str(settings.click_interval))
        self.stop_condition_var.set(str(settings.stop_condition))
        self.stop_value_var.set(str(settings.stop_value))
        self.anti_detection_var.set(settings.anti_detection)
        self.offset_var.set(str(settings.anti_detection_max_offset))


def main():
    """Main entry point"""
    root = tk.Tk()
    app = AutoClickerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
