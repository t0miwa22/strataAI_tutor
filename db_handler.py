import sqlite3

# Create a new SQLite database or connect to one
conn = sqlite3.connect('chat_data.db')
cursor = conn.cursor()

def create_tables():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY,
        role TEXT NOT NULL,
        content TEXT NOT NULL
    )
    ''')
    conn.commit()

def insert_message(role, content):
    cursor.execute("INSERT INTO chat_messages (role, content) VALUES (?, ?)", (role, content))
    conn.commit()

def get_chat_history():
    cursor.execute("SELECT role, content FROM chat_messages")
    return cursor.fetchall()

def close_connection():
    conn.close()
