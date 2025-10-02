#!/bin/bash

# Post-start script for GitHub Codespaces
# This runs each time the container starts

echo "🔄 Legal AI Assistant Codespace Ready!"

# Check if Azure OpenAI environment variables are set
if [ -z "$AZURE_OPENAI_API_KEY" ] || [ -z "$AZURE_OPENAI_ENDPOINT" ]; then
    echo "⚠️  Azure OpenAI configuration not found"
    echo "   Set these as Codespace secrets or in .env file:"
    echo "   - AZURE_OPENAI_API_KEY"
    echo "   - AZURE_OPENAI_ENDPOINT" 
    echo "   - AZURE_OPENAI_API_VERSION"
    echo "   - AZURE_OPENAI_DEPLOYMENT_NAME"
fi

if [ -n "$CODESPACE_NAME" ]; then
    echo ""
    echo "🌐 Service URLs (will be available once you start the servers):"
    echo "   - Backend API: https://$CODESPACE_NAME-8000.app.github.dev"
    echo "   - Frontend:    https://$CODESPACE_NAME-3000.app.github.dev"
    echo "   - API Docs:    https://$CODESPACE_NAME-8000.app.github.dev/docs"
fi

echo ""
echo "🚀 To start the application:"
echo "   Terminal 1: cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "   Terminal 2: cd frontend && npm start"