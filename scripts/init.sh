#!/bin/bash
rm -rf ./data/*
rm ./mongodb-build/auth/mongodb-keyfile
openssl rand -base64 756 > ./mongodb-build/auth/mongodb-keyfile
chmod 600 ./mongodb-build/auth/mongodb-keyfile
chown 999:999 ./mongodb-build/auth/mongodb-keyfile

docker-compose up -d
echo "Running startup script..."

sleep 10
docker-compose exec configsvr1 bash "/scripts/init-configserver.js"
sleep 10

docker-compose exec shard1-0 bash "/scripts/init-shard1.js"
docker-compose exec shard2-0 bash "/scripts/init-shard2.js"
docker-compose exec shard3-0 bash "/scripts/init-shard3.js"
sleep 10

docker-compose exec router1 sh -c "mongosh < /scripts/init-router.js"
sleep 10

docker-compose exec configsvr1 bash "/scripts/auth.js"
docker-compose exec shard1-0 bash "/scripts/auth.js"
docker-compose exec shard2-0 bash "/scripts/auth.js"
docker-compose exec shard3-0 bash "/scripts/auth.js"

docker exec -it router-1 bash -c "echo 'sh.status()' | mongosh --port 27017 -u 'user' -p 'user' --authenticationDatabase admin"
docker-compose exec router1 mongosh --port 27017 -u "user" -p "user" --authenticationDatabase admin --eval "
  db = db.getSiblingDB('Transparency');
  db.createCollection('Prices', {
    validator: {
      \$jsonSchema: {
        bsonType: 'object',
        required: ['MTU (CET/CEST)', 'Area', 'Day-ahead Price (EUR/MWh)'],
        properties: {
          'MTU (CET/CEST)': { bsonType: 'string' },
          'Area': { bsonType: 'string' },
          'Day-ahead Price (EUR/MWh)': { bsonType: ['double', 'string', 'int'] }
        }
      }
    }
  });

  db.createCollection('Load', {
    validator: {
      \$jsonSchema: {
        bsonType: 'object',
        required: ['MTU (CET/CEST)', 'Area', 'Actual Total Load (MW)'],
        properties: {
          'MTU (CET/CEST)': { bsonType: 'string' },
          'Area': { bsonType: 'string' },
          'Actual Total Load (MW)': { bsonType: ['double', 'string', 'int'] },
          'Day-ahead Total Load Forecast (MW)': { bsonType: ['double', 'string', 'int'] }
        }
      }
    }
  });

  db.createCollection('Production', {
    validator: {
      \$jsonSchema: {
        bsonType: 'object',
        required: ['MTU (CET/CEST)', 'Area', 'Production Type', 'Generation (MW)'],
        properties: {
          'MTU (CET/CEST)': { bsonType: 'string' },
          'Area': { bsonType: 'string' },
          'Production Type': { bsonType: 'string' },
          'Generation (MW)': { bsonType: ['double', 'string', 'int'] }
        }
      }
    }
  });

  sh.enableSharding('Transparency');

  db.adminCommand({ shardCollection: 'Transparency.Load', key: { 'Area': 1, 'MTU (CET/CEST)': 1 } });
  db.adminCommand({ shardCollection: 'Transparency.Prices', key: { 'Area': 1, 'MTU (CET/CEST)': 1 } });
  db.adminCommand({ shardCollection: 'Transparency.Production', key: { 'Area': 1, 'MTU (CET/CEST)': 1, 'Production Type': 1 } });
"
echo "Finished."