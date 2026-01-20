#!/bin/bash

# Automatic Setup - CV Generator

cd "$(dirname "$0")"

echo ""
echo "🚀 CV Generator Setup"
echo "======================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    echo "Install Python 3 from https://www.python.org"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create venv
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q reportlab
echo "✓ Dependencies installed"

# Validate cv_data.json
echo "✓ Validating cv_data.json..."
python3 -c "from cv_generator import CVGenerator; CVGenerator('cv_data.json')" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ cv_data.json valid"
else
    echo "⚠️  cv_data.json has issues (verify and try again)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit cv_data.json with your data"
echo "  2. Execute: ./start_mac.sh"
echo ""
