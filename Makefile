# YouTube AI Platform v3.0 - Professional Makefile
# Managing Backend, Frontend, and Mini-App Modules

.PHONY: help install setup start dev stop kill-port test-shopier shopier mini-app logs clean

help: ## Show this help message
	@echo "YouTube AI Platform v3.0 - Command Suite"
	@echo "=========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies (Backend & Frontend)
	@echo "📦 Installing Backend dependencies..."
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r backend/requirements.txt
	@echo "📦 Installing Frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Installation complete"

setup: ## Full environment setup and database initialization
	@echo "🎯 [v3.0] Executing Intelligent Setup..."
	bash scripts/setup.sh

start: ## Launch the unified platform (Backend & Dashboard)
	@echo "🚀 Launching YouTube AI Platform..."
	bash scripts/start_app.sh

dev: ## Start development servers with hot-reload
	@echo "🛠️  Starting Backend (Port 8000)..."
	export PYTHONPATH=$PYTHONPATH:$(pwd) && source venv/bin/activate && cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "🛠️  Starting Frontend (Port 3001)..."
	cd frontend && npm run dev -- --port 3001

kill-port: ## Force kill processes on default ports (8000, 3001)
	@echo "🔪 Cleaning up ports..."
	bash scripts/kill_port.sh 8000
	bash scripts/kill_port.sh 3001

test-shopier: ## Verify Shopier License Key (Master Key) bypass
	@echo "🧪 Verifying Shopier Master Key..."
	curl -X POST http://localhost:8000/api/auth/login-with-key \
		-H "Content-Type: application/json" \
		-d '{"access_key": "LAZY_MASTER_2025_ADMIN"}'

shopier: ## Launch Shopier-specific app mode (storefront + backend)
	@echo "🛒 Launching Shopier app mode..."
	bash scripts/start_shopier_app.sh

mini-app: ## Launch the YouTube Income Commander Mini-App
	@echo "💰 Launching Income Commander..."
	cd modules/mini_app && bash run_complete_system.sh

logs: ## View application logs
	@echo "📋 Streaming logs..."
	tail -f logs/app.log

clean: ## Remove temporary files, caches, and logs
	@echo "🧹 Cleaning repository..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	@echo "✅ Cleanup complete"
