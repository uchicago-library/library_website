#!/bin/bash

# Docker setup script for Library Website
# Replicates the Vagrant provisioning workflow

set -e

# Handle help flag
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Library Website Docker Development Environment"
    echo "============================================="
    echo ""
    cat dev-docs.txt
    echo ""
    cat docker-commands.txt
    echo ""
    exit 0
fi

echo "🐳 Setting up Library Website Docker environment..."

# Create necessary directories (under bind mount)
echo "Creating required directories..."
mkdir -p media/documents library_website/static

# Build and start services
echo "Building Docker images..."
docker compose build

echo "Starting services..."
docker compose up -d db redis

# Wait for database to be ready
echo "Waiting for database to be ready..."
until docker compose exec db pg_isready -U vagrant -d lib_www_dev; do
  echo "Database not ready, waiting..."
  sleep 2
done

# Start Elasticsearch if enabled
if [ "${ELASTICSEARCH:-true}" != "false" ]; then
    echo "Starting Elasticsearch..."
    docker compose --profile elasticsearch up -d elasticsearch
    echo "Waiting for Elasticsearch to be ready..."
    until curl -s http://localhost:9200/_cluster/health | grep -q "yellow\|green"; do
        echo "Elasticsearch not ready, waiting..."
        sleep 5
    done
fi

# Start the web container
echo "Starting web container..."
docker compose up -d web

# Run Django setup
echo "Running Django migrations and loading dev database..."
docker compose exec web bash -c "
    source /venv/bin/activate && \
    python manage.py migrate --noinput && \
    python manage.py loaddata /app/base/fixtures/test.json && \
    python manage.py shell -c \"from wagtail.models import Site; Site.objects.filter(hostname='localhost').delete()\" && \
    python manage.py update_index
"

# Create news feed test file
echo "Creating news feed test file..."
docker compose exec web bash -c "
    cp /app/base/fixtures/news-feed-test.json /app/static/lib_news/files/lib-news.json
"

echo ""
echo "🎉 Docker setup complete!"
echo ""

# Display shared developer documentation
cat dev-docs.txt

echo ""

# Display shared Docker commands
cat docker-commands.txt

echo ""
echo "To see this help again:"
echo "  ./docker-setup.sh --help"
echo ""