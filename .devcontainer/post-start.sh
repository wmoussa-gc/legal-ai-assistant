#!/bin/bash

# Post-start script for GitHub Codespaces
# This runs each time the container starts

echo "🔄 Starting Legal AI Assistant services..."

# Check if Azure OpenAI environment variables are set
if [ -z "$AZURE_OPENAI_API_KEY" ] || [ -z "$AZURE_OPENAI_ENDPOINT" ]; then
    echo "⚠️  Warning: Azure OpenAI configuration incomplete"
    echo "   Please set the following in your Codespace secrets or .env file:"
    echo "   - AZURE_OPENAI_API_KEY"
    echo "   - AZURE_OPENAI_ENDPOINT" 
    echo "   - AZURE_OPENAI_API_VERSION (optional, defaults to 2024-02-15-preview)"
    echo "   - AZURE_OPENAI_DEPLOYMENT_NAME"
fi

# Start services in the background
cd /workspace

echo "🚀 Starting development servers..."
echo "   - Backend API will be available at: https://$CODESPACE_NAME-8000.app.github.dev"
echo "   - Frontend will be available at: https://$CODESPACE_NAME-3000.app.github.dev"

# Log startup completion
echo "✅ Post-start setup completed!"
echo "📚 Use 'docker-compose up' to start all services"