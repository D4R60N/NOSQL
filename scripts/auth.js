#!/bin/bash
mongosh <<EOF
use admin;
db.createUser({user: "user", pwd: "user", roles:[{role: "root", db: "admin"}]});
exit;
EOF