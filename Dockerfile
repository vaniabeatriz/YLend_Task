FROM python:3.12-slim

# Keep Python logs visible in ECS and avoid writing .pyc files to the container.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies before copying app code so Docker can cache this layer.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 5000

# ECS/ALB will call /health. Gunicorn is used instead of the Flask dev server.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
