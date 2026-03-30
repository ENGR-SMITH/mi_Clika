# New _build_control_panel method - Copy this to replace the old one
def _build_control_panel(self):
    """Build the main control panel with improved styling - includes digit buttons, Match/Differ, Input section, and 2/1 targets"""
    # Create a scrollable frame
    canvas = tk.Canvas(self.control_frame, bg='#f5f5f5', highlightthickness=0)
    scrollbar = tk.Scrollbar(self.control_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='#f5f5f5')
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Status section with prominent display
    status_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.FLAT, bd=1)
    status_frame.pack(fill=tk.X, pady=(15, 15), padx=15)
    status_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
    
    status_label_title = tk.Label(
        status_frame,
        text="STATUS",
        font=("Arial", 9, "bold"),
        bg='white',
        fg='#666666'
    )
    status_label_title.pack(anchor=tk.W, padx=15, pady=(10, 5))
    
    self.status_label = tk.Label(
        status_frame,
        text="STOPPED",
        font=("Arial", 16, "bold"),
        fg='#e74c3c',
        bg='white'
    )
    self.status_label.pack(anchor=tk.W, padx=15, pady=(5, 10))
    
    # DIGIT BUTTONS section (0-9)
    digit_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.FLAT, bd=1)
    digit_frame.pack(fill=tk.X, pady=(0, 15), padx=15)
    digit_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
    
    digit_label = tk.Label(
        digit_frame,
        text="DIGIT SETUP (0-9)",
        font=("Arial", 9, "bold"),
        bg='white',
        fg='#666666'
    )
    digit_label.pack(anchor=tk.W, padx=15, pady=(10, 10))
    
    # Digit buttons grid
    digits_container = tk.Frame(digit_frame, bg='white')
    digits_container.pack(fill=tk.X, padx=15, pady=(0, 10))
    
    def setup_digit(digit_num):
        """Setup a digit button"""
        def on_point_selected(x, y):
            self.digit_setup_status[digit_num] = True
            self._update_digit_button_color(digit_num)
            self.root.after(0, lambda: self._show_point_indicator(x, y, digit_num + 10))  # Use digit_num + 10 as target_num for storage
        
        selector = PointSelectorOverlay(on_point_selected)
        selector.show()
    
    digit_buttons_row_frames = []
    for row in range(2):  # 2 rows for 10 buttons
        row_frame = tk.Frame(digits_container, bg='white')
        row_frame.pack(fill=tk.X, pady=3)
        for col in range(5):
            digit_num = row * 5 + col
            btn = tk.Button(
                row_frame,
                text=str(digit_num),
                command=lambda d=digit_num: setup_digit(d),
                font=("Arial", 10, "bold"),
                bg='#e74c3c',  # Red initially
                fg='white',
                relief=tk.FLAT,
                padx=15,
                pady=5,
                cursor="hand2",
                width=5
            )
            btn.pack(side=tk.LEFT, padx=3, expand=True)
            self.digit_buttons[digit_num] = btn
    
    # MATCH and DIFFER buttons
    match_differ_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.FLAT, bd=1)
    match_differ_frame.pack(fill=tk.X, pady=(0, 15), padx=15)
    match_differ_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
    
    match_label = tk.Label(
        match_differ_frame,
        text="MATCH & DIFFER SETUP",
        font=("Arial", 9, "bold"),
        bg='white',
        fg='#666666'
    )
    match_label.pack(anchor=tk.W, padx=15, pady=(10, 10))
    
    match_differ_buttons = tk.Frame(match_differ_frame, bg='white')
    match_differ_buttons.pack(fill=tk.X, padx=15, pady=(0, 10))
    
    def setup_match():
        """Setup Match button"""
        def on_point_selected(x, y):
            self.match_setup_status = True
            self.match_x_pos_var.set(str(x))
            self.match_y_pos_var.set(str(y))
            self._update_match_button_color()
            self.root.after(0, lambda: self._show_point_indicator(x, y, 999))  # Special target_num for Match
        
        selector = PointSelectorOverlay(on_point_selected)
        selector.show()
    
    def setup_differ():
        """Setup Differ button"""
        def on_point_selected(x, y):
            self.differ_setup_status = True
            self.differ_x_pos_var.set(str(x))
            self.differ_y_pos_var.set(str(y))
            self._update_differ_button_color()
            self.root.after(0, lambda: self._show_point_indicator(x, y, 998))  # Special target_num for Differ
        
        selector = PointSelectorOverlay(on_point_selected)
        selector.show()
    
    self.match_btn = tk.Button(
        match_differ_buttons,
        text="SET MATCH",
        command=setup_match,
        font=("Arial", 11, "bold"),
        bg='#e74c3c',  # Red initially
        fg='white',
        relief=tk.FLAT,
        padx=20,
        pady=8,
        cursor="hand2"
    )
    self.match_btn.pack(side=tk.LEFT, padx=5, expand=True)
    
    self.differ_btn = tk.Button(
        match_differ_buttons,
        text="SET DIFFER",
        command=setup_differ,
        font=("Arial", 11, "bold"),
        bg='#e74c3c',  # Red initially
        fg='white',
        relief=tk.FLAT,
        padx=20,
        pady=8,
        cursor="hand2"
    )
    self.differ_btn.pack(side=tk.LEFT, padx=5, expand=True)
    
    # Current target position section with toggle (2 or 1)
    target_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.FLAT, bd=1)
    target_frame.pack(fill=tk.X, pady=(0, 15), padx=15)
    target_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
    
    # Header with toggle button
    header_frame = tk.Frame(target_frame, bg='white')
    header_frame.pack(fill=tk.X, padx=15, pady=(10, 10))
    
    target_label = tk.Label(
        header_frame,
        text="TARGET POSITIONS",
        font=("Arial", 9, "bold"),
        bg='white',
        fg='#666666'
    )
    target_label.pack(side=tk.LEFT)
    
    # Create switch canvas for 2/1 toggle
    switch_canvas = tk.Canvas(header_frame, width=80, height=28, bg='white', highlightthickness=0, cursor="hand2", relief=tk.FLAT)
    switch_canvas.pack(side=tk.RIGHT, padx=10)
    
    # Switch-style toggle for number of targets (2 or 1)
    def draw_switch():
        is_one = self.num_targets_var.get() == "1"
        switch_canvas.delete("all")
        
        # Draw switch background
        bg_color = '#2ecc71' if is_one else '#7f8c8d'
        switch_canvas.create_rectangle(4, 4, 76, 24, fill=bg_color, outline=bg_color, tags="bg")
        
        # Draw switch circle
        circle_x = 56 if is_one else 16
        switch_canvas.create_oval(circle_x - 8, 3, circle_x + 8, 25, fill='white', outline='#ddd', width=1, tags="circle")
        
        # Draw labels on the switch
        switch_canvas.create_text(16, 14, text="2", font=("Arial", 9, "bold"), fill='white' if not is_one else '#bbb', tags="label2")
        switch_canvas.create_text(64, 14, text="1", font=("Arial", 9, "bold"), fill='white' if is_one else '#bbb', tags="label1")
    
    def toggle_targets(event=None):
        current = self.num_targets_var.get()
        new_val = "1" if current == "2" else "2"
        self.num_targets_var.set(new_val)
        update_target_display()
        draw_switch()
    
    switch_canvas.bind("<Button-1>", toggle_targets)
    draw_switch()
    
    # Container for target positions
    targets_container = tk.Frame(target_frame, bg='white')
    targets_container.pack(fill=tk.X, padx=15, pady=(0, 10))
    
    # Target 1
    target1_frame = tk.Frame(targets_container, bg='white')
    target1_frame.pack(fill=tk.X, pady=5)
    tk.Label(target1_frame, text="Target 1 -", font=("Arial", 10, "bold"), bg='white', fg='#2980b9').pack(side=tk.LEFT, padx=(0, 5))
    tk.Label(target1_frame, text="X:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 5))
    x1_entry = tk.Entry(target1_frame, textvariable=self.target1_x_var, width=10, font=("Arial", 10))
    x1_entry.pack(side=tk.LEFT, padx=5)
    tk.Label(target1_frame, text="Y:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(15, 5))
    y1_entry = tk.Entry(target1_frame, textvariable=self.target1_y_var, width=10, font=("Arial", 10))
    y1_entry.pack(side=tk.LEFT, padx=5)
    set_1_btn = tk.Button(
        target1_frame,
        text="SET",
        command=lambda: self._open_point_selector(1),
        bg='#3498db',
        fg='white',
        font=("Arial", 9, "bold"),
        relief=tk.FLAT,
        padx=10,
        pady=3,
        cursor="hand2"
    )
    set_1_btn.pack(side=tk.LEFT, padx=(15, 5))
    self.target_frames.append(target1_frame)
    
    # Target 2
    target2_frame = tk.Frame(targets_container, bg='white')
    target2_frame.pack(fill=tk.X, pady=5)
    tk.Label(target2_frame, text="Target 2 -", font=("Arial", 10, "bold"), bg='white', fg='#2980b9').pack(side=tk.LEFT, padx=(0, 5))
    tk.Label(target2_frame, text="X:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 5))
    x2_entry = tk.Entry(target2_frame, textvariable=self.target2_x_var, width=10, font=("Arial", 10))
    x2_entry.pack(side=tk.LEFT, padx=5)
    tk.Label(target2_frame, text="Y:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(15, 5))
    y2_entry = tk.Entry(target2_frame, textvariable=self.target2_y_var, width=10, font=("Arial", 10))
    y2_entry.pack(side=tk.LEFT, padx=5)
    set_2_btn = tk.Button(
        target2_frame,
        text="SET",
        command=lambda: self._open_point_selector(2),
        bg='#3498db',
        fg='white',
        font=("Arial", 9, "bold"),
        relief=tk.FLAT,
        padx=10,
        pady=3,
        cursor="hand2"
    )
    set_2_btn.pack(side=tk.LEFT, padx=(15, 5))
    self.target_frames.append(target2_frame)
    
    def update_target_display():
        """Show or hide target frames based on selected number"""
        num = int(self.num_targets_var.get())
        self.target_frames[0].pack(fill=tk.X, pady=5)  # Always show target 1
        if num == 2:
            self.target_frames[1].pack(fill=tk.X, pady=5)  # Show target 2
        else:
            self.target_frames[1].pack_forget()  # Hide target 2
    
    # INPUT SECTION (integrated into Control Panel)
    input_section_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.FLAT, bd=1)
    input_section_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15), padx=15)
    input_section_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
    
    input_sec_label = tk.Label(
        input_section_frame,
        text="INPUT SECTION",
        font=("Arial", 9, "bold"),
        bg='white',
        fg='#666666'
    )
    input_sec_label.pack(anchor=tk.W, padx=15, pady=(10, 10))
    
    # Input target position
    pos_input_frame = tk.Frame(input_section_frame, bg='white')
    pos_input_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
    
    tk.Label(pos_input_frame, text="X:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 5))
    x_input_entry = tk.Entry(pos_input_frame, textvariable=self.input_x_pos_var, width=10, font=("Arial", 10))
    x_input_entry.pack(side=tk.LEFT, padx=5)
    
    tk.Label(pos_input_frame, text="Y:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(15, 5))
    y_input_entry = tk.Entry(pos_input_frame, textvariable=self.input_y_pos_var, width=10, font=("Arial", 10))
    y_input_entry.pack(side=tk.LEFT, padx=5)
    
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
    
    # Text input area
    text_label = tk.Label(
        input_section_frame,
        text="Text to Type:",
        font=("Arial", 9, "bold"),
        bg='white',
        fg='#666666'
    )
    text_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    
    self.input_text_area = tk.Text(
        input_section_frame,
        font=("Arial", 10),
        height=3,
        width=50,
        wrap=tk.WORD,
        fg='#333333'
    )
    self.input_text_area.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
    
    # Input control buttons
    input_btn_frame = tk.Frame(input_section_frame, bg='white')
    input_btn_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
    
    self.input_start_btn = tk.Button(
        input_btn_frame,
        text="START INPUT",
        command=self._start_input_automation,
        font=("Arial", 10, "bold"),
        bg='#27ae60',
        fg='white',
        relief=tk.FLAT,
        padx=15,
        pady=5,
        cursor="hand2"
    )
    self.input_start_btn.pack(side=tk.LEFT, padx=5)
    
    self.input_stop_btn = tk.Button(
        input_btn_frame,
        text="STOP INPUT",
        command=self._stop_input_automation,
        font=("Arial", 10, "bold"),
        bg='#e74c3c',
        fg='white',
        relief=tk.FLAT,
        padx=15,
        pady=5,
        cursor="hand2"
    )
    self.input_stop_btn.pack_forget()
    
    # Statistics section
    stats_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.FLAT, bd=1)
    stats_frame.pack(fill=tk.X, pady=(0, 15), padx=15)
    stats_frame.configure(highlightbackground='#e0e0e0', highlightthickness=1)
    
    stats_label = tk.Label(
        stats_frame,
        text="STATISTICS",
        font=("Arial", 9, "bold"),
        bg='white',
        fg='#666666'
    )
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
    
    self.start_btn = tk.Button(
        button_frame,
        text="START",
        command=self._start_clicking,
        font=("Arial", 12, "bold"),
        bg='#27ae60',
        fg='white',
        relief=tk.FLAT,
        padx=20,
        pady=10,
        cursor="hand2"
    )
    self.start_btn.pack_forget()
    
    self.pause_btn = tk.Button(
        button_frame,
        text="PAUSE",
        command=self._pause_clicking,
        font=("Arial", 12, "bold"),
        bg='#f39c12',
        fg='white',
        relief=tk.FLAT,
        padx=20,
        pady=10,
        cursor="hand2"
    )
    self.pause_btn.pack_forget()
    
    self.stop_btn = tk.Button(
        button_frame,
        text="STOP",
        command=self._stop_clicking,
        font=("Arial", 12, "bold"),
        bg='#e74c3c',
        fg='white',
        relief=tk.FLAT,
        padx=20,
        pady=10,
        cursor="hand2"
    )
    self.stop_btn.pack_forget()
