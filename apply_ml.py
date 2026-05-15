import sqlite3
import os
from classifier import predict_category

# !!! УКАЖИ ЗДЕСЬ ТОЧНОЕ ИМЯ ФАЙЛА ВАШЕЙ БАЗЫ ДАННЫХ !!!
DB_NAME = 'news_aggregator.db' 

def update_db_categories():
    if not os.path.exists(DB_NAME):
        print(f"Файл БД '{DB_NAME}' не найден. Проверь название!")
        return
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Ищем все неопределенные новости в таблице articles
        cursor.execute("SELECT rowid, title FROM articles WHERE category = 'Неопределено' OR category IS NULL")
        rows = cursor.fetchall()
        
        if not rows:
            print("Не найдено новостей с категорией 'Неопределено'.")
        
        for rowid, title in rows:
            # Твоя модель предсказывает категорию по заголовку
            predicted_cat = predict_category(title)
            
            # Записываем результат обратно в базу
            cursor.execute("UPDATE articles SET category = ? WHERE rowid = ?", (predicted_cat, rowid))
            print(f"Успех | {title[:40]}... ---> {predicted_cat}")
            
        conn.commit()
        print("\nВсе новости успешно классифицированы и сохранены в БД!")
        
    except Exception as e:
        print(f"Ошибка: {e}\nУбедись, что таблица называется 'articles', а текст новости лежит в 'title'.")
        
    conn.close()

if __name__ == '__main__':
    update_db_categories()
