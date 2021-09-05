HASH=$(tar cf - . | sha1sum | awk '{print $1}')
docker build -t weynwebworks/mailu-admin:$HASH -t weynwebworks/mailu-admin:latest .
if [ "$1" == "--push" ]; then
  docker push weynwebworks/mailu-admin:$HASH
  docker push weynwebworks/mailu-admin:latest
fi
