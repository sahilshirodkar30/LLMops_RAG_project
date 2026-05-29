# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set workdir
WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:$PATH"
ENV UV_LINK_MODE=copy
ENV PYTHONPATH="/app:/app/multi_doc_chat"

# Copy requirements
COPY requirements.txt ./

# Install dependencies
RUN uv pip install --system -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8080

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]