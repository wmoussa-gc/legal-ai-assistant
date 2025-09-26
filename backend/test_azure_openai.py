#!/usr/bin/env python3
"""
Azure OpenAI Configuration Helper Script
Run this to test your Azure OpenAI configuration.
"""

import os
import asyncio

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file")
except ImportError:
    print("❌ python-dotenv not available, using system environment variables only")

from app.services.llm_service import LLMService

async def test_azure_openai():
    print("🔧 Azure OpenAI Configuration Test")
    print("=" * 50)
    
    # Check environment variables
    config_items = [
        ("Azure OpenAI API Key", "AZURE_OPENAI_API_KEY"),
        ("Azure Endpoint", "AZURE_OPENAI_ENDPOINT"), 
        ("Azure API Version", "AZURE_OPENAI_API_VERSION"),
        ("Azure Deployment Name", "AZURE_OPENAI_DEPLOYMENT_NAME")
    ]
    
    all_configured = True
    for label, env_var in config_items:
        value = os.getenv(env_var)
        if value and "your-" not in value:
            print(f"✅ {label}: {value[:20]}...")
        else:
            print(f"❌ {label}: Not configured")
            all_configured = False
    
    print("\n🤖 Testing LLM Service...")
    try:
        llm_service = LLMService()
        print(f"Service Available: {'✅' if llm_service.is_available() else '❌'}")
        print(f"Using Azure OpenAI: {'✅' if getattr(llm_service, 'is_azure_openai', False) else '❌'}")
        
        if llm_service.is_available() and all_configured:
            print("\n🧪 Testing Legal Query...")
            test_prompt = """
            Analyze this legal question: "Can a Canadian citizen request access to government health records?"
            
            Consider the Access to Information Act and provide:
            1. Legal reasoning
            2. Confidence level
            3. Required conditions
            """
            
            try:
                response = await llm_service._query_openai(test_prompt, max_tokens=500)
                print("✅ Test query successful!")
                print(f"Model: {response.model_used}")
                print(f"Tokens: {response.tokens_used}")
                print(f"Response preview: {response.content[:200]}...")
            except Exception as e:
                print(f"❌ Test query failed: {e}")
        
    except Exception as e:
        print(f"❌ LLM Service initialization failed: {e}")
    
    if not all_configured:
        print("\n📝 To configure Azure OpenAI, update your .env file:")
        print("AZURE_OPENAI_API_KEY=your-actual-key")
        print("AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/")
        print("AZURE_OPENAI_DEPLOYMENT_NAME=your-gpt4-deployment")

if __name__ == "__main__":
    asyncio.run(test_azure_openai())