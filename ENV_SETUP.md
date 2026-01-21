# Environment Setup Guide

This guide will help you set up the development environment for FlexiAI Toolsmith.

## Prerequisites

- **Python 3.12+** (Python 3.13 is also supported)
- **Conda** (Miniconda/Anaconda) - *optional but recommended*
- **Redis** - *optional, only needed if using Redis channel*

## Quick Setup

### Option 1: Automated Setup Script (Recommended)

Run the setup script:

```bash
./setup_env.sh
```

The script will:
- Check Python version
- Ask if you want to use Conda (if available)
- Create the environment (Conda or venv)
- Create `.env` file from template
- Provide activation instructions

### Option 2: Manual Setup with Conda

```bash
# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate .conda_flexiai
```

### Option 3: Manual Setup with venv

```bash
# Create virtual environment
python3 -m venv .venv

# Activate environment
source .venv/bin/activate  # On Linux/Mac
# OR
.venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### 1. Create `.env` file

Copy the template:

```bash
cp .env.template .env
```

### 2. Edit `.env` file

Open `.env` and configure the following **required** settings:

#### General Settings (Required)

```env
# Choose your AI provider
CREDENTIAL_TYPE=openai  # Options: openai, azure, deepseek, qwen, github_models

# Get this from your OpenAI/Azure dashboard
ASSISTANT_ID=your_assistant_id_here

# User identifier
USER_ID=default_user

# Active channels (comma-separated)
ACTIVE_CHANNELS=cli,quart  # Options: cli, redis, quart
```

#### Provider-Specific API Keys

**For OpenAI:**
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**For Azure OpenAI:**
```env
AZURE_OPENAI_API_KEY=your-azure-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

**For DeepSeek:**
```env
DEEPSEEK_API_KEY=your-deepseek-api-key-here
```

**For Qwen:**
```env
QWEN_API_KEY=your-qwen-api-key-here
```

**For GitHub Azure Inference:**
```env
GITHUB_TOKEN=your-github-token-here
```

### 3. Optional Settings

```env
# YouTube API Key (for YouTube search tool)
YOUTUBE_API_KEY=your-youtube-api-key

# Redis URL (if using Redis channel)
REDIS_URL=redis://localhost:6379/0

# Database URL (defaults to SQLite if not set)
DATABASE_URL=

# Secret key for Quart sessions
SECRET_KEY=your-secret-key-here
```

## Verify Installation

### Check Python version

```bash
python --version
# Should show Python 3.12 or higher
```

### Verify dependencies

```bash
python -c "import quart; import openai; print('✓ Dependencies OK')"
```

## Running the Application

### CLI Chat

```bash
python chat.py
```

### Web Chat (Quart + SSE)

```bash
hypercorn app:app --bind 127.0.0.1:8000 --workers 1
```

Then open: [http://127.0.0.1:8000/chat/](http://127.0.0.1:8000/chat/)

## Troubleshooting

### Issue: Python version too old

**Solution:** Install Python 3.12+ from [python.org](https://www.python.org/downloads/) or use conda:

```bash
conda install python=3.12
```

### Issue: Missing dependencies

**Solution:** Reinstall requirements:

```bash
pip install -r requirements.txt
```

### Issue: Redis connection error

**Solution:** 
- Install Redis: `sudo apt-get install redis-server` (Linux) or use Docker
- Or remove `redis` from `ACTIVE_CHANNELS` in `.env`

### Issue: Module not found errors

**Solution:** Make sure your virtual environment is activated:

```bash
# Check if activated (should show your venv path)
which python

# If not activated, activate it
source .venv/bin/activate  # or conda activate .conda_flexiai
```

### Issue: API key errors

**Solution:** 
- Verify your `.env` file exists and contains the correct API keys
- Check that `CREDENTIAL_TYPE` matches your provider
- Ensure no extra spaces or quotes around values in `.env`

## Additional Notes

- The `.env` file is git-ignored for security
- Always use `.env.template` as a reference
- For production, use strong `SECRET_KEY` values
- Redis is optional unless you're using the Redis channel

## Next Steps

1. ✅ Environment set up
2. ✅ `.env` configured
3. 🚀 Run the application
4. 📖 Read the main [README.md](README.md) for usage details
