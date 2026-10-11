FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir "mistralai-workflows[mistralai]>=3.10"

COPY worker.py ./worker.py

CMD ["python", "worker.py"]
