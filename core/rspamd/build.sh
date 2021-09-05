HASH=$(tar cf - . | sha1sum | awk '{print $1}')
docker build -t weynwebworks/mailu-rspamd:$HASH -t weynwebworks/mailu-rspamd:latest .
if [ "$1" == "--push" ]; then
  docker push weynwebworks/mailu-rspamd:$HASH
  docker push weynwebworks/mailu-rspamd:latest
fi
