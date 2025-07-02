#!/usr/bin/env bash

set -e # exit if command fails

echo "Installing PostgreSQL..."
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib

echo "Enabling and starting PostgreSQL service..."
sudo systemctl enable postgresql
sudo systemctl start postgresql

echo "Creating PostgreSQL user 'django' and database 'rackflowdb'..."


# pgql 
sudo -u postgres psql <<EOF
-- Create user
DO \$\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = 'django'
   ) THEN
      CREATE ROLE django LOGIN PASSWORD 'changeme';
   END IF;
END
\$\$;

-- Create database if it doesn't exist
CREATE DATABASE rackflowdb OWNER django;
EOF

echo "PostgreSQL setup complete."
