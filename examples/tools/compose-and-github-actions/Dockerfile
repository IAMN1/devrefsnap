FROM python:3.14-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY app.py test_app.py ./

USER 10001
CMD ["python", "app.py"]
