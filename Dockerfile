
# Use a minimal Python base image
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y build-essential libpq-dev && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=localhost
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ENABLEXSRFPROTECTION=false
ENV STREAMLIT_SERVER_BASEURLPATH=global-disasters

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=localhost", "--server.headless=true", "--server.enableCORS=false", "--server.enableXsrfProtection=false", "--server.baseUrlPath=global-disasters"]