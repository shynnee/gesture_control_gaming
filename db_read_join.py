import sqlite3
from tabulate import tabulate

def fetch_and_print_joined_data():
    # Connect to the database
    conn = sqlite3.connect('face_recognition.db')

    # Create a cursor object
    c = conn.cursor()

    # SQL query to join the tables
    join_query = """
    SELECT users.full_name, users.username, users.password,
           face_images.image_path, registration_times.registration_time,
           login_attempts.login_count, login_attempts.last_login_time
    FROM users
    LEFT JOIN face_images ON users.username = face_images.username
    LEFT JOIN registration_times ON users.username = registration_times.username
    LEFT JOIN login_attempts ON users.username = login_attempts.username
    """

    # Execute the query
    c.execute(join_query)
    rows = c.fetchall()

    # Get column names
    col_names = [description[0] for description in c.description]

    # Print the results in table format
    print("data from joined tables:")
    print(tabulate(rows, headers=col_names, tablefmt='grid'))

    # Close the connection
    conn.close()

if __name__ == "__main__":
    fetch_and_print_joined_data()
