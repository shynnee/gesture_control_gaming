import sqlite3
from tabulate import tabulate

# Connect to the database
conn = sqlite3.connect('face_recognition.db')

# Create a cursor object
c = conn.cursor()


# Function to fetch and print data with column names in a table format
def fetch_and_print_table(table_name):
    c.execute(f"SELECT * FROM {table_name}")
    rows = c.fetchall()
    col_names = [description[0] for description in c.description]

    print(f"data from {table_name} table:")
    print(tabulate(rows, headers=col_names, tablefmt='grid'))
    print("\n")  # Add a newline for better readability


# Fetch data from all tables
fetch_and_print_table("users")
fetch_and_print_table("face_images")
fetch_and_print_table("registration_times")
fetch_and_print_table("login_attempts")

# Close the connection
conn.close()
