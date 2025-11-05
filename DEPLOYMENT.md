# Comprehensive Deployment Guide

This guide provides step-by-step instructions to deploy `ai-agents` in various environments.

---

## 1. Local Deployment (Flask API + Web App)

### Prerequisites
- Python 3.8+
- pip

### Steps
1. Clone the repository:
    ```sh
git clone https://github.com/R-c-8008/ai-agents.git
cd ai-agents
```
2. Create and activate a virtual environment:
    ```sh
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate   # Windows
```
3. Install dependencies:
    ```sh
pip install -r requirements.txt
```
4. Set environment variables (see section 5).
5. Run the Flask API:
    ```sh
flask run
```
6. Access the web app at `http://localhost:5000`

---

## 2. Cloud Deployment

### (a) Heroku
1. Sign up at [Heroku](https://heroku.com) and install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).
2. Create a `Procfile` in the root directory (if not present):
    ```Procfile
web: flask run
```
3. Initialize Git, add, and commit changes.
4. Deploy:
    ```sh
heroku create
heroku config:set VAR_NAME=value # Set environment variables
heroku git:remote -a <app-name>
git push heroku main
```
5. Visit the provided Heroku URL.

### (b) Railway
1. Sign up at [Railway](https://railway.app).
2. Create a new project, link your GitHub repo, and set up environment variables.
3. Railway auto-builds your app. 

### (c) Render
1. Sign up at [Render](https://render.com).
2. Create a new Web Service, connect your repository, and set build commands:
    - Build Command: `pip install -r requirements.txt`
    - Start Command: `flask run`
3. Set environment variables in the Render dashboard.

---

## 3. Chrome Extension Publishing

1. Edit or build the extension according to your requirements.
2. Zip extension files (manifest.json, scripts, UI files, etc.).
3. Visit [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole/).
4. Pay the registration fee (if not paid).
5. Upload zip file, add details, and publish.
6. Extension will be reviewed prior to public listing.

---

## 4. Docker Deployment

### Build and Run Locally
1. Build the Docker image:
    ```sh
docker build -t ai-agents .
```
2. Run the container:
    ```sh
docker run -d -p 5000:5000 --env-file .env ai-agents
```
   - Ensure `.env` contains required environment variables (see section 5).

### Docker Compose (Multi-service)
Create `docker-compose.yml`:
```yaml
version: "3"
services:
  web:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
```
Run with:
```sh
docker-compose up --build
```

---

## 5. Environment Variables Setup

Create a `.env` file in the root or set variables in cloud dashboards. Example variables:
```
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
API_KEY=your-api-key
```
Set/add as needed per your application.

---

## 6. Production Considerations

- **Use production-ready web servers**: e.g., Gunicorn/UWSGI for Python apps in cloud/Docker
- **Security**: Never expose secret keys; use encrypted variables for cloud
- **Scaling**: Consider service autoscaling and database backups
- **Monitoring**: Integrate tools such as [Sentry](https://sentry.io/), [Prometheus](https://prometheus.io/)
- **Logging**: Persistent and centralized logging (stdout in Docker, cloud log dashboards)
- **HTTPS**: Terminate SSL at the CDN or Proxy where possible (Heroku, Render, etc.)

---

## Need Help?
Open an issue in the repository for deployment assistance.

---
