#!/bin/bash

echo "Setting up Django Backend for Smart Griev..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
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
echo "Seeding database with departments..."
python manage.py seed_db

echo ""
echo "Setup complete!"
echo ""
echo "To start the server, run:"
echo "  source venv/bin/activate  # On Linux/Mac"
echo "  venv\\Scripts\\activate    # On Windows"
echo "  python manage.py runserver 0.0.0.0:5000"
