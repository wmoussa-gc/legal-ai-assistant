#!/bin/bash

# Quick setup script for Legal AI Assistant
# This can be run manually if needed

set -e

echo "🚀 Setting up Legal AI Assistant..."

# Check if we're in Codespaces
if [ -n "$CODESPACE_NAME" ]; then
    echo "✅ Running in GitHub Codespaces"
    BACKEND_URL="https://$CODESPACE_NAME-8000.app.github.dev"
    FRONTEND_URL="https://$CODESPACE_NAME-3000.app.github.dev"
else
    echo "🏠 Running in local environment"
    BACKEND_URL="http://localhost:8000"
    FRONTEND_URL="http://localhost:3000"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment file from template..."
    cp env.template .env
    
    # Update URLs for Codespaces
    if [ -n "$CODESPACE_NAME" ]; then
        sed -i "s|REACT_APP_API_URL=.*|REACT_APP_API_URL=$BACKEND_URL|g" .env
    fi
fi

# Check for Azure OpenAI configuration
if [ -z "$AZURE_OPENAI_API_KEY" ] || [ -z "$AZURE_OPENAI_ENDPOINT" ]; then
    echo "⚠️  Warning: Azure OpenAI configuration incomplete!"
    echo "   Please add your Azure OpenAI settings to:"
    echo "   - Codespace secrets (recommended for Codespaces)"
    echo "   - .env file (for local development)"
    echo ""
    echo "   Required variables:"
    echo "   - AZURE_OPENAI_API_KEY"
    echo "   - AZURE_OPENAI_ENDPOINT"
    echo "   - AZURE_OPENAI_API_VERSION (defaults to 2024-02-15-preview)"
    echo "   - AZURE_OPENAI_DEPLOYMENT_NAME"
fi

# Build and start services
echo "🔧 Building services..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
if curl -s "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo "✅ Backend is running at: $BACKEND_URL"
else
    echo "❌ Backend is not responding at: $BACKEND_URL"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📍 Service URLs:"
echo "   Backend API: $BACKEND_URL"
echo "   Frontend:    $FRONTEND_URL"
echo "   API Docs:    $BACKEND_URL/docs"
echo ""
echo "📚 Useful commands:"
echo "   docker-compose logs -f        # View logs"
echo "   docker-compose down           # Stop services"
echo "   docker-compose restart        # Restart services"