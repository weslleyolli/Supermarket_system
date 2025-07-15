.PHONY: install run test lint format clean docker-build docker-run

# Instalação
install:
	pip install -r requirements.txt

# Desenvolvimento
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-ui:
	streamlit run app/ui/main.py

# Testes
test:
	pytest

test-cov:
	pytest --cov=app tests/

# Formatação e linting
format:
	black app tests
	isort app tests

lint:
	flake8 app tests
	mypy app

# Database
migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(msg)"

# Docker
docker-build:
	docker-compose -f docker/docker-compose.yml build

docker-run:
	docker-compose -f docker/docker-compose.yml up -d

docker-stop:
	docker-compose -f docker/docker-compose.yml down

docker-logs:
	docker-compose -f docker/docker-compose.yml logs -f

# Limpeza
clean:
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Backup
backup:
	python scripts/backup.py

# Deploy
deploy:
	./scripts/deploy.sh
