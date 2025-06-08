FROM python:3.10

WORKDIR /app

COPY scraper.py .

RUN pip install --default-timeout=100 requests beautifulsoup4 pymongo

CMD ["python", "scraper.py"]

