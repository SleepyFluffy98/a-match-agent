# Skill Matching Agent - Troubleshooting Guide

## 🎯 Current Status
- ✅ All Python dependencies are installed and working
- ✅ All project modules import successfully
- ✅ Configuration and data files are properly set up
- ❓ Streamlit server startup issue

## 🔧 Solutions to Try

### Option 1: Direct Python Execution
```powershell
cd "C:\Users\rfe9ku4\OneDrive - Allianz\Desktop\A-MATCH-AGENT"
python -m streamlit run app.py
```

### Option 2: Alternative Port
```powershell
cd "C:\Users\rfe9ku4\OneDrive - Allianz\Desktop\A-MATCH-AGENT"
python -m streamlit run app.py --server.port 8080
```

### Option 3: Specific IP Address
```powershell
cd "C:\Users\rfe9ku4\OneDrive - Allianz\Desktop\A-MATCH-AGENT"
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

### Option 4: Browser Configuration
```powershell
cd "C:\Users\rfe9ku4\OneDrive - Allianz\Desktop\A-MATCH-AGENT"
python -m streamlit run app.py --browser.gatherUsageStats false
```

## 🌐 Manual Browser Access
If Streamlit starts but doesn't open browser automatically, try these URLs:
- http://localhost:8501
- http://localhost:8502
- http://localhost:8505
- http://127.0.0.1:8501

## 🔍 Debug Information
- Python Environment: ✅ All imports working
- Config Validation: ✅ Azure OpenAI configured
- Data Files: ✅ Skills (1.1MB) and Positions (0.5MB) loaded
- Dependencies: ✅ streamlit, pandas, plotly, openai, pydantic

## 🚨 If Still Having Issues

### Check Network/Firewall
Windows Defender Firewall might be blocking Python/Streamlit. Try:
1. Run PowerShell as Administrator
2. Temporarily disable Windows Firewall for testing
3. Add Python to firewall exceptions

### Alternative: Use Different Python Environment
If using Anaconda/Miniconda:
```powershell
conda activate base  # or your preferred environment
streamlit run app.py
```

### Check Streamlit Config
Create `.streamlit/config.toml` in project directory:
```toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

## 📞 Next Steps
1. Try each option above in order
2. If browser doesn't open automatically, manually navigate to the URLs
3. Check Windows Event Viewer for any Python/network errors
4. Consider running from different terminal (Command Prompt vs PowerShell)
