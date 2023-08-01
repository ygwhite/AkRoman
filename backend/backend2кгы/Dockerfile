FROM python:3.10-slim
WORKDIR /akroman
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000" ]