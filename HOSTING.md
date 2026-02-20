# Hosting Finance Tracker Online

This guide covers the best approaches to run the Finance Tracker app in the cloud so it’s user-friendly and ready for online use.

---

## 1. Streamlit Community Cloud (recommended for quick deploy)

**Best for:** Getting a public URL quickly with minimal setup.

### Steps

1. **Push your app to GitHub**  
   - Use a **private** repo if the code or data is sensitive.  
   - Ensure `requirements.txt` is at the repo root.

2. **Go to [share.streamlit.io](https://share.streamlit.io)**  
   - Sign in with GitHub and choose your repo.

3. **Configure the app**  
   - **Main file path:** `finance_tracker.py`  
   - **Python version:** 3.9 or 3.10 (match your local version)

4. **Secrets (optional)**  
   - In the Cloud UI: **Settings → Secrets**.  
   - Or add a `.streamlit/secrets.toml` file (do not commit real secrets; use the Cloud UI for production).  
   - You can use secrets for things like API keys or overrides; the app currently runs without them.

5. **Deploy**  
   - Click **Deploy**. The first run may take a few minutes while dependencies install.

### Important for Streamlit Cloud

- **Database:** The app uses a SQLite file (`finance_tracker.db`) by default. On Streamlit Cloud, the filesystem is **ephemeral**: the DB is reset on each redeploy or after inactivity. For persistent data you’d need an external DB (e.g. PostgreSQL) and code changes; for personal/demo use, the default is fine.
- **Sleep:** Free apps sleep after inactivity; the first load after sleep can be slow.
- **Security:** Use strong passwords and consider making the app private (e.g. Streamlit’s sharing settings or a reverse proxy with auth) if it holds real financial data.

---

## 2. Docker (best for control and portability)

**Best for:** Running the same setup locally and on any cloud (AWS, GCP, Azure, Railway, Fly.io, etc.).

### Dockerfile example

Create `Dockerfile` in the project root:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs dir and optional data volume mount point
RUN mkdir -p logs

# Use env for DB path so host can mount a volume (see below)
ENV FINANCE_TRACKER_DB_PATH=/data/finance_tracker.db

EXPOSE 8501

CMD ["streamlit", "run", "finance_tracker.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Run locally

```bash
# Build
docker build -t finance-tracker .

# Run (persist DB in a volume)
docker run -p 8501:8501 -v finance_tracker_data:/data finance-tracker
```

### Using environment variables

- **`FINANCE_TRACKER_DB_PATH`** – Path to the SQLite database file. Set to a path inside a mounted volume (e.g. `/data/finance_tracker.db`) so data survives restarts.  
- Optional: add more env vars for config (e.g. feature flags) and document them in `.env.example`.

---

## 3. Cloud platforms (VPS / PaaS)

You can run the app on any host that supports Python or Docker.

| Platform        | Good for                          | Notes                                                                 |
|-----------------|------------------------------------|-----------------------------------------------------------------------|
| **Railway**     | Simple Docker or Python deploy     | Mount volume for `/data` and set `FINANCE_TRACKER_DB_PATH`            |
| **Fly.io**      | Global regions, Docker             | Use a volume for the DB path                                         |
| **Google Cloud Run** | Serverless containers         | Use Cloud SQL or a volume for persistence                             |
| **AWS (ECS / EC2)**  | Full control, compliance     | Put DB on EBS or RDS; use env for DB path or connection string       |
| **Hugging Face Spaces** | Free demo, Streamlit native | Similar to Streamlit Cloud (ephemeral storage unless you add external DB) |

General steps:

1. Build the Docker image (or use `pip install -r requirements.txt` and run `streamlit run finance_tracker.py`).
2. Set **`FINANCE_TRACKER_DB_PATH`** to a persistent path (or later, to a real database URL).
3. Expose port **8501** and set the app URL in the platform.

---

## 4. Security and user-friendliness for production

- **HTTPS:** Use a host that provides HTTPS (Streamlit Cloud, Railway, Fly, etc. do this by default).
- **Authentication:** The app has its own login; keep strong passwords and consider limiting signups if it’s only for you.
- **Secrets:** Never commit `.env` or `config.yaml` with real credentials. Use the platform’s secrets or env vars.
- **Backups:** If using SQLite on a volume, back up the DB file regularly (e.g. cron + cloud storage).
- **Updates:** Pin versions in `requirements.txt` and redeploy after updating dependencies.

---

## 5. Quick reference

| Goal                    | Approach                    |
|-------------------------|----------------------------|
| Easiest public URL      | Streamlit Community Cloud  |
| Persistent data + control| Docker + volume + env DB path |
| Same setup everywhere   | Dockerfile + env vars      |
| Production / compliance | VPS or cloud + external DB (future) |

For a **user-friendly, host-online setup**, start with **Streamlit Community Cloud** for a quick shareable link, or **Docker** with a volume and **`FINANCE_TRACKER_DB_PATH`** for persistent data and portability.
