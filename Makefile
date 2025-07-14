.PHONY: install sync run dev clean format lint check docker-build docker-run k8s-deploy k8s-undeploy k8s-status k8s-logs k8s-port-forward

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

run:
	python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

format:
	python -m black app/
	python -m ruff format app/

lint:
	python -m ruff check app/

check:
	python -m validate-pyproject pyproject.toml

clean:
	rm -rf .venv
	rm -rf .ruff_cache
	rm -rf shield_backend.egg-info/
	rm -rf app/__pycache__/
	rm -rf app/*/__pycache__/

# Docker commands
docker-build:
	docker build -t shield-backend:latest .

docker-run:
	docker run -p 8000:8000 shield-backend:latest

# Kubernetes deployment commands
k8s-deploy:
	@echo "🚀 Deploying to Kubernetes..."
	./deploy.sh

k8s-deploy-tag:
	@echo "🚀 Deploying to Kubernetes with custom tag..."
	./deploy.sh $(TAG)

k8s-deploy-registry:
	@echo "🚀 Deploying to Kubernetes with registry..."
	./deploy.sh $(TAG) $(REGISTRY)

k8s-undeploy:
	@echo "🗑️  Removing deployment from Kubernetes..."
	kubectl delete -f k8s/ --ignore-not-found=true

k8s-status:
	@echo "📊 Checking deployment status..."
	kubectl get pods,services,ingress -n shield

k8s-logs:
	@echo "📋 Showing application logs..."
	kubectl logs -f deployment/shield-backend -n shield

k8s-port-forward:
	@echo "🔗 Port forwarding to localhost:8000..."
	kubectl port-forward svc/shield-backend-service 8000:80 -n shield

k8s-restart:
	@echo "🔄 Restarting deployment..."
	kubectl rollout restart deployment/shield-backend -n shield
	kubectl rollout status deployment/shield-backend -n shield
