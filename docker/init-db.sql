-- PostgreSQL initialization script
-- Runs once when the container is first created

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create test database (used by integration tests)
CREATE DATABASE agentic_rag_test;

\connect agentic_rag_test
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
