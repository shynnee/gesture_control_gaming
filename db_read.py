import sqlite3

# Connect to the database
conn = sqlite3.connect('face_recognition.db')

# Create a cursor object
c = conn.cursor()

# Function to fetch data from users table
def fetch_users():
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    for user in users:
        print(user)

# Function to fetch data from face_images table
def fetch_face_images():
    c.execute("SELECT * FROM face_images")
    face_images = c.fetchall()
    for image in face_images:
        print(image)

# Function to fetch data from registration_times table
def fetch_registration_times():
    c.execute("SELECT * FROM registration_times")
    registration_times = c.fetchall()
    for reg_time in registration_times:
        print(reg_time)

# Function to fetch data from login_attempts table
def fetch_login_attempts():
    c.execute("SELECT * FROM login_attempts")
    login_attempts = c.fetchall()
    for attempt in login_attempts:
        print(attempt)

# Fetch data from all tables
fetch_users()
fetch_face_images()
fetch_registration_times()
fetch_login_attempts()

# Close the connection
conn.close()

