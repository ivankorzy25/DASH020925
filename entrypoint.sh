#!/bin/sh

# Abort on any error
set -e

# Path to the lock file
INIT_LOCK_FILE="/app/.initialized"

# Check if the initialization has already been done
if [ ! -f "$INIT_LOCK_FILE" ]; then
    echo "First time setup: Initializing the application (database, users, etc.)..."
    
    # Run the initialization
    python run.py init
    
    # Create the lock file to prevent re-initialization
    touch "$INIT_LOCK_FILE"
    
    echo "Initialization complete."
else
    echo "Application already initialized. Skipping setup."
fi

# Start the Streamlit application
echo "Starting Streamlit server..."
exec python -m streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0
