
# Use a minimal Python base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y build-essential libpq-dev && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy all source files into the image
COPY . .

# Set environment variables to be loaded from docker-compose
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=localhost
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ENABLEXSRFPROTECTION=false
ENV STREAMLIT_SERVER_BASEURLPATH=global-disasters

# Expose the Streamlit port
EXPOSE 8501

# Start the app using the full production command
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=localhost", "--server.headless=true", "--server.enableCORS=false", "--server.enableXsrfProtection=false", "--server.baseUrlPath=global-disasters"]