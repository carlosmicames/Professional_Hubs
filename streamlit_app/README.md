# Professional Hubs - Streamlit Frontend

Clean, professional web interface for the conflict checking system.

## Features

### ✨ User Interface
- **Modern Design** - Gradient header, clean cards, professional styling
- **Dual Search** - Separate tabs for person and company searches
- **Color-Coded Results** - Red for high confidence, yellow for medium
- **Real-time Statistics** - Total conflicts, high/medium confidence counts
- **Responsive Layout** - Works on desktop and mobile

### 🔍 Search Functionality
- **Person Search** - Nombre, Apellido, Segundo Apellido
- **Company Search** - Nombre de Empresa
- **Fuzzy Matching** - Powered by backend API
- **Instant Results** - Real-time conflict detection

### 📊 Results Display
- **Styled Table** - Color-coded rows based on confidence level
- **Detailed Information** - Client name, matter, status, match field
- **Export to CSV** - Download results for records
- **Alert Boxes** - Visual warnings for high/medium conflicts

### 📜 Search Logging
- **Automatic Logging** - All searches logged with timestamp
- **User Tracking** - Records which lawyer performed search
- **Search History** - Sidebar shows last 10 searches
- **Audit Trail** - Complete search history in session

### ⚙️ Configuration
- **API Connection** - Configurable backend URL
- **Firm ID** - Multi-tenant support
- **Connection Test** - Health check button
- **User Settings** - Customizable user name

## Local Development

### Prerequisites
- Python 3.11+
- FastAPI backend running (see main README)

### Setup

1. **Navigate to streamlit_app directory:**
```bash
cd streamlit_app
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API URL
```

5. **Run Streamlit:**
```bash
streamlit run app.py
```

6. **Access app:**
   - Open browser: http://localhost:8501

## Environment Variables

Create a `.env` file:

```bash
# Local development
API_BASE_URL=http://localhost:8000
FIRM_ID=1

# Production (Railway API)
# API_BASE_URL=https://your-api.railway.app
# FIRM_ID=1
```

## Deployment to Streamlit Cloud

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at [streamlit.io](https://streamlit.io))

### Steps

1. **Push code to GitHub:**
```bash
git add .
git commit -m "Add Streamlit frontend"
git push origin main
```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repository
   - Set main file path: `streamlit_app/app.py`
   - Click "Deploy"

3. **Configure secrets:**
   - In Streamlit Cloud dashboard, go to "Settings" → "Secrets"
   - Add:
     ```toml
     API_BASE_URL = "https://your-api.railway.app"
     FIRM_ID = "1"
     ```

4. **Access your app:**
   - URL: `https://your-app.streamlit.app`

## Usage Guide

### Searching for a Person

1. Click on "👤 Persona Natural" tab
2. Enter:
   - **Nombre:** José
   - **Apellido:** González
   - **Segundo Apellido:** Rivera (optional)
3. Click "🔎 Buscar Persona"
4. View results with confidence levels

### Searching for a Company

1. Click on "🏢 Empresa" tab
2. Enter:
   - **Nombre de Empresa:** Corporación ABC
3. Click "🔎 Buscar Empresa"
4. View results

### Understanding Results

**Color Coding:**
- 🔴 **Red Background** - High confidence (≥90%) - Requires review
- 🟡 **Yellow Background** - Medium confidence (70-89%) - Verify before proceeding
- ✅ **Green Alert** - No conflicts found

**Result Columns:**
- **Cliente** - Name of conflicting client
- **Asunto** - Legal matter name
- **Estado** - Matter status (ACTIVO, CERRADO, etc.)
- **Campo Coincidente** - Which field matched (cliente_nombre, parte_relacionada, etc.)
- **Tipo** - Type of match (cliente_persona, parte_relacionada_demandado, etc.)
- **Confianza** - Confidence level (ALTA or MEDIA)
- **Similitud** - Similarity percentage

### Exporting Results

1. After search, scroll to bottom of results
2. Click "📥 Exportar a CSV"
3. File downloads with format: `conflictos_name_YYYYMMDD_HHMMSS.csv`

### Viewing Search History

1. Check sidebar "📜 Historial de Búsquedas"
2. Click on any entry to expand details
3. See timestamp, user, search term, and results count
4. Click "🗑️ Limpiar Historial" to clear

## Features Explained

### 1. Smart Search
- **Accent Normalization** - José matches Jose
- **Fuzzy Matching** - Handles typos (González matches Gonsalez)
- **Case Insensitive** - JOSÉ matches jose
- **Comprehensive** - Searches clients AND related parties

### 2. Visual Feedback
- **Statistics Cards** - Quick overview of conflicts
- **Alert Boxes** - Clear warnings based on severity
- **Color-Coded Table** - Easy identification of risk level

### 3. Audit Trail
- **User Tracking** - Records who performed search
- **Timestamps** - Exact time of each search
- **Search Terms** - What was searched
- **Results Count** - How many conflicts found

### 4. Professional Design
- **Gradient Header** - Modern, professional look
- **Card Layout** - Clean, organized information
- **Responsive** - Works on all screen sizes
- **Accessible** - Clear labels and help text

## Architecture

```
streamlit_app/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── .env.example             # Environment template
└── README.md                # This file
```

## API Integration

The frontend communicates with the FastAPI backend:

**Endpoint Used:**
```
POST /api/v1/conflictos/verificar
Headers: X-Firm-ID: 1
Body: { "nombre": "José", "apellido": "García" }
```

**Health Check:**
```
GET /health
```

## Troubleshooting

### Issue: Cannot connect to API
**Solution:**
- Verify API_BASE_URL in `.env`
- Check that FastAPI backend is running
- Test connection with "Probar Conexión API" button

### Issue: CORS errors
**Solution:**
- Ensure backend CORS is configured to allow Streamlit Cloud domain
- In FastAPI config.py, set `CORS_ORIGINS` to include Streamlit app URL

### Issue: Search returns no results
**Solution:**
- Verify FIRM_ID is correct
- Check that database has data
- Test API directly with curl

### Issue: Styling not loading
**Solution:**
- Clear browser cache
- Restart Streamlit server
- Check browser console for CSS errors

## Production Checklist

Before deploying to production:

- [ ] Update API_BASE_URL to production API
- [ ] Configure proper FIRM_ID
- [ ] Test all search scenarios
- [ ] Verify CORS settings on backend
- [ ] Test export functionality
- [ ] Check responsive design on mobile
- [ ] Review search logging for compliance
- [ ] Test connection health check

## Customization

### Change Color Scheme

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#your-color"
backgroundColor = "#your-color"
```

### Modify Logo

In `app.py`, line ~268:
```python
st.image("path/to/your/logo.png", use_container_width=True)
```

### Add Custom Branding

Edit header section in `app.py`:
```python
st.markdown("""
    <div class="header-container">
        <h1>Your Firm Name</h1>
    </div>
""", unsafe_allow_html=True)
```

## Support

For issues:
- Check API connectivity first
- Review browser console for JavaScript errors
- Verify environment variables are set
- Test API endpoint with curl

---

**Built with ❤️ for Puerto Rico law firms**
