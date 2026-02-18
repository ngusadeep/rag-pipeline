# Docker commands for RAG Pipeline

.PHONY: build up down restart logs shell clean

# Build the Docker image
build:
	docker-compose build

# Start the services
up:
	docker-compose up -d

# Start with build
up-build:
	docker-compose up --build -d

# Stop the services
down:
	docker-compose down

# Restart the services
restart:
	docker-compose restart

# View logs
logs:
	docker-compose logs -f rag-pipeline

# Access container shell
shell:
	docker-compose exec rag-pipeline bash

# Clean up containers and volumes
clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# Full rebuild
rebuild:
	docker-compose down -v --remove-orphans
	docker-compose build --no-cache
	docker-compose up -d

# Check health
health:
	curl -f http://localhost:8000/health || echo "Service not healthy"