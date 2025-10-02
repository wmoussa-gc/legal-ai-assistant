#!/bin/bash

# Post-create script for GitHub Codespaces
# This runs after the container is created but before it starts

echo "🚀 Setting up Legal AI Assistant development environment..."

# Create necessary directories
mkdir -p /workspace/logs
mkdir -p /workspace/temp

# Install SWI-Prolog and s(CASP)
echo "📦 Installing SWI-Prolog..."
sudo apt-get update
sudo apt-get install -y software-properties-common apt-transport-https
sudo apt-add-repository ppa:swi-prolog/stable
sudo apt-get update
sudo apt-get install -y swi-prolog

# Install additional system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    curl \
    wget \
    unzip \
    tree \
    jq

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
cd /workspace/backend
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies for frontend
echo "📦 Installing Node.js dependencies..."
cd /workspace/frontend
npm install

# Set up environment file from template
echo "⚙️ Setting up environment configuration..."
cd /workspace
if [ ! -f .env ]; then
    cp env.template .env
    echo "✅ Created .env file from template"
fi

# Create a symbolic link to make scasp accessible
sudo ln -sf /usr/bin/swipl /usr/local/bin/scasp 2>/dev/null || true

# Set up git configuration if not already set
if [ -z "$(git config --global user.name)" ]; then
    echo "🔧 Setting up Git configuration (you may want to customize this)..."
    git config --global user.name "Codespace User"
    git config --global user.email "codespace@example.com"
    git config --global init.defaultBranch main
fi

# Set permissions
sudo chown -R vscode:vscode /workspace
chmod +x /workspace/.devcontainer/*.sh

echo "✅ Post-create setup completed successfully!"
echo "📝 Next steps:"
echo "  1. Add your Azure OpenAI configuration to the .env file:"
echo "     - AZURE_OPENAI_API_KEY"
echo "     - AZURE_OPENAI_ENDPOINT" 
echo "     - AZURE_OPENAI_API_VERSION"
echo "     - AZURE_OPENAI_DEPLOYMENT_NAME"
echo "  2. Run the application with: docker-compose up"