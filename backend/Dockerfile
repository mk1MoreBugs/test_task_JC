FROM python:3.13.2-slim

WORKDIR /backend

COPY . .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
EXPOSE 8080

CMD uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
