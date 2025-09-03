#!/usr/bin/env python3
"""
Validation script to check if the Skill Matching Agent is properly configured
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if the environment is properly configured"""
    print("🔍 Checking Skill Matching Agent Configuration...")
    print("=" * 50)
    
    issues = []
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        issues.append("❌ app.py not found - please run from project root")
        return issues
    
    # Check .env file
    if not Path(".env").exists():
        issues.append("❌ .env file not found")
    else:
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ .env file found")
        except ImportError:
            issues.append("❌ python-dotenv package not installed")
            return issues
        
        # Check Azure OpenAI configuration
        azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        azure_key = os.getenv('AZURE_OPENAI_API_KEY')
        
        if azure_endpoint and azure_key:
            print("✅ Azure OpenAI configuration found")
            print(f"   Endpoint: {azure_endpoint}")
            print(f"   Chat Model: {os.getenv('AZURE_OPENAI_CHAT_MODEL', 'Not set')}")
            print(f"   Chat Deployment: {os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT', 'Not set')}")
        else:
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                print("✅ OpenAI API key found")
            else:
                issues.append("❌ Neither Azure OpenAI nor OpenAI API key configured")
    
    # Check data files
    data_dir = Path("data")
    required_files = [
        "skills_taxonomy.json",
        "positions.json"
    ]
    
    if data_dir.exists():
        print("✅ Data directory found")
        for file in required_files:
            file_path = data_dir / file
            if file_path.exists():
                file_size = file_path.stat().st_size
                print(f"✅ {file} found ({file_size:,} bytes)")
            else:
                issues.append(f"❌ {file} not found in data directory")
    else:
        issues.append("❌ Data directory not found")
    
    # Check raw data files
    raw_data_dir = Path("raw-data")
    raw_files = [
        "skill-taxonomy.xlsx",
        "position-skill-requirements.xlsx", 
        "job_output_with_skills_cleaned.xlsx"
    ]
    
    if raw_data_dir.exists():
        print("✅ Raw data directory found")
        for file in raw_files:
            file_path = raw_data_dir / file
            if file_path.exists():
                file_size = file_path.stat().st_size
                print(f"✅ {file} found ({file_size:,} bytes)")
            else:
                print(f"⚠️  {file} not found (optional)")
    else:
        print("⚠️  Raw data directory not found (optional)")
    
    # Check required Python packages
    try:
        import streamlit
        import pandas
        import plotly
        import openai
        import pydantic
        print("✅ Required Python packages are installed")
    except ImportError as e:
        issues.append(f"❌ Missing Python package: {e}")
    
    print("=" * 50)
    
    if not issues:
        print("🎉 Configuration check passed! Ready to run the application.")
        print("\nTo start the application, run:")
        print("   streamlit run app.py")
        print("\nOr use the provided scripts:")
        print("   • Windows: start_app.bat")
        print("   • PowerShell: ./start_app.ps1")
        return True
    else:
        print("❌ Configuration issues found:")
        for issue in issues:
            print(f"   {issue}")
        print("\nPlease fix these issues before running the application.")
        return False

if __name__ == "__main__":
    success = check_environment()
    sys.exit(0 if success else 1)
