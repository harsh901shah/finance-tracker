"""
Centralized logging system for the finance tracker application
"""
import logging
import streamlit as st
from datetime import datetime
import os

class AppLogger:
    """Centralized logging utility"""
    
    _logger = None
    
    @classmethod
    def get_logger(cls):
        """Get or create the application logger"""
        if cls._logger is None:
            cls._logger = cls._setup_logger()
        return cls._logger
    
    @classmethod
    def _setup_logger(cls):
        """Setup the logger with file and console handlers"""
        logger = logging.getLogger('finance_tracker')
        logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    @classmethod
    def log_error(cls, message, exception=None, show_user=True):
        """Log error and optionally show to user"""
        logger = cls.get_logger()
        
        if exception:
            logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            logger.error(message)
        
        if show_user:
            st.error(f"⚠️ {message}")
    
    @classmethod
    def log_warning(cls, message, show_user=False):
        """Log warning and optionally show to user"""
        logger = cls.get_logger()
        logger.warning(message)
        
        if show_user:
            st.warning(f"⚠️ {message}")
    
    @classmethod
    def log_info(cls, message):
        """Log info message"""
        logger = cls.get_logger()
        logger.info(message)
    
    @classmethod
    def log_debug(cls, message):
        """Log debug message"""
        logger = cls.get_logger()
        logger.debug(message)