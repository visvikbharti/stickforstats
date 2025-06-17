#!/bin/bash
# Database backup script for StickForStats Production Environment
# This script creates database backups and manages retention

# Set error handling
set -e
set -o pipefail

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_ROOT="/var/backups/stickforstats"
DB_BACKUP_DIR="$BACKUP_ROOT/database"
MEDIA_BACKUP_DIR="$BACKUP_ROOT/media"
LOG_FILE="$BACKUP_ROOT/backup.log"
RETENTION_DAYS=30
S3_BUCKET="stickforstats-backups"
PROJECT_ROOT="/home/stickforstats/production"

# Load environment variables from .env.prod if it exists
if [ -f "$PROJECT_ROOT/.env.prod" ]; then
    source "$PROJECT_ROOT/.env.prod"
fi

# Ensure backup directories exist
mkdir -p "$DB_BACKUP_DIR"
mkdir -p "$MEDIA_BACKUP_DIR"
mkdir -p "$BACKUP_ROOT/logs"

# Log function
log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

# Database backup function
backup_database() {
    log "Starting database backup..."
    
    # Database backup filename
    DB_BACKUP_FILE="$DB_BACKUP_DIR/stickforstats_db_$TIMESTAMP.sql.gz"
    
    # Create database backup using Docker
    log "Creating database dump..."
    cd "$PROJECT_ROOT"
    
    # Use the Docker Compose file to access the PostgreSQL container
    docker-compose -f docker-compose.prod.yml exec -T db \
        pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
        | gzip > "$DB_BACKUP_FILE"
    
    # Check if backup was successful
    if [ $? -eq 0 ] && [ -f "$DB_BACKUP_FILE" ]; then
        log "Database backup completed successfully: $DB_BACKUP_FILE ($(du -h "$DB_BACKUP_FILE" | cut -f1))"
    else
        log "ERROR: Database backup failed!"
        return 1
    fi
}

# Media files backup function
backup_media_files() {
    log "Starting media files backup..."
    
    # Media backup filename
    MEDIA_BACKUP_FILE="$MEDIA_BACKUP_DIR/stickforstats_media_$TIMESTAMP.tar.gz"
    
    # Create media files backup
    log "Creating media archive..."
    cd "$PROJECT_ROOT"
    
    # Use tar to create a compressed archive of the media directory
    tar -czf "$MEDIA_BACKUP_FILE" -C "$PROJECT_ROOT/media" .
    
    # Check if backup was successful
    if [ $? -eq 0 ] && [ -f "$MEDIA_BACKUP_FILE" ]; then
        log "Media backup completed successfully: $MEDIA_BACKUP_FILE ($(du -h "$MEDIA_BACKUP_FILE" | cut -f1))"
    else
        log "ERROR: Media backup failed!"
        return 1
    fi
}

# Cleanup old backups function
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    # Find and delete database backups older than retention period
    find "$DB_BACKUP_DIR" -name "*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
    
    # Find and delete media backups older than retention period
    find "$MEDIA_BACKUP_DIR" -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete
    
    log "Cleanup completed."
}

# Upload to S3 function (if configured)
upload_to_s3() {
    # Check if AWS CLI is installed and S3 bucket is configured
    if command -v aws >/dev/null 2>&1 && [ -n "$S3_BUCKET" ]; then
        log "Uploading backups to S3 bucket: $S3_BUCKET"
        
        # Upload database backup
        aws s3 cp "$DB_BACKUP_FILE" "s3://$S3_BUCKET/database/$(basename "$DB_BACKUP_FILE")"
        
        # Upload media backup
        aws s3 cp "$MEDIA_BACKUP_FILE" "s3://$S3_BUCKET/media/$(basename "$MEDIA_BACKUP_FILE")"
        
        log "S3 upload completed."
    else
        log "S3 upload skipped. AWS CLI not installed or S3_BUCKET not configured."
    fi
}

# Main execution
main() {
    log "=== StickForStats Backup Process Started ==="
    
    # Perform database backup
    backup_database
    DB_BACKUP_STATUS=$?
    
    # Perform media backup
    backup_media_files
    MEDIA_BACKUP_STATUS=$?
    
    # Clean up old backups
    cleanup_old_backups
    
    # Upload to S3 if both backups were successful
    if [ $DB_BACKUP_STATUS -eq 0 ] && [ $MEDIA_BACKUP_STATUS -eq 0 ]; then
        upload_to_s3
    else
        log "WARNING: Skipping S3 upload due to backup failures."
    fi
    
    # Log completion
    log "=== StickForStats Backup Process Completed ==="
    
    # Return success if both backups succeeded
    if [ $DB_BACKUP_STATUS -eq 0 ] && [ $MEDIA_BACKUP_STATUS -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# Run the main function
main
exit $?