import sqlite3

DB_NAME = "news_aggregator.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Добавлено поле author
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            description TEXT,
            published_date TEXT,
            source TEXT,
            author TEXT,
            category TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Добавлен аргумент author
def insert_article(title, url, description, published_date, source, author, category="Неопределено"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO articles (title, url, description, published_date, source, author, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, url, description, published_date, source, author, category))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Игнорируем дубликаты
    finally:
        conn.close()