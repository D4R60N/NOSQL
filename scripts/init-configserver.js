#!/bin/bash

mongosh <<EOF
var config = {
	"_id": "rs-config-server",
	"configsvr": true,
	"version": 1,
	"members": [
		{
			"_id": 0,
			"host": "configsvr1:27017",
			"priority": 1
		},
		{
			"_id": 1,
			"host": "configsvr2:27017",
			"priority": 0.5
		},
		{
			"_id": 2,
			"host": "configsvr3:27017",
			"priority": 0.5
		}
	]
};
rs.initiate(config, { force: true });
EOF