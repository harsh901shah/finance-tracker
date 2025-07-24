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
    """Service for handling user authentication"""
    
    DB_FILE = 'finance_tracker.db'
    logger = LoggerService.get_logger('auth_service')
    
    @classmethod
    def initialize_auth_database(cls):
        """Create users table if it doesn't exist"""
        conn = None
        try:
            conn = sqlite3.connect(cls.DB_FILE)
            cursor = conn.cursor()
            
            # Create users table
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
            
            # Create sessions table
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
            if conn:
                conn.rollback()
            cls.logger.error(f"Database initialization error: {str(e)}")
            raise DatabaseError(f"Failed to initialize auth database: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def register_user(cls, username: str, password: str, email: str, 
                     phone_number: str, full_name: str) -> Tuple[bool, str]:
        """
        Register a new user
        
        Args:
            username: Username
            password: Plain text password
            email: User email
            phone_number: User phone number
            full_name: User's full name
            
        Returns:
            Tuple of (success, message)
        """
        conn = None
        try:
            # Validate inputs
            if not username or not password or not email or not phone_number or not full_name:
                cls.logger.warning("Registration attempt with missing required fields")
                return False, "All fields are required"
            
            if len(password) < 8:
                cls.logger.warning(f"Registration attempt with short password for user: {username}")
                return False, "Password must be at least 8 characters"
            
            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                cls.logger.warning(f"Registration attempt with invalid email: {email}")
                return False, "Invalid email format"
            
            # Validate phone number format (simple validation)
            if not re.match(r"^\+?[0-9]{10,15}$", phone_number):
                cls.logger.warning(f"Registration attempt with invalid phone number: {phone_number}")
                return False, "Invalid phone number format"
            
            conn = sqlite3.connect(cls.DB_FILE)
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                cls.logger.warning(f"Registration attempt with existing username: {username}")
                raise UserExistsError("Username already exists")
            
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                cls.logger.warning(f"Registration attempt with existing email: {email}")
                raise UserExistsError("Email already exists")
            
            # Check if phone number already exists
            cursor.execute("SELECT id FROM users WHERE phone_number = ?", (phone_number,))
            if cursor.fetchone():
                cls.logger.warning(f"Registration attempt with existing phone number: {phone_number}")
                raise UserExistsError("Phone number already exists")
            
            # Generate salt and hash password
            salt = cls._generate_salt()
            password_hash = cls._hash_password(password, salt)
            
            # Insert new user
            cursor.execute('''
            INSERT INTO users (username, password_hash, salt, email, phone_number, full_name)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, salt, email, phone_number, full_name))
            
            conn.commit()
            cls.logger.info(f"User registered successfully: {username}")
            return True, "User registered successfully"
        except UserExistsError as e:
            return False, str(e)
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            cls.logger.error(f"Database error during registration: {str(e)}")
            return False, f"Registration failed: {str(e)}"
        except Exception as e:
            if conn:
                conn.rollback()
            cls.logger.error(f"Unexpected error during registration: {str(e)}")
            return False, f"Registration failed: An unexpected error occurred"
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def login(cls, identifier: str, password: str, login_type: str = "username") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Authenticate a user
        
        Args:
            identifier: Username, email or phone number
            password: Plain text password
            login_type: Type of identifier (username, email, phone)
            
        Returns:
            Tuple of (success, message, user_data)
        """
        conn = None
        try:
            if not identifier or not password:
                cls.logger.warning("Login attempt with missing credentials")
                return False, "All fields are required", None
                
            conn = sqlite3.connect(cls.DB_FILE)
            cursor = conn.cursor()
            
            # Get user data based on login type
            if login_type == "email":
                query = "SELECT id, username, password_hash, salt, email, phone_number, full_name, is_active FROM users WHERE email = ?"
            elif login_type == "phone":
                query = "SELECT id, username, password_hash, salt, email, phone_number, full_name, is_active FROM users WHERE phone_number = ?"
            else:  # default to username
                query = "SELECT id, username, password_hash, salt, email, phone_number, full_name, is_active FROM users WHERE username = ?"
            
            cursor.execute(query, (identifier,))
            
            user = cursor.fetchone()
            if not user:
                cls.logger.warning(f"Login attempt with invalid {login_type}: {identifier}")
                raise InvalidCredentialsError("Invalid credentials")
            
            user_id, username, db_password_hash, salt, email, phone_number, full_name, is_active = user
            
            # Check if account is active
            if not is_active:
                cls.logger.warning(f"Login attempt on disabled account: {username}")
                raise AccountDisabledError("Account is disabled")
            
            # Verify password
            password_hash = cls._hash_password(password, salt)
            if password_hash != db_password_hash:
                cls.logger.warning(f"Login attempt with invalid password for user: {username}")
                raise InvalidCredentialsError("Invalid credentials")
            
            # Update last login time
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, user_id))
            
            # Create session
            session_token = cls._generate_session_token()
            expires_at = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            INSERT INTO sessions (user_id, session_token, expires_at)
            VALUES (?, ?, ?)
            ''', (user_id, session_token, expires_at))
            
            conn.commit()
            
            # Return user data
            user_data = {
                "id": user_id,
                "username": username,
                "email": email,
                "phone_number": phone_number,
                "full_name": full_name,
                "session_token": session_token,
                "expires_at": expires_at
            }
            
            cls.logger.info(f"User logged in successfully: {username}")
            return True, "Login successful", user_data
        except (InvalidCredentialsError, AccountDisabledError) as e:
            return False, str(e), None
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            cls.logger.error(f"Database error during login: {str(e)}")
            return False, f"Login failed: Database error", None
        except Exception as e:
            if conn:
                conn.rollback()
            cls.logger.error(f"Unexpected error during login: {str(e)}")
            return False, f"Login failed: An unexpected error occurred", None
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def verify_session(cls, session_token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Verify a session token
        
        Args:
            session_token: Session token
            
        Returns:
            Tuple of (valid, user_data)
        """
        conn = None
        try:
            conn = sqlite3.connect(cls.DB_FILE)
            cursor = conn.cursor()
            
            # Get session data
            cursor.execute('''
            SELECT s.id, s.user_id, s.expires_at, u.username, u.email, u.phone_number, u.full_name
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = ? AND u.is_active = 1
            ''', (session_token,))
            
            session = cursor.fetchone()
            if not session:
                cls.logger.debug(f"Session verification failed: Invalid session token")
                return False, None
            
            session_id, user_id, expires_at, username, email, phone_number, full_name = session
            
            # Check if session is expired
            expires_at_dt = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
            if expires_at_dt < datetime.now():
                # Delete expired session
                cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                conn.commit()
                cls.logger.debug(f"Session expired for user: {username}")
                raise SessionExpiredError("Session expired")
            
            # Return user data
            user_data = {
                "id": user_id,
                "username": username,
                "email": email,
                "phone_number": phone_number,
                "full_name": full_name,
                "session_token": session_token,
                "expires_at": expires_at
            }
            
            return True, user_data
        except SessionExpiredError:
            return False, None
        except sqlite3.Error as e:
            cls.logger.error(f"Database error during session verification: {str(e)}")
            return False, None
        except Exception as e:
            cls.logger.error(f"Unexpected error during session verification: {str(e)}")
            return False, None
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def logout(cls, session_token: str) -> bool:
        """
        Logout a user by invalidating their session
        
        Args:
            session_token: Session token
            
        Returns:
            Success status
        """
        conn = None
        try:
            conn = sqlite3.connect(cls.DB_FILE)
            cursor = conn.cursor()
            
            # Get user info for logging
            cursor.execute('''
            SELECT u.username FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = ?
            ''', (session_token,))
            
            result = cursor.fetchone()
            username = result[0] if result else "Unknown"
            
            # Delete session
            cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
            conn.commit()
            
            cls.logger.info(f"User logged out: {username}")
            return True
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            cls.logger.error(f"Database error during logout: {str(e)}")
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            cls.logger.error(f"Unexpected error during logout: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def _generate_salt(length: int = 16) -> str:
        """Generate a random salt"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Hash a password with the given salt"""
        # Combine password and salt
        salted_password = password + salt
        
        # Hash using SHA-256
        hash_obj = hashlib.sha256(salted_password.encode())
        return hash_obj.hexdigest()
    
    @staticmethod
    def _generate_session_token(length: int = 32) -> str:
        """Generate a random session token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))