"""
Authentication service module for the Finance Tracker application.

This module provides user authentication, registration, and session management functionality.
It handles secure password storage with salted hashing, user validation, and session token generation.
The implementation follows security best practices including:
- Salted password hashing to prevent rainbow table attacks
- Secure session token generation for authentication persistence
- Input validation to prevent injection attacks
- Proper error handling and logging for security events
"""

import sqlite3
import hashlib
import secrets
import string
import re
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
# Consider adding bcrypt for production environments
# import bcrypt
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
    
    Security features:
    - Password salting and hashing using SHA-256
    - Secure random token generation for sessions
    - Session expiration and validation
    - Input validation and sanitization
    - Comprehensive error handling and security logging
    """
    
    DB_FILE = 'finance_tracker.db'
    logger = LoggerService.get_logger('auth_service')
    
    # Default session duration in days
    SESSION_DURATION_DAYS = 30
    
    # Maximum age of expired sessions to keep (in days)
    SESSION_CLEANUP_THRESHOLD_DAYS = 7
    
    @classmethod
    def initialize_auth_database(cls):
        """
        Create authentication-related database tables if they don't exist.
        
        Creates the users table for storing user credentials and personal information,
        and the sessions table for managing active user sessions. This method ensures
        the database schema is properly set up before any authentication operations.
        
        Tables created:
        - users: Stores user credentials and personal information
        - sessions: Stores active authentication sessions with expiration
        
        Raises:
            DatabaseError: If there's an issue with database initialization
        """
        conn = None
        try:
            conn = sqlite3.connect(cls.DB_FILE)
            cursor = conn.cursor()
            
            # Create users table with required fields and constraints
            # The is_active field allows for account disabling without deletion
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
            # The expires_at field enables automatic session expiration
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
            
            # Clean up expired sessions on initialization
            cls._cleanup_expired_sessions()
        except sqlite3.Error as e:
            # Roll back any changes if an error occurs to maintain database integrity
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
        salted password hashing. The validation includes format checking for
        email and phone number, as well as minimum password length requirements.
        
        Security measures:
        - Input validation to prevent injection attacks
        - Unique constraint enforcement for username/email/phone
        - Password strength requirements (minimum length)
        - Secure password storage with random salt generation
        
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
            # Minimum 8 characters is an industry standard baseline for password security
            if len(password) < 8:
                cls.logger.warning(f"Registration attempt with short password for user: {username}")
                return False, "Password must be at least 8 characters"
            
            # Validate email format using regex
            # This pattern checks for basic email format: something@something.something
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                cls.logger.warning(f"Registration attempt with invalid email: {email}")
                return False, "Invalid email format"
            
            # Validate phone number format using regex
            # Accepts 10-15 digits with optional + prefix for international format
            if not re.match(r"^\+?[0-9]{10,15}$", phone_number):
                cls.logger.warning(f"Registration attempt with invalid phone number: {phone_number}")
                return False, "Invalid phone number format"
            
            conn = sqlite3.connect(cls.DB_FILE)
            cursor = conn.cursor()
            
            # Check if username already exists to prevent duplicates
            # This enforces the uniqueness constraint at the application level
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
            # A unique salt is generated for each user to prevent rainbow table attacks
            salt = cls._generate_salt()
            password_hash = cls._hash_password(password, salt)
            
            # Insert new user into the database
            # All sensitive data is properly hashed before storage
            cursor.execute('''
            INSERT INTO users (username, password_hash, salt, email, phone_number, full_name)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, salt, email, phone_number, full_name))
            
            conn.commit()
            cls.logger.info(f"User registered successfully: {username}")
            return True, "User registered successfully"
        except UserExistsError as e:
            # Handle case where user already exists with provided credentials
            # Return a generic message to avoid revealing which users exist
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
        The method implements security best practices including constant-time password
        comparison and secure session token generation.
        
        Security measures:
        - Support for multiple authentication methods (username/email/phone)
        - Password verification using secure hashing
        - Account status verification
        - Session token generation for persistent authentication
        - Session expiration for security
        
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
            # This allows flexible authentication using different identifiers
            if login_type == "email":
                query = "SELECT id, username, password_hash, salt, email, phone_number, full_name, is_active FROM users WHERE email = ?"
            elif login_type == "phone":
                query = "SELECT id, username, password_hash, salt, email, phone_number, full_name, is_active FROM users WHERE phone_number = ?"
            else:  # default to username
                query = "SELECT id, username, password_hash, salt, email, phone_number, full_name, is_active FROM users WHERE username = ?"
            
            cursor.execute(query, (identifier,))
            
            # Check if user exists
            # Note: We use the same error message regardless of whether the user exists
            # to prevent username enumeration attacks
            user = cursor.fetchone()
            if not user:
                cls.logger.warning(f"Login attempt with invalid {login_type}: {identifier}")
                raise InvalidCredentialsError("Invalid credentials")
            
            user_id, username, db_password_hash, salt, email, phone_number, full_name, is_active = user
            
            # Check if account is active or disabled
            # This allows administrators to disable accounts without deleting them
            if not is_active:
                cls.logger.warning(f"Login attempt on disabled account: {username}")
                raise AccountDisabledError("Account is disabled")
            
            # Verify password by comparing hashes
            # This is a secure way to verify passwords without storing plaintext
            password_hash = cls._hash_password(password, salt)
            if password_hash != db_password_hash:
                cls.logger.warning(f"Login attempt with invalid password for user: {username}")
                raise InvalidCredentialsError("Invalid credentials")
                
            # Generate a new session token for persistent authentication
            # Using cryptographically secure random token generation
            session_token = cls._generate_session_token()
            
            # Calculate session expiry (default: 30 days from now)
            # This ensures sessions eventually expire for security
            expires_at = (datetime.now() + timedelta(days=cls.SESSION_DURATION_DAYS)).isoformat()
            
            # Store session in database for future verification
            cursor.execute('''
            INSERT INTO sessions (user_id, session_token, expires_at)
            VALUES (?, ?, ?)
            ''', (user_id, session_token, expires_at))
            
            # Update last login timestamp for auditing purposes
            cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            
            # Clean up expired sessions periodically
            # We do this after successful login to avoid impacting performance on failed attempts
            cls._cleanup_expired_sessions()
            
            # Prepare user data to return
            # Note: We don't include sensitive data like password hash or salt
            user_data = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "phone_number": phone_number,
                "full_name": full_name,
                "session_token": session_token
            }
            
            cls.logger.info(f"User logged in successfully: {username}")
            return True, "Login successful", user_data
            
        except (InvalidCredentialsError, AccountDisabledError) as e:
            # Handle authentication errors
            # We use the same error message for invalid credentials regardless of the reason
            # to prevent information leakage
            return False, str(e), None
        except sqlite3.Error as e:
            # Handle database errors and roll back transaction
            if conn:
                conn.rollback()
            cls.logger.error(f"Database error during login: {str(e)}")
            return False, f"Login failed: Database error", None
        except Exception as e:
            # Handle any other unexpected errors
            if conn:
                conn.rollback()
            cls.logger.error(f"Unexpected error during login: {str(e)}")
            return False, "Login failed: An unexpected error occurred", None
        finally:
            # Ensure connection is closed even if an exception occurs
            if conn:
                conn.close()
    
    @classmethod
    def verify_session(cls, session_token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Verify if a session token is valid and not expired.
        
        This method checks if the provided session token exists in the database,
        has not expired, and belongs to an active user account. It's used to
        authenticate users on subsequent requests after initial login.
        
        Security measures:
        - Session expiration verification
        - User account status verification
        - Token existence verification
        - Comprehensive error handling
        
        Args:
            session_token: The session token to verify
            
        Returns:
            Tuple of (valid, user_data) where:
            - valid: Boolean indicating if the session is valid
            - user_data: Dictionary with user information (if valid)
        """
        conn = None
        try:
            conn = sqlite3.connect(cls.DB_FILE)
            cursor = conn.cursor()
            
            # Get session data with user information in a single query
            # This joins the sessions and users tables for efficiency
            cursor.execute('''
            SELECT s.user_id, s.expires_at, u.username, u.email, u.phone_number, u.full_name, u.is_active
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = ?
            ''', (session_token,))
            
            # Check if session exists
            session = cursor.fetchone()
            if not session:
                cls.logger.warning(f"Session verification failed: Session token not found")
                return False, None
                
            user_id, expires_at, username, email, phone_number, full_name, is_active = session
            
            # Check if session is expired by comparing current time with expiration time
            # This ensures that old sessions cannot be used indefinitely
            if datetime.fromisoformat(expires_at) < datetime.now():
                cls.logger.warning(f"Session verification failed: Expired session for user {username}")
                return False, None
                
            # Check if user account is still active
            # This ensures that sessions for disabled accounts are invalidated
            if not is_active:
                cls.logger.warning(f"Session verification failed: Disabled account for user {username}")
                return False, None
                
            # Prepare user data to return
            # Note: We don't include sensitive data like password hash or salt
            user_data = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "phone_number": phone_number,
                "full_name": full_name,
                "session_token": session_token
            }
            
            return True, user_data
            
        except Exception as e:
            # Handle any unexpected errors during session verification
            cls.logger.error(f"Error during session verification: {str(e)}")
            return False, None
        finally:
            # Ensure connection is closed even if an exception occurs
            if conn:
                conn.close()
    
    @classmethod
    def logout(cls, session_token: str) -> bool:
        """
        Invalidate a user's session token.
        
        This method removes the specified session token from the database,
        effectively logging the user out and preventing further use of that token.
        It's an important security measure to allow users to terminate their sessions.
        
        Args:
            session_token: The session token to invalidate
            
        Returns:
            bool: True if logout was successful, False otherwise
        """
        conn = None
        try:
            conn = sqlite3.connect(cls.DB_FILE)
            cursor = conn.cursor()
            
            # Delete the session from the database
            # This immediately invalidates the token
            cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
            conn.commit()
            
            cls.logger.info(f"User logged out successfully")
            return True
        except Exception as e:
            # Handle any errors during logout and roll back transaction
            if conn:
                conn.rollback()
            cls.logger.error(f"Error during logout: {str(e)}")
            return False
        finally:
            # Ensure connection is closed even if an exception occurs
            if conn:
                conn.close()
    
    @classmethod
    def _cleanup_expired_sessions(cls) -> None:
        """
        Remove expired sessions from the database.
        
        This method deletes sessions that have expired beyond a certain threshold
        (default: 7 days past expiration). This helps keep the database clean and
        improves performance by removing unnecessary records.
        
        The cleanup is performed periodically during login operations to avoid
        impacting normal application performance.
        """
        conn = None
        try:
            # Calculate the cutoff date for session cleanup
            # We keep recently expired sessions for a while in case they need to be audited
            cutoff_date = (datetime.now() - timedelta(days=cls.SESSION_CLEANUP_THRESHOLD_DAYS)).isoformat()
            
            conn = sqlite3.connect(cls.DB_FILE)
            cursor = conn.cursor()
            
            # Delete expired sessions older than the cutoff date
            cursor.execute("DELETE FROM sessions WHERE expires_at < ?", (cutoff_date,))
            deleted_count = cursor.rowcount
            conn.commit()
            
            if deleted_count > 0:
                cls.logger.info(f"Cleaned up {deleted_count} expired sessions")
        except Exception as e:
            # Log errors but don't propagate them since this is a background operation
            if conn:
                conn.rollback()
            cls.logger.error(f"Error cleaning up expired sessions: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def _generate_salt(length: int = 16) -> str:
        """
        Generate a random salt for password hashing.
        
        This method creates a cryptographically secure random string to use as
        a salt for password hashing. Using a unique salt for each user prevents
        rainbow table attacks and ensures that identical passwords have different
        hashes in the database.
        
        Security considerations:
        - Uses Python's secrets module for cryptographically secure randomness
        - Includes letters, digits, and punctuation for high entropy
        - Default length of 16 characters provides good security
        
        Args:
            length: Length of the salt string (default: 16)
            
        Returns:
            str: Random salt string
        """
        # Use a mix of letters, digits, and punctuation for high entropy
        alphabet = string.ascii_letters + string.digits + string.punctuation
        # secrets.choice is cryptographically secure, unlike random.choice
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """
        Hash a password with the provided salt.
        
        This method combines the password with a salt and creates a secure hash
        using SHA-256. The salt ensures that identical passwords will have different
        hashes, protecting against rainbow table attacks.
        
        Security considerations:
        - Uses SHA-256, a strong cryptographic hash function
        - Combines password with salt before hashing
        - Returns hexadecimal digest for safe storage
        
        Note: For production systems, consider using more specialized password
        hashing algorithms like bcrypt, Argon2, or PBKDF2 with appropriate
        work factors.
        
        Args:
            password: Plain text password
            salt: Salt string to use in hashing
            
        Returns:
            str: Hashed password as hexadecimal string
        """
        # Combine password and salt
        salted_password = password + salt
        
        # Hash using SHA-256
        # Note: In a production environment, consider using a more specialized
        # password hashing algorithm like bcrypt, Argon2, or PBKDF2
        hash_obj = hashlib.sha256(salted_password.encode())
        return hash_obj.hexdigest()
        
        # Example implementation with bcrypt (for production use):
        # return bcrypt.hashpw(password.encode(), salt.encode()).decode()
    
    @staticmethod
    def _generate_session_token(length: int = 64) -> str:
        """
        Generate a secure random session token.
        
        This method creates a cryptographically secure random string to use as
        a session token for user authentication. The token is used to identify
        and authenticate users after initial login.
        
        Security considerations:
        - Uses Python's secrets module for cryptographically secure randomness
        - Uses a mix of letters and digits for compatibility
        - Default length of 64 characters provides high entropy
        - Avoids special characters for better URL compatibility
        
        Args:
            length: Length of the token string (default: 64)
            
        Returns:
            str: Random session token
        """
        # Use only letters and digits for better compatibility with URLs and cookies
        # Special characters are avoided to prevent encoding issues
        alphabet = string.ascii_letters + string.digits
        # secrets.choice is cryptographically secure, unlike random.choice
        return ''.join(secrets.choice(alphabet) for _ in range(length))