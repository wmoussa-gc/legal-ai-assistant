#!/bin/bash

# Development utilities script
# Provides common development tasks

set -e

case "$1" in
    "start")
        echo "🚀 Starting Legal AI Assistant..."
        docker-compose up -d
        ;;
    "stop")
        echo "🛑 Stopping Legal AI Assistant..."
        docker-compose down
        ;;
    "restart")
        echo "🔄 Restarting Legal AI Assistant..."
        docker-compose restart
        ;;
    "logs")
        echo "📋 Showing logs (Ctrl+C to exit)..."
        docker-compose logs -f "${2:-}"
        ;;
    "build")
        echo "🔧 Building services..."
        docker-compose build "${2:-}"
        ;;
    "clean")
        echo "🧹 Cleaning up Docker resources..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        ;;
    "test")
        echo "🧪 Running tests..."
        docker-compose exec backend pytest tests/ -v
        ;;
    "shell")
        service="${2:-backend}"
        echo "🐚 Opening shell in $service container..."
        docker-compose exec "$service" /bin/bash
        ;;
    "install")
        echo "📦 Installing dependencies..."
        docker-compose exec backend pip install -r requirements.txt
        docker-compose exec frontend npm install
        ;;
    "check")
        echo "🔍 Checking service health..."
        if [ -n "$CODESPACE_NAME" ]; then
            BACKEND_URL="https://$CODESPACE_NAME-8000.app.github.dev"
        else
            BACKEND_URL="http://localhost:8000"
        fi
        
        echo "Backend status:"
        if curl -s "$BACKEND_URL/health" > /dev/null 2>&1; then
            echo "  ✅ Backend is running"
        else
            echo "  ❌ Backend is not responding"
        fi
        
        echo "Container status:"
        docker-compose ps
        ;;
    *)
        echo "Legal AI Assistant Development Tools"
        echo ""
        echo "Usage: ./dev.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start              Start all services"
        echo "  stop               Stop all services"
        echo "  restart [service]  Restart services (or specific service)"
        echo "  logs [service]     Show logs (all or specific service)"
        echo "  build [service]    Build services (all or specific service)"
        echo "  clean              Clean up Docker resources"
        echo "  test               Run tests"
        echo "  shell [service]    Open shell in container (default: backend)"
        echo "  install            Install/update dependencies"
        echo "  check              Check service health and status"
        echo ""
        echo "Examples:"
        echo "  ./dev.sh start              # Start all services"
        echo "  ./dev.sh logs backend       # Show backend logs"
        echo "  ./dev.sh shell frontend     # Open shell in frontend container"
        echo "  ./dev.sh restart backend    # Restart only backend service"
        ;;
esac