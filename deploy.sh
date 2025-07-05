#!/bin/bash

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Railway CLI not found. Please install it first:"
    echo "https://docs.railway.app/reference/cli/"
    exit 1
fi

# Login to Railway if not already logged in
if ! railway whoami &> /dev/null; then
    echo "Not logged in to Railway. Please login first:"
    railway login
fi

# Create new project if not exists
if ! railway project list | grep -q "vortexfetchbot"; then
    echo "Creating new Railway project..."
    railway project create vortexfetchbot
fi

# Set project
railway project switch vortexfetchbot

# Initialize Railway
if [ ! -d ".railway" ]; then
    railway init
fi

# Add environment variables
railway env set BOT_TOKEN "$BOT_TOKEN"
railway env set ADMIN_ID "$ADMIN_ID"

# Deploy to Railway
railway up --yes

# Show deployment URL
railway link
