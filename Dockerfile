FROM python:3.12.7-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV INVENTORY_DB=/data/inventory.db

VOLUME ["/data"]

CMD ["python", "main.py"]