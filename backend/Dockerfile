FROM python:3.10.6-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r /app/requirements.txt --no-cache-dir
COPY foodgram/ .
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]