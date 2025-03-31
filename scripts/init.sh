#!/bin/bash
docker-compose up -d
echo "Running startup script..."

docker-compose exec configsvr1 bash "/scripts/init-configserver.js"
sleep 10

docker-compose exec shard1-0 bash "/scripts/init-shard1.js"
docker-compose exec shard2-0 bash "/scripts/init-shard2.js"
docker-compose exec shard3-0 bash "/scripts/init-shard3.js"
sleep 10

docker-compose exec router1 sh -c "mongosh < /scripts/init-router.js"
sleep 10  # Add a delay if necessary

docker-compose exec configsvr1 bash "/scripts/auth.js"
docker-compose exec shard1-0 bash "/scripts/auth.js"
docker-compose exec shard2-0 bash "/scripts/auth.js"
docker-compose exec shard3-0 bash "/scripts/auth.js"

docker exec -it router-1 bash -c "echo 'sh.status()' | mongosh --port 27017 -u 'user' -p 'user' --authenticationDatabase admin"
docker-compose exec router1 mongosh --port 27017 -u "user" -p "user" --authenticationDatabase admin