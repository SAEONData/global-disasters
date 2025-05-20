# Base image from devcontainer.json
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy dependency definitions
COPY requirements.txt ./

# Install dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy rest of the source code
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Default environment (you can override via --env-file)
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ENABLEXSRFPROTECTION=false
ENV STREAMLIT_SERVER_HEADLESS=true

# Run the app
CMD ["streamlit", "run", "app.py", "--server.address=localhost"]