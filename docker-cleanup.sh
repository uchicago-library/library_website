#!/bin/bash

# Docker cleanup script for Library Website
# Handles proper cleanup of all services including profiled ones

# simplify progress bar if this is being run in an Emacs shell
if [ -n "$INSIDE_EMACS" ]; then
    DOCKER_PROG=--progress=plain;
else DOCKER_PROG=;
fi

echo "🧹 Cleaning up Library Website Docker environment..."

# Stop all services including profiled ones (like Elasticsearch)
echo "Stopping all services..."
docker compose $DOCKER_PROG --profile elasticsearch down -v --remove-orphans

# Remove project-specific images
echo "Removing project images..."
docker image rm $DOCKER_PROG -f library_website-web 2>/dev/null || true

# Remove project-specific volumes
echo "Removing project volumes..."
docker volume rm $DOCKER_PROG -f library_website_postgres_data library_website_elasticsearch_data library_website_static_files 2>/dev/null || true

# Remove project-specific network
echo "Removing project network..."
docker network rm $DOCKER_PROG library_website_library_network 2>/dev/null || true

# Only prune dangling/unused resources (safer than full system prune)
echo "Cleaning up dangling resources..."
docker container prune -f
docker image prune -f
docker network prune -f

echo ""
echo "✅ Docker cleanup complete!"
echo ""
echo "For complete system cleanup (affects ALL Docker projects):"
echo "  docker system prune -a --volumes -f"
echo ""
echo "To rebuild from scratch:"
echo "  ./docker-setup.sh"
echo ""
echo "To rebuild without Elasticsearch/Node.js:"
echo "  ELASTICSEARCH=false NODEJS=false ./docker-setup.sh"
echo ""
