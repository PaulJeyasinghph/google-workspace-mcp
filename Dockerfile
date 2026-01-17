# Multi-stage build for Google Workspace MCP Server
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application source
COPY src/ /app/

# Create directory for credentials
RUN mkdir -p /data/credentials

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Run the MCP server
ENTRYPOINT ["python", "server.py"]
