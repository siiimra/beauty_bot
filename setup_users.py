"""
setup_users.py

PURPOSE:
    This script initializes the user-related tables for the BeautyBot application.
    It creates the following tables if they do not already exist:
      - users: stores user account details
      - results: stores each user's latest quiz results
      - favorites: stores products each user has saved to their wishlist

USAGE:
    Run with: python setup_users.py

NOTES:
    - This script is intended to be run once during initial setup.
    - All tables use INTEGER PRIMARY KEY auto-increment IDs.
    - The results and favorites tables reference the users table via foreign keys.

OUTPUT:
    Prints a confirmation once tables are created or updated.
"""

import sqlite3

# Connect to the database
conn = sqlite3.connect("beauty_products.db")
cursor = conn.cursor()

# Create the users table to store account credentials
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Create the results table to store quiz responses linked to a user
cursor.execute('''
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    skin_type TEXT,
    makeup_pref TEXT,
    finish TEXT,
    concerns TEXT,
    price_range TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

# Create the favorites table to store user-selected products
cursor.execute('''
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product_name TEXT,
    brand_name TEXT,
    category TEXT,
    image_url TEXT,
    purchase_link TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

conn.commit()
conn.close()
print("Tables created or updated!")
