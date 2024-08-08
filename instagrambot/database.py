import sqlite3
from datetime import datetime

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users
    (id INTEGER PRIMARY KEY, 
    full_name TEXT, 
    user_name TEXT, 
    registration_date TEXT)""")
               
cursor.execute("""CREATE TABLE IF NOT EXISTS links
    (id INTEGER PRIMARY KEY, 
    user_id INTEGER, link TEXT, 
    FOREIGN KEY(user_id) REFERENCES users(id))""")

conn.commit()

def add_user(user_id, full_name, user_name):
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO users (id, full_name, user_name, registration_date) VALUES (?, ?, ?, ?)", 
                   (user_id, full_name, user_name, registration_date))
    conn.commit()


def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    return cursor.fetchone()

def add_link(user_id, url):
    cursor.execute("INSERT INTO links (user_id, link) VALUES (?, ?)", (user_id, url))
    conn.commit()

def get_links(user_id):
    cursor.execute("SELECT link FROM links WHERE user_id=?", (user_id,))
    return cursor.fetchall()

def get_registration_time(user_id):
    cursor.execute("SELECT registration_date FROM users WHERE id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

def delete_user(user_id):
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()

def delete_links(user_id):
    cursor.execute("DELETE FROM links WHERE user_id=?", (user_id,))
    conn.commit()

def get_all_users():
    cursor.execute("SELECT id, full_name, user_name FROM users")
    return cursor.fetchall()

def get_bot_stats():
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM links")
    link_count = cursor.fetchone()[0]
    
    return f"Foydalanuvchilar soni: {user_count}\nHavolalar soni: {link_count}"
