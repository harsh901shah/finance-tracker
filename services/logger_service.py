import logging
import os
from datetime import datetime
from typing import Optional

class LoggerService:
    """Centralized logging service for the application"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger instance by name
        
        Args:
            name: Logger name (usually module name)
            
        Returns:
            Logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Create handlers
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler(
            os.path.join(logs_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log"),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatters
        console_format = logging.Formatter('%(levelname)s - %(message)s')
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Set formatters
        console_handler.setFormatter(console_format)
        file_handler.setFormatter(file_format)
        
        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        # Store logger
        cls._loggers[name] = logger
        
        return logger