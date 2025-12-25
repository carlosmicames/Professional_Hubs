# Railway Deployment Fix - "pip: command not found"

## Problem

Railway deployment was failing with error:
```
/bin/bash: line 1: pip: command not found
ERROR: failed to build: failed to solve: process "/bin/bash -ol pipefail -c pip install -r conflict_api/requirements.txt" did not complete successfully: exit code: 127
```

## Root Cause

The original configuration used NIXPACKS builder with a custom build command, but NIXPACKS wasn't properly detecting Python and setting up pip in the environment.

## Solution

Switched to **Docker-based deployment** with a custom `Dockerfile` that explicitly:
1. Uses Python 3.11 base image (includes pip)
2. Installs system dependencies (gcc, postgresql-client)
3. Installs Python packages from requirements.txt
4. Runs database migrations automatically
5. Starts Gunicorn server

## Files Created/Modified

### ✅ Created: `Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
# ... installs dependencies and runs app
```

### ✅ Created: `.dockerignore`
Excludes unnecessary files from Docker build for faster builds.

### ✅ Modified: `railway.toml`
Changed from:
```toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r conflict_api/requirements.txt"
```

To:
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"
```

### ✅ Modified: `railway.json`
Same change - switched to DOCKERFILE builder.

### ✅ Updated: `DEPLOYMENT.md`
Added troubleshooting section for this specific error.

## How to Deploy Now

### Step 1: Commit and Push Changes
```bash
git add .
git commit -m "Fix Railway deployment with Dockerfile"
git push origin main
```

### Step 2: Deploy to Railway

**Option A: Fresh Deploy (Recommended)**
1. Go to Railway dashboard
2. Delete the existing failed service (if any)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect the Dockerfile
6. Add PostgreSQL database
7. Configure environment variables

**Option B: Redeploy Existing Service**
1. Go to your existing Railway service
2. Click "Settings"
3. Verify "Builder" is set to "Dockerfile"
4. Go to "Deployments"
5. Click "Deploy" to trigger new build with updated code

### Step 3: Verify Build Success

Check Railway logs for:
```
✅ Building Docker image
✅ Installing Python dependencies
✅ Running migrations: alembic upgrade head
✅ Starting gunicorn server
```

### Step 4: Test API

Once deployed, visit:
- Health check: `https://your-project.railway.app/health`
- API docs: `https://your-project.railway.app/api/v1/docs`

## Why Docker Instead of NIXPACKS?

### Advantages of Dockerfile:
1. **Explicit control** - We specify exactly what gets installed
2. **Reproducible builds** - Same build works locally and on Railway
3. **Debugging** - Can test Docker build locally before pushing
4. **Auto migrations** - Database migrations run automatically on deploy
5. **Industry standard** - Dockerfile works on any Docker-compatible platform

### When to Use NIXPACKS:
- Simple Python apps without complex dependencies
- When you don't need custom build steps
- Quick prototypes

### When to Use Dockerfile:
- ✅ Apps with system dependencies (PostgreSQL client)
- ✅ Multi-step builds (migrations + server start)
- ✅ Production deployments requiring control
- ✅ **Our case!**

## Testing Docker Build Locally (Optional)

Before pushing to Railway, you can test the Docker build locally:

```bash
# Build the image
docker build -t professional-hubs .

# Run with environment variables
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host/db" \
  -e FUZZY_THRESHOLD=70 \
  -e FUZZY_HIGH_CONFIDENCE=90 \
  professional-hubs

# Test the API
curl http://localhost:8000/health
```

## Environment Variables Required

Make sure these are set in Railway:

```bash
# Required
DATABASE_URL=<auto-set-by-railway-postgres>

# Optional (have defaults)
APP_NAME="Professional Hubs - Conflict API"
API_VERSION=v1
DEBUG=False
FUZZY_THRESHOLD=70
FUZZY_HIGH_CONFIDENCE=90
CORS_ORIGINS=*
TIMEZONE=America/Puerto_Rico
```

## Expected Build Time

- **First build:** 3-5 minutes (installs all dependencies)
- **Subsequent builds:** 1-2 minutes (uses Docker layer cache)

## If Deployment Still Fails

1. **Check Dockerfile exists:**
   ```bash
   ls -la Dockerfile
   ```

2. **Verify railway.toml:**
   ```bash
   cat railway.toml
   # Should show builder = "DOCKERFILE"
   ```

3. **Check Railway logs:**
   - Go to Railway dashboard
   - Click on deployment
   - Check "Build Logs" for specific errors

4. **Verify requirements.txt path:**
   ```bash
   ls -la conflict_api/requirements.txt
   # Should exist
   ```

5. **Contact support:**
   - Railway Discord: https://discord.gg/railway
   - Include build logs and error messages

## Success Indicators

When deployment succeeds, you'll see:

✅ **Build Logs:**
```
Step 1/10 : FROM python:3.11-slim
Step 2/10 : WORKDIR /app
...
Step 10/10 : CMD alembic upgrade head && gunicorn...
Successfully built abc123def456
```

✅ **Deploy Logs:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:8000
[INFO] Using worker class: uvicorn.workers.UvicornWorker
```

✅ **API Response:**
```bash
curl https://your-project.railway.app/health
# {"status":"healthy","service":"conflict-api"}
```

---

## Summary

The fix is simple: **Use Dockerfile instead of NIXPACKS**.

The Dockerfile provides:
- ✅ Guaranteed pip availability
- ✅ Explicit Python 3.11 environment
- ✅ Automatic database migrations
- ✅ Production-ready Gunicorn setup
- ✅ Works on any platform (Railway, AWS, GCP, local)

**Just commit the new files and redeploy!** 🚀
