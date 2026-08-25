FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    API_PORT=8019 \
    API_HOST=0.0.0.0

# Install uv for fast, reliable dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml requirements.txt ./

# Install python dependencies
RUN uv pip install --system -r requirements.txt fastapi uvicorn httpx scikit-learn matplotlib pyarrow fsspec requests filelock openpyxl joblib psutil

# Copy application source code
COPY . .

EXPOSE 8019

CMD ["python3", "scripts/run_api_server.py"]
