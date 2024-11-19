FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir jinja2

EXPOSE 3000

CMD ["python", "main.py"]
