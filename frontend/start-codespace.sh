#!/bin/bash

# Helper script to start frontend with correct backend URL in Codespaces

if [ -n "$CODESPACE_NAME" ]; then
    export REACT_APP_API_URL="https://$CODESPACE_NAME-8000.app.github.dev"
    echo "🌐 Using Codespace backend URL: $REACT_APP_API_URL"
else
    export REACT_APP_API_URL="http://localhost:8000"
    echo "🏠 Using local backend URL: $REACT_APP_API_URL"
fi

cd "$(dirname "$0")" || exit
npm start