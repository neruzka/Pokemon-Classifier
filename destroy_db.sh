#!/bin/bash
PGPASSWORD=super_secret psql -h 127.0.1 -p 5433 -U postgres -d tt-db -f db_scripts/delete_table.sql
