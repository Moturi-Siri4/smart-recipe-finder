import sqlite3
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')

def preprocess(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    return " ".join(filtered_words)

def load_data():
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    
    # Ensure table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            ingredients TEXT,
            instructions TEXT
        )
    """)

    # Check if data exists
    cursor.execute("SELECT COUNT(*) FROM recipes")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("Pasta Carbonara", "pasta, eggs, bacon, parmesan, pepper", "Boil pasta. Cook bacon. Mix with eggs and parmesan."),
            ("Chicken Curry", "chicken, curry powder, coconut milk, garlic, onion", "Cook chicken. Add spices and coconut milk. Simmer."),
            ("Vegetable Stir Fry", "broccoli, carrot, bell pepper, soy sauce, garlic", "Stir fry vegetables. Add soy sauce and garlic.")
        ]
        cursor.executemany("INSERT INTO recipes (name, ingredients, instructions) VALUES (?, ?, ?)", sample_data)
        conn.commit()

    cursor.execute("SELECT * FROM recipes")
    data = cursor.fetchall()
    conn.close()
    
    # Preprocess ingredients and instructions for easier search
    return [(row[1], preprocess(row[2] + " " + row[3])) for row in data]

# Example use:
data = load_data()
for recipe in data:
    print(recipe)
