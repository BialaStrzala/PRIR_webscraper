from pymongo import MongoClient, errors
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool

# === STRONY ===
urls = [
    'https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops',
    'https://webscraper.io/test-sites/e-commerce/allinone/computers/tablets',
    'https://webscraper.io/test-sites/e-commerce/allinone/phones'
]

# === SCRAPOWANIE ===
def scrapuj(url):
    print(f"=== Scrapuje strone {url} ===")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Blad {e}")
        return 1

    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.select('div.thumbnail') # pobiera dane ze strony

    # === MONGODB ===
    client = MongoClient("mongodb://mongodb:27017/")
    db = client['produkty_db']
    collection = db['produkty']
    collection.create_index("id", unique=True)

    for product in products:
        name_tag = product.select_one('a.title')
        name = name_tag.text.strip()
        temp_link = name_tag.get("href")
        link = f"https://webscraper.io{temp_link}" # caly link do jednego produktu

        price = product.select_one('h4.price').text.strip()
        reviews = product.select_one('span[itemprop="reviewCount"]').text.strip()
        rating_tag = product.select_one('p[data-rating]')
        rating = rating_tag.get('data-rating') if rating_tag else None

        # dane produktu
        item = {
            "id": link,
            "kategoria": url.split("/")[-1],
            "nazwa": name,
            "cena": price,
            "recenzje": reviews,
            "ocena": int(rating) if rating else None
        }

        try:
            collection.insert_one(item)
            print(f"Dodano {name}")
        except errors.DuplicateKeyError:
            print(f"Pominieto duplikat {name}")

# === MAIN ===
def main():
    with Pool(processes=3) as pool:
        pool.map(scrapuj, urls)

if __name__ == "__main__":
    main()
