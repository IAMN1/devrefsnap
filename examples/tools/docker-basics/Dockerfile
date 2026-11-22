FROM python:3.14-slim

WORKDIR /site
COPY message.txt ./
USER 10001:10001
EXPOSE 8000
STOPSIGNAL SIGINT
CMD ["python", "-m", "http.server", "8000", "--bind", "0.0.0.0"]
