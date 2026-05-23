import sqlite3
import os
from classifier import predict_category, train_model, MODEL_PATH
 
# !!! УКАЖИ ЗДЕСЬ ТОЧНОЕ ИМЯ ФАЙЛА ВАШЕЙ БАЗЫ ДАННЫХ !!!
DB_NAME = 'news_aggregator.db'
 
 
def ensure_model_exists():
    """
    Проверяет наличие модели и переобучает её при необходимости.
    Это решает проблему несовместимости .pkl файла между версиями Python/sklearn.
    """
    if not os.path.exists(MODEL_PATH):
        print("Модель не найдена. Запускаю обучение...")
        train_model()
        return
 
    # Проверяем, что модель читается корректно (защита от повреждённого .pkl)
    try:
        import joblib
        joblib.load(MODEL_PATH)
        print("Модель загружена успешно.")
    except Exception as e:
        print(f"Модель повреждена или несовместима: {e}")
        print("Переобучаю модель на встроенных данных...")
        train_model()
 
 
def update_db_categories():
    """
    Классифицирует все новости с категорией 'Неопределено' или NULL
    и сохраняет предсказанные категории обратно в базу данных.
    """
    # Гарантируем наличие рабочей модели перед стартом
    ensure_model_exists()
 
    if not os.path.exists(DB_NAME):
        print(f"Файл БД '{DB_NAME}' не найден. Проверь название!")
        return
 
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
 
    try:
        # Ищем все неопределённые новости в таблице articles
        cursor.execute(
            "SELECT rowid, title FROM articles WHERE category = 'Неопределено' OR category IS NULL"
        )
        rows = cursor.fetchall()
 
        if not rows:
            print("Не найдено новостей с категорией 'Неопределено'. Всё уже классифицировано.")
            return
 
        print(f"Найдено {len(rows)} новостей для классификации...\n")
 
        stats = {}
        for rowid, title in rows:
            predicted_cat = predict_category(title)
            cursor.execute(
                "UPDATE articles SET category = ? WHERE rowid = ?",
                (predicted_cat, rowid)
            )
            stats[predicted_cat] = stats.get(predicted_cat, 0) + 1
            print(f"  ✓ [{predicted_cat:12s}] {title[:60]}")
 
        conn.commit()
 
        print("\n--- Итоги классификации ---")
        for cat, count in sorted(stats.items(), key=lambda x: -x[1]):
            print(f"  {cat:12s}: {count} новостей")
        print(f"\nВсего обновлено: {len(rows)} записей в БД.")
 
    except sqlite3.OperationalError as e:
        print(
            f"Ошибка работы с БД: {e}\n"
            "Убедись, что таблица называется 'articles', "
            "а заголовок новости лежит в столбце 'title'."
        )
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
    finally:
        conn.close()
 
 
def reclassify_all():
    """
    Переклассифицирует ВСЕ новости в базе данных (включая уже размеченные).
    Полезно после переобучения модели с новыми категориями.
    """
    ensure_model_exists()
 
    if not os.path.exists(DB_NAME):
        print(f"Файл БД '{DB_NAME}' не найден.")
        return
 
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
 
    try:
        cursor.execute("SELECT rowid, title FROM articles")
        rows = cursor.fetchall()
 
        if not rows:
            print("Таблица articles пуста.")
            return
 
        print(f"Переклассифицирую все {len(rows)} новостей...\n")
 
        stats = {}
        for rowid, title in rows:
            predicted_cat = predict_category(title)
            cursor.execute(
                "UPDATE articles SET category = ? WHERE rowid = ?",
                (predicted_cat, rowid)
            )
            stats[predicted_cat] = stats.get(predicted_cat, 0) + 1
            print(f"  ✓ [{predicted_cat:12s}] {title[:60]}")
 
        conn.commit()
 
        print("\n--- Итоги переклассификации ---")
        for cat, count in sorted(stats.items(), key=lambda x: -x[1]):
            print(f"  {cat:12s}: {count} новостей")
        print(f"\nВсего обновлено: {len(rows)} записей.")
 
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        conn.close()
 
 
if __name__ == '__main__':
    import sys
 
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        # python apply_ml.py --all  → переклассифицировать все записи
        reclassify_all()
    else:
        # python apply_ml.py  → классифицировать только Неопределено
        update_db_categories()