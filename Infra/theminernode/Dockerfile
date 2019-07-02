FROM python:alpine3.10
LABEL maintainer="new.hossam0@gmail.com"
EXPOSE 8545
EXPOSE 30303
EXPOSE 30303/udp


RUN \
  apk add --update bash git go make gcc musl-dev linux-headers curl jq nodejs perl busybox-extras python3-dev build-base

RUN \
  git clone --branch v1.8.27 https://github.com/ethereum/go-ethereum
RUN \
  (cd go-ethereum && make geth)                                              && \
  cp go-ethereum/build/bin/geth /usr/local/bin/                              && \
  (cd go-ethereum && build/env.sh go run build/ci.go install ./cmd/bootnode) && \
  cp go-ethereum/build/bin/bootnode /usr/local/bin/


RUN \
  cd /root && git clone https://github.com/cubedro/eth-net-intelligence-api  && \
  apk add --update npm &&\
  cd eth-net-intelligence-api &&\
  npm install &&\
  npm install -g pm2

RUN \
  apk del git go make gcc musl-dev linux-headers                             && \
  rm -rf /go-ethereum && rm -rf /var/cache/apk/*

ADD app.json /root/eth-net-intelligence-api/app.json

COPY entrypoint.sh /entrypoint.sh


ENV ETH_DIR /root/.ethereum

COPY mine_when_needed.js /mine_when_needed.js
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
