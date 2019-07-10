FROM python:alpine3.10
LABEL maintainer="new.hossam0@gmail.com"
EXPOSE 8545
EXPOSE 30303
EXPOSE 30303/udp


RUN \
  apk add --update bash git go make gcc musl-dev linux-headers curl jq nodejs perl busybox-extras python3-dev build-base && \
  apk add --update npm

RUN \
  git clone --branch v1.8.27 https://github.com/ethereum/go-ethereum
RUN \
  (cd go-ethereum && make geth)                                              && \
  cp go-ethereum/build/bin/geth /usr/local/bin/                              && \
  (cd go-ethereum && build/env.sh go run build/ci.go install ./cmd/bootnode) && \
  cp go-ethereum/build/bin/bootnode /usr/local/bin/


RUN \
  apk del go make gcc musl-dev linux-headers                             && \
  rm -rf /go-ethereum && rm -rf /var/cache/apk/*

RUN addgroup -g 1000 -S geth_user && \
      adduser -u 1000 -S geth_user -G geth_user

COPY entrypoint.sh /home/geth_user/entrypoint.sh
RUN chown geth_user:geth_user /home/geth_user/entrypoint.sh
RUN chmod +x /home/geth_user/entrypoint.sh

RUN \
  cd /home/geth_user && git clone https://github.com/cubedro/eth-net-intelligence-api  && \
  cd eth-net-intelligence-api &&\
  npm install &&\
  npm install -g pm2


USER geth_user

ADD app.json /home/geth_user/eth-net-intelligence-api/app.json




ENV ETH_DIR /home/geth_user/.ethereum

COPY mine_when_needed.js /home/geth_user/mine_when_needed.js

ENTRYPOINT ["/home/geth_user/entrypoint.sh"]
