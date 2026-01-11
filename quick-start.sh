#!/bin/bash
# Quick Start Script for Smart Griev Development

set -e

echo "================================"
echo "Smart Griev - Quick Start Setup"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}[1/4]${NC} Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Found: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Setup Backend
echo ""
echo -e "${BLUE}[2/4]${NC} Setting up backend..."
cd backend_django

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Download NLP data
echo "Downloading NLP data (one-time setup)..."
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True)" 2>/dev/null || true

echo -e "${GREEN}✓${NC} Backend setup complete"

# Return to project root
cd ..

# Setup Frontend
echo ""
echo -e "${BLUE}[3/4]${NC} Setting up frontend..."

# Check pnpm/npm
if command -v pnpm &> /dev/null; then
    PKG_MANAGER="pnpm"
    echo -e "${GREEN}✓${NC} Found: pnpm"
elif command -v npm &> /dev/null; then
    PKG_MANAGER="npm"
    echo -e "${GREEN}✓${NC} Found: npm"
else
    echo "❌ Neither pnpm nor npm found. Please install Node.js"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    $PKG_MANAGER install -q
fi

echo -e "${GREEN}✓${NC} Frontend setup complete"

# Print next steps
echo ""
echo -e "${BLUE}[4/4]${NC} Setup complete! Next steps:"
echo ""
echo -e "${GREEN}Terminal 1 - Start Backend:${NC}"
echo "  cd backend_django"
echo "  source venv/bin/activate"
echo "  python manage.py runserver 0.0.0.0:8000"
echo ""
echo -e "${GREEN}Terminal 2 - Start Frontend:${NC}"
echo "  $PKG_MANAGER dev"
echo ""
echo -e "${GREEN}Then open:${NC}"
echo "  http://localhost:3000"
echo ""
echo -e "${GREEN}Run Tests:${NC}"
echo "  cd backend_django"
echo "  python manage.py test api -v 2"
echo ""
echo "================================"
echo -e "${GREEN}Happy coding! 🚀${NC}"
echo "================================"
