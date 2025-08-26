# Render Deployment Instructions

## Files Ready for Deployment:
- Procfile
- render.yaml  
- runtime.txt
- requirements.txt
- .gitignore

## Steps to Deploy:

1. **Create GitHub Repository:**
   - Go to github.com
   - Create new repository named "CalcaneusAnalyzer"
   - Upload all project files

2. **Deploy on Render:**
   - Visit render.com
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Auto-detection will use these settings:
     - Build: `pip install -r requirements.txt`
     - Start: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

3. **App will be live at your Render URL**

## Git Commands (run in terminal with Git installed):
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/CalcaneusAnalyzer.git
git push -u origin main
```