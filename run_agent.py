#!/usr/bin/env python3
"""
Calendar Agent - Google Calendar integration with AI agent
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.agent import run_calendar_agent

if __name__ == "__main__":
    print("Starting Calendar Agent...\n")
    
    # Check for required Vertex AI environment variables
    required_vars = {
        "GOOGLE_CLOUD_PROJECT": "Your GCP project ID",
        "GOOGLE_CLOUD_LOCATION": "GCP location (e.g., europe-west1)",
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.environ.get(var):
            missing_vars.append(f"  {var}: {description}")
    
    if missing_vars:
        print("❌ Error: Missing required environment variables in .env file:\n")
        print("\n".join(missing_vars))
        print("\nMake sure your .env file contains:")
        print("  GOOGLE_GENAI_USE_VERTEXAI=1")
        print("  GOOGLE_CLOUD_PROJECT=your-project-id")
        print("  GOOGLE_CLOUD_LOCATION=europe-west1")
        print("  ROOT_AGENT_MODEL=gemini-2.0-flash-001")
        sys.exit(1)
    
    # Check for client secret
    if not os.path.exists("client_secret.json"):
        print("❌ Error: client_secret.json not found")
        print("\nDownload it from Google Cloud Console:")
        print("  https://console.cloud.google.com/apis/credentials")
        sys.exit(1)
    
    run_calendar_agent()