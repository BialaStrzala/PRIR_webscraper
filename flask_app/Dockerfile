FROM python:3.10

WORKDIR /app

COPY app.py .

COPY static ./static

RUN pip install flask pymongo

CMD ["python", "app.py"]

