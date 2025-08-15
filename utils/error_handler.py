"""
Centralized error handling utilities for the Finance Tracker application.
"""
import logging
import streamlit as st
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling and user feedback utilities."""
    
    @staticmethod
    def handle_database_error(e: Exception, operation: str, user_message: str = None) -> bool:
        """Handle database-related errors with consistent logging and user feedback."""
        import sqlite3
        
        if isinstance(e, sqlite3.IntegrityError):
            logger.warning(f"Database integrity violation during {operation}: {str(e)}")
            st.warning(user_message or f"Data validation failed during {operation}")
            return False
        elif isinstance(e, sqlite3.OperationalError):
            logger.error(f"Database operation failed during {operation}: {str(e)}")
            st.error(user_message or f"Database operation failed. Please try again.")
            return False
        elif isinstance(e, sqlite3.DatabaseError):
            logger.error(f"Database error during {operation}: {str(e)}")
            st.error(user_message or f"Database error occurred. Please contact support.")
            return False
        else:
            logger.error(f"Unexpected error during {operation}: {str(e)}")
            st.error(user_message or f"An unexpected error occurred during {operation}")
            return False
    
    @staticmethod
    def handle_validation_error(e: Exception, operation: str) -> bool:
        """Handle validation errors with user-friendly messages."""
        logger.warning(f"Validation failed during {operation}: {str(e)}")
        st.error(str(e))
        return False
    
    @staticmethod
    def handle_json_error(e: Exception, operation: str) -> bool:
        """Handle JSON encoding/decoding errors."""
        import json
        
        if isinstance(e, json.JSONEncodeError):
            logger.error(f"JSON encoding failed during {operation}: {str(e)}")
            st.error("Invalid data format. Please check your input.")
        elif isinstance(e, json.JSONDecodeError):
            logger.warning(f"JSON decoding failed during {operation}: {str(e)}")
            st.warning("Corrupted data detected. Using default values.")
        else:
            logger.error(f"JSON error during {operation}: {str(e)}")
            st.error("Data processing error occurred.")
        return False
    
    @staticmethod
    def safe_execute(func: Callable, operation: str, default_return: Any = None, 
                    user_message: str = None) -> Any:
        """Safely execute a function with comprehensive error handling."""
        try:
            return func()
        except ValueError as e:
            return ErrorHandler.handle_validation_error(e, operation) or default_return
        except (ImportError, AttributeError) as e:
            logger.error(f"Module/attribute error during {operation}: {str(e)}")
            st.error(user_message or f"Feature temporarily unavailable: {operation}")
            return default_return
        except Exception as e:
            logger.error(f"Unexpected error during {operation}: {str(e)}")
            st.error(user_message or f"An error occurred during {operation}")
            return default_return