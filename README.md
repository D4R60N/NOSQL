# NOSQL

docker stop $(docker ps -a -q)

docker-compose down -v --rmi all --remove-orphans

docker exec -it router-1 bash -c "echo 'sh.status()' | mongosh --port 27017 -u 'user' -p 'user' --authenticationDatabase admin"

docker-compose up -d


sh.enableSharding("MyDatabase")

db.adminCommand( { shardCollection: "MyDatabase.MyCollection", key: { oemNumber: "hashed", zipCode: 1, supplierId: 1 } } )

