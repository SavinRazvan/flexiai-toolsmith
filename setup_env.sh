#!/bin/bash
# FlexiAI Toolsmith Environment Setup Script
# This script helps set up the development environment

set -e  # Exit on error

echo "🚀 FlexiAI Toolsmith Environment Setup"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.12+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Check Python version (should be 3.12+)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 12 ]); then
    echo "⚠️  Warning: Python 3.12+ is recommended. You have Python $PYTHON_VERSION"
fi

# Check if conda is available
USE_CONDA=false
if command -v conda &> /dev/null; then
    echo "✓ Conda is available"
    read -p "Do you want to use Conda? (y/n) [y]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        USE_CONDA=true
    fi
fi

# Setup environment
if [ "$USE_CONDA" = true ]; then
    echo ""
    echo "📦 Setting up Conda environment..."
    conda env create -f environment.yml
    echo ""
    echo "✅ Conda environment created!"
    echo ""
    echo "To activate the environment, run:"
    echo "  conda activate .conda_flexiai"
else
    echo ""
    echo "📦 Setting up Python virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created!"
    echo ""
    echo "To activate the environment, run:"
    echo "  source .venv/bin/activate  # On Linux/Mac"
    echo "  .venv\\Scripts\\activate     # On Windows"
    echo ""
    echo "Then install dependencies:"
    echo "  pip install -r requirements.txt"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    if [ -f .env.template ]; then
        cp .env.template .env
        echo "✅ .env file created from .env.template"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and fill in your configuration values!"
    else
        echo "⚠️  .env.template not found. Please create .env manually."
    fi
else
    echo ""
    echo "✓ .env file already exists"
fi

echo ""
echo "======================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate your environment (see commands above)"
echo "2. Edit .env file with your API keys and settings"
echo "3. Run the application:"
echo "   - CLI: python chat.py"
echo "   - Web: hypercorn app:app --bind 127.0.0.1:8000"
echo ""
