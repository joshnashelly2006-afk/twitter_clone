#!/usr/bin/env bash
# PostgreSQL Automated Database Backup Script

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/twitter_clone_backup_${TIMESTAMP}.sql"

# Read environment variables if available
DB_USER="${POSTGRES_USER:-postgres}"
DB_NAME="${POSTGRES_DB:-twitter_clone_db}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

mkdir -p "${BACKUP_DIR}"

echo "Starting PostgreSQL database backup for ${DB_NAME}..."
PGPASSWORD="${POSTGRES_PASSWORD:-postgres}" pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -F c -b -v -f "${BACKUP_FILE}" "${DB_NAME}"

echo "Database backup completed successfully: ${BACKUP_FILE}"
