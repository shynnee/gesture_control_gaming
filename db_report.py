import sqlite3
from tabulate import tabulate
from datetime import datetime


def fetch_and_print_joined_data(c):
    join_query = """
    SELECT users.full_name, users.username, users.password,
           face_images.image_path, registration_times.registration_time,
           login_attempts.login_count, login_attempts.last_login_time
    FROM users
    LEFT JOIN face_images ON users.username = face_images.username
    LEFT JOIN registration_times ON users.username = registration_times.username
    LEFT JOIN login_attempts ON users.username = login_attempts.username
    """
    c.execute(join_query)
    rows = c.fetchall()
    col_names = [description[0] for description in c.description]
    return col_names, rows


def generate_summary_statistics(c):
    statistics = {}

    # Total number of users
    c.execute("SELECT COUNT(*) FROM users")
    statistics['Total Users'] = c.fetchone()[0]

    # Total number of face images
    c.execute("SELECT COUNT(*) FROM face_images")
    statistics['Total Face Images'] = c.fetchone()[0]

    # Total number of login attempts
    c.execute("SELECT COUNT(*) FROM login_attempts")
    statistics['Total Login Attempts'] = c.fetchone()[0]

    return statistics


def print_summary_statistics(statistics):
    print("Summary Statistics:")
    for key, value in statistics.items():
        print(f"{key}: {value}")
    print("\n")


def generate_report():
    # Connect to the database
    conn = sqlite3.connect('face_recognition.db')
    c = conn.cursor()

    # Fetch and print summary statistics
    statistics = generate_summary_statistics(c)
    print_summary_statistics(statistics)

    # Fetch and print joined data
    col_names, rows = fetch_and_print_joined_data(c)
    print("Detailed User Information:")
    print(tabulate(rows, headers=col_names, tablefmt='grid'))
    print("\n")

    # Close the connection
    conn.close()


if __name__ == "__main__":
    print("Generating report...")
    print(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    generate_report()
