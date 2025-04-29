# setup_users.py
import sqlite3

conn = sqlite3.connect("beauty_products.db")
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Create results table
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

# Favorites table (if not already made)
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
