# ---
# KazLabs Media Group
# Made with ♥ by Liam Sorensen - AI Assisted by Cursor.AI.
# Version 0.1.4 - 2025-02-25
# ---

import os
import sys
import json
from logger import Logger

class StartupChecker:
    def __init__(self):
        self.logger = Logger("StartupChecker")
        self.exe_path = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
        
    def check_directory_clean(self):
        """Check if directory is clean except for allowed files"""
        try:
            allowed_files = ['config.json', 'KazLabs-AutoClicker.exe', 'icon.ico']
            directory_contents = os.listdir(self.exe_path)
            
            unexpected_files = [f for f in directory_contents if f not in allowed_files]
            
            if unexpected_files:
                self.logger.warning(f"Unexpected files found in directory: {', '.join(unexpected_files)}")
                return False
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking directory: {str(e)}")
            return False
    
    def ensure_config_exists(self):
        """Ensure config.json exists, create with defaults if missing"""
        config_path = os.path.join(self.exe_path, 'config.json')
        try:
            if not os.path.exists(config_path):
                default_config = {            
                    "default_min_interval": 500,
                    "default_max_interval": 1500,
                    "default_hotkey": "ctrl+shift+a",
                    "turbo_warning_shown": True,
                    "window_title": "KazLabs AutoClicker",
                    "dark_mode": True,
                    "theme": {
                        "dark": {
                            "background": "#0d101d",
                            "foreground": "#eeeeee",
                            "accent": "#0d1f4e"
                        },
                        "light": {
                            "background": "#cccccc",
                            "foreground": "#333333",
                            "accent": "#5882ee"
                        }
                    }
                }
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=4)
                self.logger.info("Created default config.json")
            return True
            
        except Exception as e:
            self.logger.error(f"Error ensuring config exists: {str(e)}")
            return False
    
    def ensure_log_directory(self):
        """Ensure log directory exists"""
        try:
            log_dir = os.path.join("C:", "Logs", "AutoClicker")
            os.makedirs(log_dir, exist_ok=True)
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating log directory: {str(e)}")
            return False
    
    def run_all_checks(self):
        """Run all startup checks"""
        try:
            checks = {
                "Directory Clean": self.check_directory_clean(),
                "Config Exists": self.ensure_config_exists(),
                "Log Directory": self.ensure_log_directory()
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                self.logger.info("All startup checks passed successfully")
            else:
                failed_checks = [name for name, passed in checks.items() if not passed]
                self.logger.warning(f"Some checks failed: {', '.join(failed_checks)}")
            
            return all_passed
            
        except Exception as e:
            self.logger.error(f"Error running startup checks: {str(e)}")
            return False 