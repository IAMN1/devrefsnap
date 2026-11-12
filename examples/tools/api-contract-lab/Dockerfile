FROM python:3.14-slim AS app

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY app.py ./

USER 10001
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

FROM node:26.8.2-bookworm-slim AS client

WORKDIR /client
RUN npm install --global --ignore-scripts typescript@6.0.3
COPY client.mts ./
RUN tsc --strict --noEmitOnError --target ES2022 --module NodeNext \
    --lib ES2022,DOM --outDir dist client.mts

USER node
CMD ["node", "dist/client.mjs"]
