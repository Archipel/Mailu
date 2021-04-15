#!/bin/bash
export TAG=$((cat Dockerfile; cat start.py; cat conf/*) | sha1sum | awk '{print $1}')
echo "TAG = $TAG"
docker build -t weynwebworks/mailu-rspamd:$TAG -t weynwebworks/mailu-rspamd:latest .
docker push weynwebworks/mailu-rspamd:$TAG
docker push weynwebworks/mailu-rspamd:latest

