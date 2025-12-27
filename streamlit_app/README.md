# Professional Hubs - Legal Practice Management Dashboard

## Overview

Complete Streamlit application for managing a legal practice in Puerto Rico. Features a two-tab navigation system, integrated COI checking, calendar management, video calls, and client/case management.

## Features

### My Office Tab
- **Dashboard** - Main overview with calendar, metrics, COI alerts, and AI Call Agent notifications
- **Clients** - Client management with automatic COI checking on new client creation
- **My Cases** - Case management with all Puerto Rico legal areas and case types
- **Civus IA** - Manual COI verification tool

### Legal Workshop Tab
- **Schedule** - Calendar management with Outlook integration
- **Forms** - Legal form templates
- **Calls** - In-app video calling system
- **Invoices** - Invoice management
- **Reports** - Statistics and analytics
- **Settings** - System configuration
- **Collaborators** - Team management

## Technical Specifications

- **Frontend**: Streamlit 1.31.0
- **Database**: SQLite (local storage)
- **API Integration**: FastAPI conflict checking API
- **Color Scheme**: Navy blue (#1e3a5f) and light gray (#f7fafc)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API settings
```

3. Run the application:
```bash
streamlit run app.py
```

4. Access at: http://localhost:8501

## Database Schema

### Tables
- **clients** - Client information with COI tracking
- **cases** - Legal cases linked to clients
- **calendar_events** - Calendar entries
- **video_calls** - Video call scheduling
- **intake_notifications** - AI Call Agent responses
- **invoices** - Billing records
- **forms** - Form templates

## Puerto Rico Legal Areas

- Civil
- Criminal
- Familia
- Laboral
- Corporativo
- Bienes Raices
- Inmigracion
- Quiebras
- Propiedad Intelectual
- Administrativo
- Ambiental
- Tributario

## COI (Conflict of Interest) Integration

The system automatically checks for conflicts when:
1. Adding a new client
2. Creating a new case with opposing party
3. Manual verification via Civus IA

Conflicts are flagged visually in:
- Client list (red highlight)
- Case list (red highlight)
- Dashboard alerts

## AI Call Agent Notifications

Intake forms from the AI Call Agent appear as notifications on the Dashboard requiring action:
- Caller Name
- Phone
- Email
- Case Type
- Description
- Timestamp

Notifications must be marked as "Reviewed" to dismiss.

## API Configuration

Connect to your FastAPI backend:

```python
API_BASE_URL = "http://localhost:8000"  # or your Railway URL
FIRM_ID = 1
```

## License

Proprietary - Professional Hubs