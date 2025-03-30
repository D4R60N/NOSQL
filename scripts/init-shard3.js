#!/bin/bash

mongosh <<EOF
var config = {
    "_id": "rs-shard-3",
    "version": 1,
    "members": [
        {
            "_id": 0,
            "host": "shard3-0:27017",
			"priority": 1
        },
        {
            "_id": 1,
            "host": "shard3-1:27017",
			"priority": 0.5
        },
        {
            "_id": 2,
            "host": "shard3-2:27017",
			"priority": 0.5
        }
    ]
};
rs.initiate(config, { force: true });
EOF