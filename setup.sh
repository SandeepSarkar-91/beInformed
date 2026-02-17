#!/bin/bash

# beInformed Flask UI Quick Start Script

echo "🚀 Starting beInformed Flask UI Setup..."
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed!"
    echo "Please install PostgreSQL first:"
    echo "  - Option 1: brew install postgresql"
    echo "  - Option 2: Download Postgres.app from https://postgresapp.com/"
    exit 1
fi

echo "✅ PostgreSQL found"

# Check if database exists
if psql -lqt | cut -d \| -f 1 | grep -qw beInformed; then
    echo "✅ Database 'beInformed' already exists"
else
    echo "📦 Creating database 'beInformed'..."
    createdb beInformed
    if [ $? -eq 0 ]; then
        echo "✅ Database created successfully"
    else
        echo "❌ Failed to create database"
        echo "You may need to start PostgreSQL first:"
        echo "  brew services start postgresql"
        exit 1
    fi
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env and update DATABASE_URL if needed"
else
    echo "✅ .env file exists"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the Flask application, run:"
echo "  python3 app.py"
echo ""
echo "Then visit: http://localhost:5001"
echo ""
