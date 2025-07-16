import sqlite3

def create_db():
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            ingredients TEXT,
            instructions TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_data(name, ingredients, instructions):
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO recipes (name, ingredients, instructions) VALUES (?, ?, ?)', 
                   (name, ingredients, instructions))
    conn.commit()
    conn.close()
