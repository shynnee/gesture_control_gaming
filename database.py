import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('face_recognition.db')
c = conn.cursor()

# Create users table
c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )''')

# Create face_images table
c.execute('''CREATE TABLE IF NOT EXISTS face_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                image_path TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username)
            )''')

# Create registration_times table
c.execute('''CREATE TABLE IF NOT EXISTS registration_times (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            )''')

# Create login_attempts table
c.execute('''CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                login_count INTEGER DEFAULT 0,
                last_login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            )''')

# Commit changes and close connection
conn.commit()
conn.close()
