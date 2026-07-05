#!/bin/bash

echo "Starting Keycloak and Postgres dependencies via Docker..."
docker compose up -d postgres keycloak

# Give Keycloak a moment to start
sleep 5

echo "Starting Backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting Frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

wait
