from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

DB_NAME = "news_aggregator.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    search = request.args.get("search", "")
    category = request.args.get("category", "")

    query = "SELECT * FROM articles WHERE 1=1"
    params = []

    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY id DESC"

    cursor.execute(query, params)
    articles = cursor.fetchall()

    conn.close()

    categories = ["технологии", "спорт", "политика", "экономика"]

    return render_template(
        "index.html",
        articles=articles,
        categories=categories,
        selected_category=category,
        search=search
    )


if __name__ == "__main__":
    app.run(debug=True)