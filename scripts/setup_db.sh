#!/usr/bin/env bash
# Setup local PostgreSQL database with pgvector extension.
# Requires: psql, createdb available on PATH.
set -euo pipefail

DB_NAME="${DB_NAME:-agentic_rag}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

echo "Creating database ${DB_NAME} if it does not exist..."
createdb -U "${DB_USER}" -h "${DB_HOST}" -p "${DB_PORT}" "${DB_NAME}" 2>/dev/null || true

echo "Enabling pgvector extension..."
psql -U "${DB_USER}" -h "${DB_HOST}" -p "${DB_PORT}" -d "${DB_NAME}" \
  -c "CREATE EXTENSION IF NOT EXISTS vector;" \
  -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"

echo "Database setup complete."
