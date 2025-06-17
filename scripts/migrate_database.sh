#!/bin/bash
# Database migration script for StickForStats Production Environment
# This script performs safe database migrations with proper backup and verification

# Set error handling
set -e
set -o pipefail

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PROJECT_ROOT="/Users/vishalbharti/Downloads/StickForStats_Migration/new_project"
BACKUP_DIR="$PROJECT_ROOT/backups"
LOG_FILE="$BACKUP_DIR/migrations.log"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Log function
log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

# Check if running in production or with --force flag
check_environment() {
    if [ "$1" != "--force" ] && [ -z "$PRODUCTION" ]; then
        echo "This script is intended for production environments."
        echo "Set PRODUCTION=1 before running or use --force to override."
        exit 1
    fi
}

# Backup database before migration
backup_database() {
    log "Creating pre-migration database backup..."
    
    # Create backup directory for this run
    MIGRATION_BACKUP_DIR="$BACKUP_DIR/pre_migration_$TIMESTAMP"
    mkdir -p "$MIGRATION_BACKUP_DIR"
    
    # Database backup filename
    DB_BACKUP_FILE="$MIGRATION_BACKUP_DIR/stickforstats_db_$TIMESTAMP.sql.gz"
    
    # Create database backup using Docker
    cd "$PROJECT_ROOT"
    
    log "Executing database dump..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db \
        pg_dump -U postgres -d stickforstats \
        | gzip > "$DB_BACKUP_FILE"
    
    # Check if backup was successful
    if [ $? -eq 0 ] && [ -f "$DB_BACKUP_FILE" ]; then
        log "Pre-migration backup completed successfully: $DB_BACKUP_FILE"
        echo "Backup created at: $DB_BACKUP_FILE"
    else
        log "ERROR: Pre-migration backup failed!"
        echo "Failed to create backup. Migration aborted."
        exit 1
    fi
}

# Check for unapplied migrations without applying them
check_migrations() {
    log "Checking for unapplied migrations..."
    
    cd "$PROJECT_ROOT"
    
    # Run showmigrations to see status
    MIGRATIONS_OUTPUT=$(docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T web python manage.py showmigrations)
    
    # Check if there are any unapplied migrations
    if echo "$MIGRATIONS_OUTPUT" | grep -q "\[ \]"; then
        log "Unapplied migrations found:"
        echo "$MIGRATIONS_OUTPUT" | grep "\[ \]" | tee -a "$LOG_FILE"
        return 0
    else
        log "No unapplied migrations found."
        return 1
    fi
}

# Apply migrations
apply_migrations() {
    log "Applying database migrations..."
    
    cd "$PROJECT_ROOT"
    
    # Run migrations
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T web python manage.py migrate
    
    # Check migration status
    if [ $? -eq 0 ]; then
        log "Migrations applied successfully."
        return 0
    else
        log "ERROR: Migration failed!"
        return 1
    fi
}

# Verify database integrity after migration
verify_database() {
    log "Verifying database integrity..."
    
    cd "$PROJECT_ROOT"
    
    # Run a series of checks to verify database integrity
    
    # Check 1: Run Django's check command
    log "Running Django system checks..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T web python manage.py check
    
    if [ $? -ne 0 ]; then
        log "ERROR: Django system check failed!"
        return 1
    fi
    
    # Check 2: Verify models
    log "Verifying models..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T web python manage.py validate_models
    
    if [ $? -ne 0 ]; then
        log "ERROR: Model validation failed!"
        return 1
    fi
    
    # Check 3: Try to access the database via a simple query
    log "Testing database access..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T web python -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1')
result = cursor.fetchone()
assert result[0] == 1, 'Database connectivity test failed'
print('Database connectivity verified')
"
    
    if [ $? -ne 0 ]; then
        log "ERROR: Database access test failed!"
        return 1
    fi
    
    log "Database integrity verification completed successfully."
    return 0
}

# Restore database if migration failed
restore_database() {
    log "Migration failed! Attempting to restore database from backup..."
    
    cd "$PROJECT_ROOT"
    
    # Database backup filename
    DB_BACKUP_FILE="$MIGRATION_BACKUP_DIR/stickforstats_db_$TIMESTAMP.sql.gz"
    
    # Drop the current database and recreate it
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db psql -U postgres -c "DROP DATABASE stickforstats;"
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db psql -U postgres -c "CREATE DATABASE stickforstats OWNER postgres;"
    
    # Restore from backup
    gunzip -c "$DB_BACKUP_FILE" | docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db psql -U postgres -d stickforstats
    
    if [ $? -eq 0 ]; then
        log "Database restored successfully from backup."
        echo "Database restored successfully from backup."
    else
        log "ERROR: Database restoration failed!"
        echo "CRITICAL ERROR: Database restoration failed! Manual intervention required."
        echo "Backup file is located at: $DB_BACKUP_FILE"
    fi
}

# Main execution
main() {
    log "=== StickForStats Database Migration Process Started ==="
    
    # Check if running in production or with --force flag
    check_environment "$1"
    
    # Check for unapplied migrations
    if check_migrations; then
        # Backup database before migration
        backup_database
        
        # Confirm migration with user
        echo "Ready to apply migrations. Continue? [y/N]"
        read -r confirm
        
        if [[ "$confirm" =~ ^[Yy]$ ]]; then
            # Apply migrations
            if apply_migrations; then
                # Verify database integrity
                if verify_database; then
                    log "Migration completed successfully."
                    echo "Migration completed successfully."
                else
                    log "Database verification failed after migration."
                    echo "Database verification failed. Attempting to restore..."
                    restore_database
                fi
            else
                # Migration failed, restore database
                log "Migration failed."
                echo "Migration failed. Attempting to restore..."
                restore_database
            fi
        else
            log "Migration cancelled by user."
            echo "Migration cancelled."
        fi
    else
        echo "No migrations to apply."
    fi
    
    log "=== StickForStats Database Migration Process Completed ==="
}

# Run the main function
main "$1"
exit $?