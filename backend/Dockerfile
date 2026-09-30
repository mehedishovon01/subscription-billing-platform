# Use the official Python image from Docker Hub
FROM python:3.12-slim

# Set environment variables to avoid buffering and to set the working directory inside the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /usr/src/app

# Install uv and sync the locked project dependencies.
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock /usr/src/app/
RUN uv sync --frozen --no-dev

# Copy the entire Django project into the container
COPY . /usr/src/app/

# Run the application entrypoint
ENTRYPOINT ["bash", "docker-entrypoint.sh"]

# Expose the application port
EXPOSE 8000

CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60"]
