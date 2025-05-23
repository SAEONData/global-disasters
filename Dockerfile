#-----------------------Multi state build-------------------------------
FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
    
COPY . .

FROM python:3.12-slim AS runner

WORKDIR /app

COPY --from=base /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY --from=base /app .

RUN adduser --disabled-password --gecos "" globaldis && chown -R globaldis /app
USER globaldis

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--server.enableCORS=false", "--server.enableXsrfProtection=false", "--server.baseUrlPath=global-disasters"]