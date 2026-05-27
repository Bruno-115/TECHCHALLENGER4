FROM python:3.9-slim

WORKDIR /app

COPY requirements .

RUN pip install -r requirements

COPY . .

CMD ["python", "train.py"]