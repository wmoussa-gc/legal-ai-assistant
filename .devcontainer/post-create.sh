#!/bin/bash

# Post-create script for GitHub Codespaces
# This runs after the container is created but before it starts

echo "🚀 Setting up Legal AI Assistant development environment..."

# Install SWI-Prolog
echo "📦 Installing SWI-Prolog..."
sudo apt-get update
sudo apt-get install -y swi-prolog

# Install Python dependencies
echo "� Installing Python dependencies..."
cd "${CODESPACE_VSCODE_FOLDER:-/workspaces/legal-ai-assistant}/backend" || cd /workspace/backend
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies for frontend
echo "📦 Installing Node.js dependencies..."
cd "${CODESPACE_VSCODE_FOLDER:-/workspaces/legal-ai-assistant}/frontend" || cd /workspace/frontend
npm install

# Set up environment file from template
echo "⚙️ Setting up environment configuration..."
cd "${CODESPACE_VSCODE_FOLDER:-/workspaces/legal-ai-assistant}" || cd /workspace
if [ ! -f .env ]; then
    cp env.template .env
    echo "✅ Created .env file from template"
fi

echo "✅ Post-create setup completed successfully!"
echo "📝 Next steps:"
echo "  1. Add your Azure OpenAI configuration to the .env file:"
echo "     - AZURE_OPENAI_API_KEY"
echo "     - AZURE_OPENAI_ENDPOINT"
echo "     - AZURE_OPENAI_API_VERSION"
echo "     - AZURE_OPENAI_DEPLOYMENT_NAME"
echo "  2. Start backend: cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "  3. Start frontend: cd frontend && npm start"