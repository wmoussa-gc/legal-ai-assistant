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
    BACKEND_URL="https://$CODESPACE_NAME-8000.app.github.dev"
    FRONTEND_URL="https://$CODESPACE_NAME-3000.app.github.dev"
    
    # Update root .env file with Codespace URLs
    ROOT_ENV="${CODESPACE_VSCODE_FOLDER:-/workspaces/legal-ai-assistant}/.env"
    if [ -f "$ROOT_ENV" ]; then
        # Update or add REACT_APP_API_URL
        if grep -q "REACT_APP_API_URL=" "$ROOT_ENV"; then
            sed -i "s|REACT_APP_API_URL=.*|REACT_APP_API_URL=$BACKEND_URL|g" "$ROOT_ENV"
        else
            echo "REACT_APP_API_URL=$BACKEND_URL" >> "$ROOT_ENV"
        fi
        echo "✅ Updated root .env with backend URL: $BACKEND_URL"
    fi
    
    # Create/update frontend .env file
    FRONTEND_ENV="${CODESPACE_VSCODE_FOLDER:-/workspaces/legal-ai-assistant}/frontend/.env"
    echo "REACT_APP_API_URL=$BACKEND_URL" > "$FRONTEND_ENV"
    echo "✅ Created frontend/.env with backend URL: $BACKEND_URL"
    
    echo ""
    echo "🌐 Service URLs (will be available once you start the servers):"
    echo "   - Backend API: $BACKEND_URL"
    echo "   - Frontend:    $FRONTEND_URL"
    echo "   - API Docs:    $BACKEND_URL/docs"
fi

echo ""
echo "🚀 To start the application:"
echo "   Terminal 1: cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
if [ -n "$CODESPACE_NAME" ]; then
    echo "   Terminal 2: cd frontend && REACT_APP_API_URL=https://$CODESPACE_NAME-8000.app.github.dev npm start"
else
    echo "   Terminal 2: cd frontend && npm start"
fi