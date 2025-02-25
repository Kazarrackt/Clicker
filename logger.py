# ---
# KazLabs Media Group
# Made with ♥ by Liam Sorensen - AI Assisted by Cursor.AI.
# Version 0.1.4 - 2025-02-25
# ---

import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.join("C:", "Logs", "AutoClicker")
        os.makedirs(log_dir, exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(os.path.join(log_dir, "main.log"))
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def format_message(self, message):
        return message.replace("\n", " - ")
    
    def debug(self, message):
        self.logger.debug(self.format_message(message))
    
    def info(self, message):
        self.logger.info(self.format_message(message))
    
    def warning(self, message):
        self.logger.warning(self.format_message(message))
    
    def error(self, message):
        self.logger.error(self.format_message(message)) 