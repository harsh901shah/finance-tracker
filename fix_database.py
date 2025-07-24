import sqlite3

def fix_database():
    """Fix the users table by recreating it with the phone_number column."""
    conn = None
    try:
        conn = sqlite3.connect('finance_tracker.db')
        cursor = conn.cursor()
        
        # Get existing users (if any)
        cursor.execute("SELECT id, username, password_hash, salt, email, full_name, created_at, last_login, is_active FROM users")
        existing_users = cursor.fetchall()
        
        # Rename the current table
        cursor.execute("ALTER TABLE users RENAME TO users_old")
        
        # Create the new table with the correct schema
        cursor.execute('''
        CREATE TABLE users (
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
        
        # Migrate existing users if any
        for user in existing_users:
            # Add a placeholder phone number for existing users
            phone_number = f"+1{user[0]:010d}"  # Use ID to create unique phone numbers
            cursor.execute('''
            INSERT INTO users (id, username, password_hash, salt, email, phone_number, full_name, created_at, last_login, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user[0], user[1], user[2], user[3], user[4] or "", phone_number, user[5] or "", user[6], user[7], user[8]))
        
        # Drop the old table
        cursor.execute("DROP TABLE users_old")
        
        conn.commit()
        print("Database fixed successfully!")
        
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_database()