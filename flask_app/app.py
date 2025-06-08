from flask import Flask, jsonify, request, render_template_string, redirect, url_for
from pymongo import MongoClient
import subprocess

app = Flask(__name__)
client = MongoClient("mongodb://mongodb:27017/")
db = client['produkty_db']
collection = db['produkty']

# === MAIN ===
@app.route("/")
def home():
    return render_template_string("""
        <html>
            <head>
                <title>Produkty</title>
                <link rel="stylesheet" href="{{ url_for('static', filename='flask.css') }}">
            </head>
        <body>
            <h1>Strona glowna</h1>
            <p>Paula Grzebyk 21236</p>
            <p>Przetwarzanie rownolegle i rozproszone - Projekt</p>
            <p>Web scraper korzysta z danych ze strony <a href="https://webscraper.io/test-sites/e-commerce/allinone">webscraper.io</a> i zapisuje nazwe, link, cene, srednia ocene oraz ilosc recenzji do MongoDB. Przy ponownym uruchomieniu scraper pomija duplikaty.</p>
            <a href="/filtry"><button>Filtry</button></a><br><br>
            <a href="/produkty"><button>Wszystkie produkty (json)</button></a>
            <form action="/wyczysc" method="post" onsubmit="return confirm('Na pewno usunac wszystkie dane?');">
                <button type="submit">Wyczysc baze danych</button>
            </form>
        </body>
        </html>
    """)

# === WYCZYSC ===
@app.route("/wyczysc", methods=["POST"])
def wyczysc():
    collection.delete_many({})
    return redirect(url_for('home'))

# === WSZYSTKIE PRODUKTY ===
@app.route("/produkty")
def get_produkty():
    produkty = list(collection.find({}, {"_id": 0}))
    return jsonify(produkty)

# === FILTRY ===
@app.route("/filtry", methods=["GET", "POST"])
def filtry():
    if request.method == "POST":
        kategoria = request.form.get("kategoria")
        cena_od = request.form.get("cena_od", type=float)
        cena_do = request.form.get("cena_do", type=float)
        ocena_min = request.form.get("ocena_min", type=int)

        query = {} # wyszukiwanie
        if kategoria:
            query["kategoria"] = kategoria
        if cena_od is not None or cena_do is not None:
            query["cena"] = {}
            if cena_od is not None:
                query["cena"]["$gte"] = f"${cena_od:.2f}"
            if cena_do is not None:
                query["cena"]["$lte"] = f"${cena_do:.2f}"
        if ocena_min is not None:
            query["ocena"] = {"$gte": ocena_min}

        wyniki = list(collection.find(query, {"_id": 0})) # wszystkie wyniki wyszukiwania
        
        # html - po filtrowaniu
        return render_template_string("""
            <html>
            <head>
                <title>Filtry</title>
                <link rel="stylesheet" href="{{ url_for('static', filename='flask.css') }}">
            </head>
            <body>
            <h1>Wyniki filtrowania</h1>
            <a href="/filtry"><button>Powrot</button></a><br>
            
            {% if wyniki %}
                <ul>
                {% for produkt in wyniki %}
                    <li>
                        <a href="{{produkt['id']}}" target="_blank"><strong>{{ produkt['nazwa'] }}</strong></a><br>
                        Kategoria: {{ produkt['kategoria'] }}<br>
                        Cena: {{ produkt['cena'] }}<br>
                        Ocena: {{ produkt['ocena'] or "brak" }}<br>
                        Recenzje: {{ produkt['recenzje'] }}<br>
                    </li>
                    <hr>
                {% endfor %}
                </ul>
            {% else %}
                <p>Brak wynikow.</p>
            {% endif %}
            </body>
            </html>
        """, wyniki=wyniki)

    # html - przed
    return render_template_string("""
        <html>
            <head>
                <title>Filtry</title>
                <link rel="stylesheet" href="{{ url_for('static', filename='flask.css') }}">
            </head>
        <body>
        <h1>Filtruj produkty</h1>
        <a href="/"><button>Strona glowna</button></a><br>
        <form method="post">
            Kategoria:
            <select name="kategoria">
                <option value="">Dowolna</option>
                <option value="laptops">Laptops</option>
                <option value="tablets">Tablets</option>
                <option value="phones">Phones</option>
            </select><br><br>
            Cena od: <input type="number" name="cena_od" step="0.01"><br>
            Cena do: <input type="number" name="cena_do" step="0.01"><br><br>
            Minimalna ocena: <input type="number" name="ocena_min" min="0" max="5"><br><br>
            <button type="submit">Filtruj</button>
        </form>
        </body>
        </html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

