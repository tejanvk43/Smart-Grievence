#!/bin/bash

echo "========================================="
echo "Smart Griev - Complete Setup"
echo "========================================="
echo ""

# Frontend Setup
echo "[1/2] Setting up Frontend..."
echo "Installing frontend dependencies..."
pnpm install

echo ""
echo "[2/2] Setting up Django Backend..."
cd backend_django

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"

# Run migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Seed database
echo "Seeding database..."
python manage.py seed_db

cd ..

echo ""
echo "========================================="
echo "✓ Setup Complete!"
echo "========================================="
echo ""
echo "To run the project:"
echo ""
echo "Terminal 1 (Frontend):"
echo "  pnpm dev"
echo ""
echo "Terminal 2 (Backend):"
echo "  cd backend_django"
echo "  source venv/bin/activate"
echo "  python manage.py runserver 0.0.0.0:5000"
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:5000"
echo "========================================="
