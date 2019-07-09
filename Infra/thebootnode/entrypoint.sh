#!/usr/bin/env bash
set -eo pipefail

cd /home/geth_user/eth-net-intelligence-api
perl -pi -e "s/XXX/$(hostname)/g" app.json

/usr/bin/pm2 start ./app.json
sleep 3

IP=$(hostname -i)
cd /home/geth_user/
echo "Running: bootnode --nodekey boot.key --nat extip:${IP}"
bootnode --nodekey boot.key --nat extip:${IP}
