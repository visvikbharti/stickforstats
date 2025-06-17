#!/bin/bash

# Exit on error
set -e

echo "🚀 Setting up StickForStats Django Development Environment"
echo "=========================================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Using Python $python_version"

# Check for PostgreSQL
if command -v psql &> /dev/null; then
    echo "✓ PostgreSQL is installed"
else
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL 14+ with pgvector extension."
    exit 1
fi

# Check for Redis
if command -v redis-cli &> /dev/null; then
    echo "✓ Redis is installed"
else
    echo "❌ Redis is not installed. Please install Redis 6+."
    exit 1
fi

# Check for Node.js
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo "✓ Node.js $node_version is installed"
else
    echo "❌ Node.js is not installed. Please install Node.js 16+."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Using existing virtual environment"
fi

# Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo "🔄 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create required directories
echo "📁 Creating required directories..."
mkdir -p media staticfiles logs

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔐 Creating .env file..."
    cat > .env << EOL
DEBUG=True
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://postgres:postgres@localhost:5432/stickforstats
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
EMAIL_URL=console://
EOL
    echo "✓ Created .env file"
else
    echo "✓ Using existing .env file"
fi

# Create PostgreSQL database if it doesn't exist
echo "🛢️ Checking PostgreSQL database..."
if psql -lqt | cut -d \| -f 1 | grep -qw stickforstats; then
    echo "✓ Database 'stickforstats' already exists"
else
    echo "🛢️ Creating PostgreSQL database..."
    createdb stickforstats
    echo "✓ Database 'stickforstats' created"
fi

# Add pgvector extension to database
echo "🔍 Adding pgvector extension to database..."
psql -d stickforstats -c "CREATE EXTENSION IF NOT EXISTS vector;" || {
    echo "❌ Failed to add pgvector extension. Please install it and try again."
    echo "   See https://github.com/pgvector/pgvector for installation instructions."
}

# Apply migrations
echo "🔄 Applying database migrations..."
python manage.py migrate

# Create superuser if needed
echo "👤 Do you want to create a superuser? (y/n)"
read -r create_superuser
if [[ $create_superuser =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend || { echo "❌ Frontend directory not found"; exit 1; }
npm install
cd ..

# Collect static files
echo "📚 Collecting static files..."
python manage.py collectstatic --noinput

echo "
✅ Setup complete! 

To run the application:

1. Start the Django development server:
   python manage.py runserver

2. In a separate terminal, start Celery worker:
   celery -A stickforstats worker -l INFO

3. In a separate terminal, start Celery beat:
   celery -A stickforstats beat -l INFO

4. In a separate terminal, start the frontend development server:
   cd frontend && npm start

The application will be available at:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Admin interface: http://localhost:8000/admin
"