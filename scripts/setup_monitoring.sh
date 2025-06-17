#!/bin/bash
# Setup monitoring for StickForStats RAG system

set -e

# Define base directory
BASE_DIR=$(pwd)
MONITORING_DIR="$BASE_DIR/monitoring"
LOGS_DIR="$BASE_DIR/logs"

# Create required directories
echo "Creating monitoring directories..."
mkdir -p $LOGS_DIR
mkdir -p $MONITORING_DIR/{prometheus,grafana/{provisioning/{datasources,dashboards},dashboards},loki,promtail,alertmanager}

# Create prometheus multi-process directory for Django metrics
mkdir -p $BASE_DIR/prometheus_multiproc_dir
chmod 777 $BASE_DIR/prometheus_multiproc_dir

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

# Check if monitoring configuration files exist
if [ ! -f "$MONITORING_DIR/prometheus/prometheus.yml" ]; then
    echo "Prometheus configuration not found. Make sure to create it at $MONITORING_DIR/prometheus/prometheus.yml"
    exit 1
fi

if [ ! -f "$MONITORING_DIR/grafana/provisioning/datasources/datasources.yml" ]; then
    echo "Grafana datasource configuration not found. Make sure to create it."
    exit 1
fi

# Setup environment variables for alerting
echo "Setting up environment variables..."
if [ ! -f "$BASE_DIR/.env" ]; then
    echo "Creating .env file..."
    touch $BASE_DIR/.env
fi

# Add monitoring-specific variables to .env
if ! grep -q "RAG_SLACK_WEBHOOK" $BASE_DIR/.env; then
    echo "Adding RAG_SLACK_WEBHOOK to .env..."
    echo "# RAG monitoring settings" >> $BASE_DIR/.env
    echo "RAG_SLACK_WEBHOOK=YOUR_SLACK_WEBHOOK_URL" >> $BASE_DIR/.env
    echo "RAG_ALERT_EMAILS=alerts@example.com" >> $BASE_DIR/.env
    echo "PROMETHEUS_MULTIPROC_DIR=$BASE_DIR/prometheus_multiproc_dir" >> $BASE_DIR/.env
fi

# Prepare log files with proper permissions
echo "Setting up log files..."
touch $LOGS_DIR/rag_system.log
touch $LOGS_DIR/rag_performance.log
touch $LOGS_DIR/rag_security.log
touch $LOGS_DIR/rag_error.log
touch $LOGS_DIR/rag_alerts.log
chmod 664 $LOGS_DIR/*.log

# Start monitoring stack 
echo "Starting monitoring stack..."
docker-compose -f docker-compose.monitoring.yml up -d

# Verify services are running
echo "Verifying monitoring services..."
sleep 5
if ! docker ps | grep -q "stickforstats-prometheus"; then
    echo "WARNING: Prometheus container not running"
fi

if ! docker ps | grep -q "stickforstats-grafana"; then
    echo "WARNING: Grafana container not running"
fi

if ! docker ps | grep -q "stickforstats-loki"; then
    echo "WARNING: Loki container not running"
fi

# Print success message and next steps
echo "Monitoring setup complete!"
echo ""
echo "Next steps:"
echo "1. Access Grafana at http://localhost:3001"
echo "   - Default username: admin"
echo "   - Default password: stickforstats"
echo "2. Update the Slack webhook URL in .env file"
echo "3. Configure email settings for alerts"
echo "4. Review the monitoring documentation at stickforstats/rag_system/documentation/MONITORING_LOGGING_GUIDE.md"
echo ""
echo "To stop the monitoring stack: docker-compose -f docker-compose.monitoring.yml down"
echo "To view logs: docker-compose -f docker-compose.monitoring.yml logs -f"