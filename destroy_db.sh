#!/bin/bash
psql -h 127.0.1 -p 5433 -U postgres -W super_secret -d tt-db -f db_scripts/delete_table.sql
