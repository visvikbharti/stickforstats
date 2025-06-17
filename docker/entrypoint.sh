#!/bin/bash

set -e

# Function to wait for the database
wait_for_db() {
    echo "Waiting for database to be ready..."
    
    if [ "$DATABASE_ENGINE" == "django.db.backends.postgresql" ]; then
        # If PostgreSQL - Use environment for authentication
        export PGPASSWORD="$DATABASE_PASSWORD"
        until psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c '\q' 2>/dev/null; do
          >&2 echo "PostgreSQL is unavailable - sleeping"
          sleep 1
        done
        unset PGPASSWORD
    else
        # For other databases or SQLite, just wait a bit
        sleep 5
    fi
    
    >&2 echo "Database is ready\!"
}

# Apply database migrations with error handling
apply_migrations() {
    echo "Applying database migrations..."
    if ! python manage.py migrate --noinput; then
        >&2 echo "Failed to apply migrations"
        exit 1
    fi
}

# Collect static files with error handling
collect_static() {
    echo "Collecting static files..."
    if ! python manage.py collectstatic --noinput; then
        >&2 echo "Failed to collect static files"
        exit 1
    fi
}

# Create cache tables if needed
create_cache_tables() {
    echo "Creating cache tables..."
    python manage.py createcachetable
}

# Start Gunicorn server
start_gunicorn() {
    echo "Starting Gunicorn server..."
    exec "$@"
}

# Main execution flow - production only
main() {
    # Wait for the database to be ready
    wait_for_db
    
    # Apply database migrations
    apply_migrations
    
    # Collect static files
    collect_static
    
    # Create cache tables
    create_cache_tables
    
    # Register modules (if available)
    if [ -f "register_modules.py" ]; then
        echo "Registering modules..."
        if ! python register_modules.py; then
            >&2 echo "Failed to register modules"
            exit 1
        fi
    fi
    
    # Start the application
    start_gunicorn "$@"
}

# Run main function
main "$@"