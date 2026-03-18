FROM python:3.10-slim

# Install system dependencies (fixes Pillow/zlib issue)
RUN apt-get update && apt-get install -y \
    build-essential \
    libz-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all files into container
COPY . .

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install -r requirements.txt

# Streamlit config
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run app
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]