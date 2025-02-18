#!/bin/bash

container_name=test_task_db
database_name=test_database

# before tests:
docker exec -it $container_name \
        psql -U postgres \
        -c "CREATE DATABASE $database_name;"

pytest .

#after tests:
docker exec -it $container_name \
        psql -U postgres \
        -c "DROP DATABASE $database_name;"
