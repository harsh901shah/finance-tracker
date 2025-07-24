"""
Authentication service module for the Finance Tracker application.

This module provides user authentication, registration, and session management functionality.
It handles secure password storage with salted hashing, user validation, and session token generation.
"""

import sqlite3
import hashlib
import secrets
import string
import re
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from services.logger_service import LoggerService

class AuthError(Exception):
    """Base exception for authentication errors"""
    pass

class UserExistsError(AuthError):
    """Exception raised when a user already exists"""
    pass

class InvalidCredentialsError(AuthError):
    """Exception raised when credentials are invalid"""
    pass

class AccountDisabledError(AuthError):
    """Exception raised when account is disabled"""
    pass

class SessionExpiredError(AuthError):
    """Exception raised when session has expired"""
    pass

class DatabaseError(AuthError):
    """Exception raised when a database error occurs"""
    pass

class ValidationError(AuthError):
    """Exception raised when input validation fails"""
    pass

class AuthService:
    """
    Service for handling user authentication, registration, and session management.
    
    This class provides methods for user registration, login authentication,
    session validation, and secure password handling. It uses SQLite for data storage
    and implements security best practices like salted password hashing.
    """
    
    DB_FILE = 'finance_tracker.db'
    logger = LoggerService.get_logger('auth_service')
    
    @classmethod
    def initialize_auth_database(cls):
        """
        Create authentication-related database tables if they don't exist.
        
        Creates the users table for storing user credentials and personal information,
        and the sessions table for managing active user sessions.
        
        Raises:
            DatabaseError: If there's an issue with database initialization
        """
        conn = None
        try:
            conn = sqlite3.connect(cls.DB_FILE)
            cursor = conn.cursor()
            
            # Create users table with required fields and constraints
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone_number TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT,
                is_active INTEGER DEFAULT 1
            )
            ''')
            
            # Create sessions table for managing user authentication sessions
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            
            conn.commit()
            cls.logger.info("Auth database initialized successfully")
        except sqlite3.Error as e:
            # Roll back any changes if an error occurs
            if conn:
                conn.rollback()
            cls.logger.error(f"Database initialization error: {str(e)}")
            raise DatabaseError(f"Failed to initialize auth database: {str(e)}")
        finally:
            # Ensure connection is closed even if an exception occurs
            if conn:
                conn.close()
    
    @classmethod
    def register_user(cls, username: str, password: str, email: str, 
                     phone_number: str, full_name: str) -> Tuple[bool, str]:
        """
        Register a new user with the provided credentials and information.
        
        Validates all input fields, checks for existing users with the same
        username/email/phone, and securely stores user information with
        salted password hashing.
        
        Args:
            username: Unique username for the user
            password: Plain text password (will be hashed before storage)
            email: User's email address (must be unique)
            phone_number: User's phone number (must be unique)
            full_name: User's full name
            
        Returns:
            Tuple of (success, message) where:
            - success: Boolean indicating if registration was successful
            - message: Description of the result or error
        """
        conn = None
        try:
            # Validate that all required fields are provided
            if not username or not password or not email or not phone_number or not full_name:
                cls.logger.warning("Registration attempt with missing required fields")
                return False, "All fields are required"
            
            # Validate password length for security
            if len(password) < 8:
                cls.logger.warning(f"Registration attempt with short password for user: {username}")
                return False, "Password must be at least 8 characters"
            
            # Validate email format using regex
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                cls.logger.warning(f"Registration attempt with invalid email: {email}")
                return False, "Invalid email format"
            
            # Validate phone number format using regex
            if not re.match(r"^\+?[0-9]{10,15}$", phone_number):
                cls.logger.warning(f"Registration attempt with invalid phone number: {phone_number}")
                return False, "Invalid phone number format"
            
            conn = sqlite3.connect(cls.DB_FILE)
            cursor = conn.cursor()
            
            # Check if username already exists to prevent duplicates
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                cls.logger.warning(f"Registration attempt with existing username: {username}")
                raise UserExistsError("Username already exists")
            
            # Check if email already exists to prevent duplicates
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                cls.logger.warning(f"Registration attempt with existing email: {email}")
                raise UserExistsError("Email already exists")
            
            # Check if phone number already exists to prevent duplicates
            cursor.execute("SELECT id FROM users WHERE phone_number = ?", (phone_number,))
            if cursor.fetchone():
                cls.logger.warning(f"Registration attempt with existing phone number: {phone_number}")
                raise UserExistsError("Phone number already exists")
            
            # Generate salt and hash password for secure storage
            salt = cls._generate_salt()
            password_hash = cls._hash_password(password, salt)
            
            # Insert new user into the database
            cursor.execute('''
            INSERT INTO users (username, password_hash, salt, email, phone_number, full_name)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, salt, email, phone_number, full_name))
            
            conn.commit()
            cls.logger.info(f"User registered successfully: {username}")
            return True, "User registered successfully"
        except UserExistsError as e:
            # Handle case where user already exists with provided credentials
            return False, str(e)
        except sqlite3.Error as e:
            # Handle database errors and roll back transaction
            if conn:
                conn.rollback()
            cls.logger.error(f"Database error during registration: {str(e)}")
            return False, f"Registration failed: {str(e)}"
        except Exception as e:
            # Handle any other unexpected errors
            if conn:
                conn.rollback()
            cls.logger.error(f"Unexpected error during registration: {str(e)}")
            return False, f"Registration failed: An unexpected error occurred"
        finally:
            # Ensure connection is closed even if an exception occurs
            if conn:
                conn.close()
    
    @classmethod
    def login(cls, identifier: str, password: str, login_type: str = "username") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Authenticate a user with the provided credentials.
        
        Supports login with username, email, or phone number. Verifies the password,
        checks if the account is active, and creates a new session token upon successful login.
        
        Args:
            identifier: Username, email, or phone number to identify the user
            password: Plain text password to verify
            login_type: Type of identifier used ("username", "email", or "phone")
            
        Returns:
            Tuple of (success, message, user_data) where:
            - success: Boolean indicating if login was successful
            - message: Description of the result or error
            - user_data: Dictionary with user information and session token (if successful)
        """
        conn = None
        try:
            # Validate that required fields are provided
            if not identifier or not password:
                cls.logger.warning("Login attempt with missing credentials")
                return False, "All fields are required", None
                
            conn = sqlite3.connect(cls.DB_FILE)
            cursor = conn.cursor()
            
            # Select appropriate query based on login type
            if login_type == "email":
                query = "SELECT id, username, password_hash, salt, email, phone_number, full_name, is_active FROM users WHERE email = ?"
            elif login_type == "phone":
                query = "SELECT id, username, password_hash, salt, email, phone_number, full_name, is_active FROM users WHERE phone_number = ?"
            else:  # default to username
                query = "SELECT id, username, password_hash, salt, email, phone_number, full_name, is_active FROM users WHERE username = ?"
            
            cursor.execute(query, (identifier,))
            
            # Check if user exists
            user = cursor.fetchone()
            if not user:
                cls.logger.warning(f"Login attempt with invalid {login_type}: {identifier}")
                raise InvalidCredentialsError("Invalid credentials")
            
            user_id, username, db_password_hash, salt, email, phone_number, full_name, is_active = user
            
            # Check if account is active or disabled
            if not is_active:
                cls.logger.warning(f"Login attempt on disabled account: {username}")
                raise AccountDisabledError("Account is disabled")
            
            # Verify password by comparing hashes
            password_hash = cls._hash_password(password, salt)
            if password_hash != db_password_hash:
                cls.logger.warning(f"Login attempt with invalid password for user: {username}")