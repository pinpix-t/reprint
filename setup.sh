#!/bin/bash

echo "Setting up Quality/Damage Analysis Dashboard..."

# Backend setup
echo "Setting up backend..."
cd backend
pip install -r ../requirements.txt
python -m spacy download en_core_web_sm
cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install
cd ..

echo "Setup complete!"
echo ""
echo "To run the backend:"
echo "  cd backend && uvicorn main:app --reload"
echo ""
echo "To run the frontend:"
echo "  cd frontend && npm run dev"

