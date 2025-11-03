#!/bin/bash
set -e

echo "🔍 Checking Python version..."
python3 --version

PY_VER=$(python3 -c "import sys; print(sys.version_info[:2] >= (3,12))")
if [ "$PY_VER" != "True" ]; then
  echo "❌ Required: Python 3.12 or higher. Installing..."
  brew install python@3.12
  echo 'export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"' >> ~/.zshrc
  source ~/.zshrc
fi

echo "✅ Using Python: $(python3 --version)"

# --- Create and activate virtual environment automatically ---
if [ ! -d "venv" ]; then
  echo "🐍 Creating virtual environment..."
  python3 -m venv venv
fi

echo "🔗 Activating virtual environment..."
source venv/bin/activate

echo "📦 Upgrading pip inside virtualenv..."
pip install --upgrade pip setuptools wheel

echo "📦 Upgrading pip..."
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip setuptools wheel

echo "🧱 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing build system (hatchling)..."
pip install hatchling

echo "📦 Installing dependencies from pyproject.toml..."

pip install docker>=6 rich>=13

# pip install black>=23 isort>=5 pytest>=7

echo "📦 Installing kaprese package..."
pip install .

echo "🎉 kaprese installation complete!"
echo "✅ To activate the virtual environment, run: source venv/bin/activate"
echo "Run with: kaprese --help"