# ---
# KazLabs Media Group
# Made with ♥ by Liam Sorensen - AI Assisted by Cursor.AI.
# Version 0.1.4 - 2025-02-25
# ---

import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import threading
import random
import time
import keyboard
import json
from logger import Logger
import sys
from datetime import datetime, timedelta
from startup_checks import StartupChecker
import os
import tkinter.font as tkFont
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from itertools import cycle

class AutoClicker:
    def __init__(self, root):
        self.logger = Logger("AutoClicker")
        self.logger.info("Initializing AutoClicker")
        
        # Run startup checks
        checker = StartupChecker()
        if not checker.run_all_checks():
            self.logger.error("Startup checks failed")
            messagebox.showwarning("Warning", 
                "Some startup checks failed. The application may not work correctly.\n"
                "Please check the logs for more information.")
        
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            messagebox.showerror("Error", "Failed to load configuration!")
            sys.exit(1)
            
        self.root = root
        self.root.title(self.config["window_title"])
        
        # Set window icon
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)), 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                self.logger.warning("Icon file not found")
        except Exception as e:
            self.logger.error(f"Failed to set window icon: {str(e)}")
        
        self.is_running = False
        self.is_turbo = False
        self.min_interval = tk.DoubleVar(value=self.config["default_min_interval"])
        self.max_interval = tk.DoubleVar(value=self.config["default_max_interval"])
        self.hotkey = tk.StringVar(value=self.config["default_hotkey"])
        self.current_hotkey = None
        
        self.click_count = 0
        self.last_click_time = datetime.now()
        self.clicks_per_second = 0
        
        # Configure error handling for pyautogui
        pyautogui.FAILSAFE = True
        
        # Oh look, we're setting up themes... because apparently light mode wasn't painful enough
        self.style = ttk.Style()
        self.dark_mode = tk.BooleanVar(value=self.config.get("dark_mode", True))
        self.apply_theme()
        
        # For turbo mode threading
        self.num_threads = multiprocessing.cpu_count() * 2  # Because why not use ALL the cores
        self.thread_pool = None
        self.click_positions = cycle([(0,0), (1,0), (-1,0), (0,1)])  # Micro-offsets to trick Windows
        
        self.create_widgets()
        self.create_status_bar()
        self.update_hotkey()
        self.update_cps()
        
    def apply_theme(self):
        """
        Applies theme because apparently black text on white background was too mainstream
        Is it messy? Yes. Does it work? Also yes.
        """
        try:
            theme = self.config["theme"]["dark" if self.dark_mode.get() else "light"]
            
            # Configure root window
            self.root.configure(bg=theme["background"])
            
            # Configure all ttk styles
            self.style.configure("TFrame", background=theme["background"])
            self.style.configure("TLabel", 
                background=theme["background"],
                foreground=theme["foreground"])
            self.style.configure("TButton",
                background=theme["accent"],
                foreground=theme["foreground"])
            self.style.configure("TCheckbutton",
                background=theme["background"],
                foreground=theme["foreground"])
            self.style.configure("TEntry",
                fieldbackground=theme["accent"],
                foreground="#111111")
            
            # Configure status bar specifically
            self.style.configure("Status.TFrame",
                background=theme["accent"])
            self.style.configure("Status.TLabel",
                background=theme["accent"],
                foreground=theme["foreground"])
            
            # Update status bar widgets if they exist
            if hasattr(self, 'status_bar'):
                self.status_bar.configure(style="Status.TFrame")
                self.version_label.configure(style="Status.TLabel")
                self.cps_label.configure(style="Status.TLabel")
                self.copyright_label.configure(style="Status.TLabel")
            
            # Save preference to config because we're nice like that
            self.config["dark_mode"] = self.dark_mode.get()
            try:
                with open('config.json', 'w') as f:
                    json.dump(self.config, f, indent=4)
            except Exception as e:
                self.logger.error(f"Failed to save theme preference because life is hard: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Theme application failed spectacularly: {str(e)}")
    
    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="Min Interval (milliseconds):").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.min_interval).grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(frame, text="Max Interval (milliseconds):").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.max_interval).grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(frame, text="Hotkey:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.hotkey).grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        # Add Turbo Mode checkbox
        self.turbo_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Turbo Mode (Fast)", 
                       variable=self.turbo_var, 
                       command=self.toggle_turbo_mode).grid(row=3, column=0, columnspan=2)
        
        self.toggle_button = ttk.Button(frame, text="Start", command=self.toggle)
        self.toggle_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.update_hotkey_button = ttk.Button(frame, text="Update Hotkey", command=self.update_hotkey)
        self.update_hotkey_button.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Add theme toggle because why not make this more complicated
        ttk.Checkbutton(frame, text="Dark Mode (For your precious eyes)", 
                       variable=self.dark_mode, 
                       command=self.apply_theme).grid(row=6, column=0, columnspan=2)
        
        for child in frame.winfo_children():
            child.grid_configure(padx=5, pady=5)
        
    def create_status_bar(self):
        self.status_bar = ttk.Frame(self.root, style="Status.TFrame")
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Version label (left)
        self.version_label = ttk.Label(self.status_bar, text="v0.1.3", style="Status.TLabel")
        self.version_label.pack(side=tk.LEFT, padx=5)
        
        # CPS label (center)
        self.cps_label = ttk.Label(self.status_bar, text="0.0 CPS", style="Status.TLabel")
        self.cps_label.pack(side=tk.LEFT, expand=True)
        
        # Copyright label (right)
        self.copyright_label = ttk.Label(self.status_bar, text="© 2025 - Kazlabs", style="Status.TLabel")
        self.copyright_label.pack(side=tk.RIGHT, padx=5)
    
    def update_cps(self):
        if self.is_running:
            current_time = datetime.now()
            time_diff = (current_time - self.last_click_time).total_seconds()
            
            if time_diff >= 1.0:
                self.clicks_per_second = self.click_count / time_diff
                self.click_count = 0
                self.last_click_time = current_time
                
            self.cps_label.config(text=f"{self.clicks_per_second:.1f} CPS")
        else:
            self.cps_label.config(text="0.0 CPS")
            
        self.root.after(100, self.update_cps)
    
    def toggle_turbo_mode(self):
        """
        Toggles turbo mode. Warning: May cause CPU meltdown, Windows crashes, 
        and your mouse driver to file for retirement.
        """
        self.is_turbo = self.turbo_var.get()
        if self.is_turbo:
            if not self.config.get("turbo_warning_shown", False):
                result = messagebox.askokcancel("Turbo Mode Warning",
                    "Warning: Turbo mode will attempt to achieve 1000+ CPS.\n\n" +
                    "Side effects may include:\n" +
                    "- CPU screaming in agony\n" +
                    "- Windows having an existential crisis\n" +
                    "- You questioning your life choices\n\n" +
                    "Continue anyway?")
                
                if not result:
                    self.turbo_var.set(False)
                    return
                    
                self.config["turbo_warning_shown"] = True
                with open('config.json', 'w') as f:
                    json.dump(self.config, f, indent=4)
            
            self.logger.warning("Turbo mode enabled - May God have mercy on your CPU")
            self.min_interval.set(self.config["turbo_min_interval"])
            self.max_interval.set(self.config["turbo_max_interval"])
        else:
            self.logger.info("Turbo mode disabled - Your CPU can rest now")
            self.min_interval.set(self.config["default_min_interval"])
            self.max_interval.set(self.config["default_max_interval"])
    
    def update_hotkey(self):
        try:
            if self.current_hotkey:
                keyboard.remove_hotkey(self.current_hotkey)
            self.current_hotkey = keyboard.add_hotkey(self.hotkey.get(), self.toggle)
            self.toggle_button.config(text=f"Start ({self.hotkey.get()})")
            self.logger.info(f"Hotkey updated to: {self.hotkey.get()}")
        except Exception as e:
            self.logger.error(f"Failed to update hotkey: {str(e)}")
            messagebox.showerror("Error", f"Failed to update hotkey: {str(e)}")
    
    def toggle(self):
        try:
            if self.is_running:
                self.is_running = False
                self.toggle_button.config(text=f"Start ({self.hotkey.get()})")
                self.logger.info("Auto-clicker stopped")
            else:
                self.is_running = True
                self.toggle_button.config(text=f"Stop ({self.hotkey.get()})")
                self.logger.info("Auto-clicker started")
                threading.Thread(target=self.auto_click, daemon=True).start()
        except Exception as e:
            self.logger.error(f"Error in toggle: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def turbo_click_worker(self):
        """
        Worker function that clicks like it's getting paid per click.
        Does this break Windows? Probably. Do we care? Not really.
        """
        try:
            while self.is_running:
                if not self.is_turbo:
                    break
                    
                # Add tiny offset to trick Windows into processing more clicks
                offset_x, offset_y = next(self.click_positions)
                x, y = pyautogui.position()
                pyautogui.click(x + offset_x, y + offset_y)
                self.click_count += 1
                
        except Exception as e:
            self.logger.error(f"Turbo worker died (RIP): {str(e)}")
    
    def auto_click(self):
        """
        The main clicking loop. Now with 1000% more clicking!
        Normal mode: Does what it says on the tin
        Turbo mode: Attempts to melt your CPU and possibly anger Windows
        """
        click_errors = 0  # Track consecutive errors. I'm not that persistent.
        
        if self.is_turbo:
            try:
                # Create thread pool for maximum clickage
                self.logger.warning("Initiating nuclear click protocol...")
                with ThreadPoolExecutor(max_workers=self.num_threads) as self.thread_pool:
                    # Launch ALL the threads!
                    futures = [self.thread_pool.submit(self.turbo_click_worker) 
                             for _ in range(self.num_threads)]
                    
                    # Wait for threads to finish (they won't) maybe...
                    for future in futures:
                        future.result()
                        
            except Exception as e:
                self.logger.error(f"Turbo mode crashed and burned: {str(e)}")
                self.is_running = False
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", "Turbo mode failed spectacularly!"))
                
        else:
            # Normal clicking mode... boring but reliable
            while self.is_running:
                try:
                    interval = random.uniform(self.min_interval.get(), self.max_interval.get()) / 1000.0
                    time.sleep(interval)
                    
                    # Check if mouse is in a corner (failsafe). Blame the cat.
                    x, y = pyautogui.position()
                    if x in [0, pyautogui.size().width-1] and y in [0, pyautogui.size().height-1]:
                        self.logger.warning("Failsafe triggered - mouse in corner")
                        self.is_running = False
                        self.root.after(0, lambda: messagebox.showwarning(
                            "Warning", "Auto-clicking stopped - mouse moved to corner"))
                        break
                    
                    pyautogui.click()
                    self.click_count += 1
                    click_errors = 0  # Reset error counter on successful click
                    
                except Exception as e:
                    self.logger.error(f"Error in auto_click: {str(e)}")
                    click_errors += 1
                    time.sleep(1)  # Wait a bit before retrying cause windows is a bitch and hates me. 

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = AutoClicker(root)
        root.mainloop()
    except Exception as e:
        Logger("AutoClicker").error(f"Fatal error: {str(e)}")
        sys.exit(1)