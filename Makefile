.PHONY: all help install venv run

help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-\\.]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

all: help

.PHONY: build
build: ## Build a Docker image
	$(info Building Docker image...)
	docker build --rm -t employes:1.0 . 

.PHONY: push
push: ## Push image to K3d registry
	$(info Pushing Docker image to K3D registry...)
	docker tag employes:1.0 localhost:32000/employes:1.0
	docker push localhost:32000/employes:1.0

venv: ## Create a Python virtual environment
	$(info Creating Python 3 virtual environment...)
	python3 -m venv ~/venv

install: ## Install Python dependencies
	$(info Installing dependencies...)
	python3 -m pip install --upgrade pip wheel
	pip install -r requirements.txt

lint: ## Run the linter
	$(info Running linting...)
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --max-complexity=10 --max-line-length=127 --statistics

.PHONY: tests
tests: ## Run the unit tests
	$(info Running tests...)
	export DATABASE_HOST=localhost && nosetests -s

run: ## Run the service
	$(info Starting service...)
	honcho start -p 8000

run_flask: ## Run in delevopment mode
	$(info Starting service...)
	export DATABASE_HOST=localhost && flask run

dbrm: ## Stop and remove PostgreSQL in Docker
	$(info Stopping and removing PostgreSQL...)
	docker stop postgresql
	docker rm postgresql

db: ## Run PostgreSQL in Docker
	$(info Running PostgreSQL...)
	docker run --rm -d --name postgresql \
		-p 5432:5432 \
		-e POSTGRES_PASSWORD=postgres \
		-e DATABASE_PASSWORD=postgres \
		-e POSTGRES_DB=employes \
		-v postgresql:/var/lib/postgresql/data \
		postgres:alpine
