# Streamlit Quick Start Guide

## Run Locally (3 Steps)

### 1. Start the FastAPI Backend
```bash
cd conflict_api
uvicorn app.main:app --reload
# API running at http://localhost:8000
```

### 2. Start Streamlit Frontend
```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
# App running at http://localhost:8501
```

### 3. Use the App
- Open http://localhost:8501 in your browser
- Enter a name: José García Rivera
- Click "Buscar Persona"
- View color-coded results!

## Deploy to Streamlit Cloud (Free)

### 1. Push to GitHub
```bash
git add .
git commit -m "Add Streamlit frontend"
git push origin main
```

### 2. Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Repository: `Professional_Hubs`
5. Branch: `main`
6. Main file path: `streamlit_app/app.py`
7. Click "Deploy!"

### 3. Configure Secrets
In Streamlit Cloud dashboard → Settings → Secrets:
```toml
API_BASE_URL = "https://your-api.railway.app"
FIRM_ID = "1"
```

**Done!** Your app is live at `https://your-app.streamlit.app`

## Screenshot Preview

**Search Interface:**
- Clean gradient header with logo
- Two tabs: Person search | Company search
- Professional input fields with help text
- Large search button

**Results Display:**
- Statistics cards (Total, High confidence, Medium confidence)
- Color-coded alert boxes:
  - 🔴 Red for HIGH confidence conflicts
  - 🟡 Yellow for MEDIUM confidence conflicts
  - ✅ Green for NO conflicts
- Data table with:
  - Red/yellow row backgrounds
  - All conflict details
  - Match confidence percentages

**Sidebar Features:**
- User name input
- API connection test
- Last 10 searches with timestamps
- Export history option

## Features

✅ **Search** - Person (nombre/apellidos) or Company
✅ **Color-Coded** - Red (high), Yellow (medium confidence)
✅ **Logging** - All searches tracked with user + timestamp
✅ **Export** - Download results as CSV
✅ **Professional** - Clean, modern design
✅ **Responsive** - Works on mobile and desktop

## Quick Test

After starting locally:

1. **Add test data** (via API docs at http://localhost:8000/api/v1/docs):
   - Create a firm
   - Add client "José García"
   - Add a matter for that client

2. **Search in Streamlit**:
   - Enter: José García
   - See the conflict appear!
   - Notice red/yellow coloring
   - Check sidebar for logged search

That's it! 🎉
