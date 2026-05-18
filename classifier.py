"""
Модуль для классификации новостей (Machine Learning).
Обеспечивает очистку текста, TF-IDF векторизацию и предсказание категорий.
"""

import re
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Путь для сохранения обученной модели
MODEL_PATH = 'models/news_classifier.pkl'

def clean_text(text):
    """
    Очищает текст новости от спецсимволов и приводит его к нижнему регистру.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return text

def train_model(texts, labels):
    """
    Обучает модель классификации и сохраняет её в файл.
    Пайплайн: очистка текста -> TF-IDF векторизатор -> Multinomial Naive Bayes.
    """
    cleaned_texts = [clean_text(t) for t in texts]
    
    # Создаем ML pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000)),
        ('clf', MultinomialNB())
    ])
    
    # Обучаем модель
    pipeline.fit(cleaned_texts, labels)
    
    # Проверяем наличие папки models и сохраняем туда файл
    os.makedirs('models', exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Модель успешно обучена и сохранена в {MODEL_PATH}")

def predict_category(text):
    """
    Загружает модель и предсказывает категорию для переданного текста новости.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Модель не найдена. Сначала выполните train_model().")
        
    pipeline = joblib.load(MODEL_PATH)
    cleaned = clean_text(text)
    prediction = pipeline.predict([cleaned])
    return prediction[0]

# Блок для тестирования ML отдельно от веб-интерфейса
if __name__ == "__main__":
    # Расширенные тестовые данные для правильного обучения
    sample_texts = [
        "Новый смартфон от Apple получил мощный процессор M4.",
        "Релиз новой видеокарты ожидается в следующем месяце.",
        "Футбольный матч завершился со счетом 3:0, форвард оформил хет-трик.",
        "В финале кубка мира команда одержала блестящую победу и забила гол.",
        "Парламент в первом чтении принял новый закон о налогах.",
        "Президент подписал указ о выделении бюджета на новые проекты."
    ]
    sample_labels = ["технологии", "технологии", "спорт", "спорт", "политика", "политика"]
    
    print("Начинаем обучение модели...")
    train_model(sample_texts, sample_labels)
    
    # Тестируем предсказание
    test_news = "В финале кубка мира команда забила красивый гол на последних минутах."
    print(f"\nТестовая новость: '{test_news}'")
    print(f"Предсказанная категория: {predict_category(test_news)}")
