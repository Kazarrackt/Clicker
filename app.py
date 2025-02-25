# ---
# KazLabs Media Group
# Made with ♥ by Liam Sorensen - AI Assisted by Cursor.AI.
# Version 0.1.0 - 2024-03-19
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
        
        self.create_widgets()
        self.create_status_bar()
        self.update_hotkey()
        self.update_cps()
        
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
        ttk.Checkbutton(frame, text="Turbo Mode (Ultra Fast)", 
                       variable=self.turbo_var, 
                       command=self.toggle_turbo_mode).grid(row=3, column=0, columnspan=2)
        
        self.toggle_button = ttk.Button(frame, text="Start", command=self.toggle)
        self.toggle_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.update_hotkey_button = ttk.Button(frame, text="Update Hotkey", command=self.update_hotkey)
        self.update_hotkey_button.grid(row=5, column=0, columnspan=2, pady=10)
        
        for child in frame.winfo_children():
            child.grid_configure(padx=5, pady=5)
        
    def create_status_bar(self):
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Version label (left)
        self.version_label = ttk.Label(self.status_bar, text="v0.1.0")
        self.version_label.pack(side=tk.LEFT, padx=5)
        
        # CPS label (center)
        self.cps_label = ttk.Label(self.status_bar, text="0.0 CPS")
        self.cps_label.pack(side=tk.LEFT, expand=True)
        
        # Copyright label (right)
        self.copyright_label = ttk.Label(self.status_bar, text="© 2025 - Kazlabs")
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
        self.is_turbo = self.turbo_var.get()
        if self.is_turbo:
            self.logger.info("Turbo mode enabled")
            self.min_interval.set(self.config["turbo_min_interval"])
            self.max_interval.set(self.config["turbo_max_interval"])
        else:
            self.logger.info("Turbo mode disabled")
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
    
    def auto_click(self):
        click_errors = 0  # Track consecutive errors
        while self.is_running:
            try:
                if click_errors > 5:  # Stop if too many errors occur
                    self.logger.error("Too many consecutive click errors, stopping auto-clicker")
                    self.is_running = False
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error", "Auto-clicking stopped due to too many errors"))
                    break
                    
                interval = random.uniform(self.min_interval.get(), self.max_interval.get()) / 1000.0
                time.sleep(interval)
                
                # Check if mouse is in a corner (failsafe)
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
                time.sleep(1)  # Wait a bit before retrying

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = AutoClicker(root)
        root.mainloop()
    except Exception as e:
        Logger("AutoClicker").error(f"Fatal error: {str(e)}")
        sys.exit(1)