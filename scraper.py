import feedparser
from database import insert_article

SOURCES = {
    "Habr": "https://habr.com/ru/rss/all/all/",
    "Lenta": "https://lenta.ru/rss/news",
    "BBC": "https://feeds.bbci.co.uk/news/rss.xml"
}

def scrape_news():
    print(" Запуск скрапера новостей...\n")
    
    for source_name, url in SOURCES.items():
        print(f" Подключение к источнику: {source_name}")
        print(f" URL: {url}")
        
        feed = feedparser.parse(url)
        articles = feed.entries
        print(f" Найдено статей для обработки: {len(articles)}")
        
        saved_count = 0
        for entry in articles:
            title = entry.get("title", "")
            link = entry.get("link", "")
            description = entry.get("summary", entry.get("description", ""))
            published = entry.get("published", "")
            
            # Извлекаем автора. Если ключа нет в RSS, ставим заглушку "Не указан"
            author = entry.get("author", "Не указан")
            
            # Передаем все данные, включая source_name и author, в базу данных
            insert_article(title, link, description, published, source_name, author)
            saved_count += 1
            
        print(f" Источник {source_name} успешно обработан.\n")
        
    print(" Скрапинг всех источников полностью завершен!")

if __name__ == "__main__":
    from database import init_db
    init_db()
    scrape_news()