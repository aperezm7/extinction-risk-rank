FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY src ./src
COPY services ./services
COPY tests/fixtures ./tests/fixtures

RUN pip install --no-cache-dir .

EXPOSE 8091
CMD ["uvicorn", "services.gateway.app:app", "--host", "0.0.0.0", "--port", "8091"]
