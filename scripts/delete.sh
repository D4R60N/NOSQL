#!/bin/bash
docker-compose down -v --rmi all --remove-orphans
sudo rm -rf ./data/*