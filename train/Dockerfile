FROM python:3.9-slim

WORKDIR /app

COPY requirements .

RUN pip install -r requirements

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]