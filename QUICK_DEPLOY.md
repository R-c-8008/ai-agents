# 🚀 Quick Deploy to Railway.app

## Why Railway is the Best Free Option

Railway.app stands out as the best free deployment platform for this AI Agents project for several reasons:

- **✅ Free Tier**: $5 monthly credit (enough for small-to-medium projects)
- **✅ Zero Configuration**: Automatic detection of Python applications
- **✅ GitHub Integration**: Direct deployment from your repository
- **✅ Persistent Storage**: Built-in PostgreSQL and Redis support
- **✅ Easy Environment Variables**: Simple web UI for configuration
- **✅ Automatic HTTPS**: Free SSL certificates included
- **✅ Fast Deployment**: Typically deploys in under 2 minutes
- **✅ Real-time Logs**: Live logging and monitoring dashboard
- **✅ No Sleep Mode**: Unlike Heroku free tier, your app stays active

## 📦 One-Click Deploy

Click the button below to deploy instantly:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/new?template=https://github.com/R-c-8008/ai-agents)

## 📋 Step-by-Step Deployment Guide

### Step 1: Sign Up for Railway

1. Go to [Railway.app](https://railway.app)
2. Click "Login" in the top-right corner
3. Sign in with your GitHub account (recommended for seamless integration)
4. Authorize Railway to access your GitHub repositories

**Screenshot Description**: *Railway homepage with a clean purple gradient interface, featuring "Login" button in the top navigation*

### Step 2: Create New Project

1. From your Railway dashboard, click "+ New Project"
2. Select "Deploy from GitHub repo"
3. Choose the `R-c-8008/ai-agents` repository from the list
4. Railway will automatically detect it as a Python project

**Screenshot Description**: *Railway dashboard showing project creation options - "Deploy from GitHub repo", "Deploy from template", "Provision PostgreSQL", etc.*

### Step 3: Configure Your Project

1. Once Railway detects your repo, it will show a configuration preview
2. Click "Add variables" to set up environment variables (see section below)
3. Railway will automatically:
   - Detect `requirements.txt` or `pyproject.toml`
   - Set up Python environment
   - Install dependencies
   - Start your application

**Screenshot Description**: *Project configuration screen showing detected buildpack (Python), start command, and environment variables section*

### Step 4: Set Up Environment Variables

Click on your deployed service, then go to the "Variables" tab. Add the following required variables:

#### Required Variables:

```bash
# AI Provider API Keys (add at least one)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Application Configuration
PORT=8000
ENVIRONMENT=production

# Database (if using PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Auto-populated if you add Postgres

# Optional: API Security
API_SECRET_KEY=your_random_secret_key_here
ALLOWED_ORIGINS=https://your-domain.com
```

#### How to Add Variables:

1. Click on your service name in the project
2. Navigate to the "Variables" tab
3. Click "+ New Variable"
4. Enter variable name and value
5. Click "Add" for each variable
6. Railway will automatically redeploy with new variables

**Screenshot Description**: *Variables configuration panel showing a list of environment variables with "+ New Variable" button and variable name/value input fields*

### Step 5: Monitor Deployment

1. Go to the "Deployments" tab to see build progress
2. Watch real-time logs in the "Build Logs" section
3. Successful deployment shows "SUCCESS" status with a green checkmark
4. Build typically takes 1-3 minutes

**Screenshot Description**: *Deployment logs screen showing real-time console output with build steps: "Installing dependencies", "Building application", "Deployment successful"*

### Step 6: Access Your Deployed Application

1. Once deployed, go to the "Settings" tab
2. Scroll to the "Domains" section
3. Click "Generate Domain" to get a free Railway subdomain
4. Your app will be available at: `https://your-app-name.up.railway.app`
5. (Optional) Add a custom domain in the same section

**Screenshot Description**: *Settings page showing Domains section with "Generate Domain" button and a field showing the generated URL format*

## 🔧 Advanced Configuration

### Adding a Database

If your AI agents need persistent storage:

1. Click "+ New" in your project
2. Select "Database" → "Add PostgreSQL"
3. Railway automatically creates and links the database
4. Access connection string via `${{Postgres.DATABASE_URL}}` variable

### Custom Domain Setup

1. Go to "Settings" → "Domains"
2. Click "Custom Domain"
3. Enter your domain name
4. Add the provided CNAME record to your DNS provider
5. Wait for DNS propagation (usually 5-60 minutes)

### Configuring Start Command

If Railway doesn't auto-detect your start command:

1. Go to "Settings" → "Deploy"
2. Find "Start Command" section
3. Add your custom command, e.g.:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
   or
   ```bash
   python app.py
   ```

## 🐛 Troubleshooting Tips

### Issue: Build Fails

**Solution:**
- Check "Build Logs" for specific error messages
- Ensure `requirements.txt` or `pyproject.toml` is in the root directory
- Verify all dependencies are compatible with Linux environment
- Check Python version compatibility (add `runtime.txt` if needed)

### Issue: Application Crashes on Start

**Solution:**
- Review "Deploy Logs" for runtime errors
- Verify all required environment variables are set
- Ensure your app listens on `0.0.0.0:$PORT` (Railway provides PORT variable)
- Check that API keys are valid and have sufficient quota

### Issue: "Module Not Found" Error

**Solution:**
- Confirm the module is listed in `requirements.txt`
- Try pinning specific versions: `openai==1.3.0` instead of `openai`
- Clear build cache: Go to Settings → Click "Restart" with "Clear Cache" option

### Issue: Environment Variables Not Working

**Solution:**
- After adding/changing variables, Railway auto-redeploys
- Wait for redeployment to complete (check Deployments tab)
- Verify variable names match exactly (they're case-sensitive)
- Check logs to see if variables are being loaded: `echo $VARIABLE_NAME`

### Issue: App Works Locally But Not on Railway

**Solution:**
- Check for hardcoded localhost URLs - use environment variables instead
- Verify file paths (use relative paths, not absolute)
- Ensure database connections use Railway's provided URLs
- Check that your app binds to `0.0.0.0` not `127.0.0.1`

### Issue: Free Tier Limits Exceeded

**Solution:**
- Railway provides $5/month free credit
- Monitor usage in "Project Settings" → "Usage"
- Optimize your application to reduce resource consumption
- Consider upgrading to the Hobby plan ($5/month) for more resources
- Implement caching to reduce API calls and processing

### Issue: Deployment Takes Too Long

**Solution:**
- Large dependencies can slow builds - consider using lighter alternatives
- Use `.railwayignore` file to exclude unnecessary files (similar to `.gitignore`)
- Check if you're installing heavy packages like TensorFlow unnecessarily
- Split services if you have multiple applications

### Issue: Cannot Access Application URL

**Solution:**
- Ensure domain was generated (Settings → Domains → Generate Domain)
- Check if deployment is actually running (green status in Deployments)
- Verify your application is listening on the PORT variable
- Review firewall settings if using custom domain
- Clear browser cache or try incognito mode

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Railway CLI Guide](https://docs.railway.app/develop/cli)
- [Environment Variables Best Practices](https://docs.railway.app/develop/variables)
- [Custom Domains Setup](https://docs.railway.app/deploy/exposing-your-app)
- [Railway Discord Community](https://discord.gg/railway)

## 💡 Pro Tips

1. **Use Railway CLI** for faster deployments from terminal:
   ```bash
   npm i -g @railway/cli
   railway login
   railway link
   railway up
   ```

2. **Set up automatic deployments**: Railway auto-deploys on git push to main branch

3. **Monitor costs**: Check "Usage" tab regularly to stay within free tier

4. **Use health checks**: Implement a `/health` endpoint for Railway to monitor

5. **Enable PR deployments**: Get temporary URLs for each pull request (Settings → Enable PR Deploys)

6. **Secrets management**: Never commit API keys - always use environment variables

7. **Logging**: Use `print()` or proper logging libraries - Railway captures stdout/stderr

8. **Rollback capability**: Railway keeps deployment history - easy to rollback from Deployments tab

## 🎉 Success!

Once deployed, your AI agents will be running 24/7 on Railway's infrastructure. Share your deployment URL and start using your agents from anywhere!

**Need help?** Open an issue in this repository or ask in [Railway's Discord](https://discord.gg/railway).

---

*Last updated: November 2025*
*Railway.app pricing and features subject to change*
