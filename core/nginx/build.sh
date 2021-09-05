HASH=$(tar cf - . | sha1sum | awk '{print $1}')
docker build -t weynwebworks/mailu-nginx:$HASH -t weynwebworks/mailu-nginx:latest .
if [ "$1" == "--push" ]; then
  docker push weynwebworks/mailu-nginx:$HASH
  docker push weynwebworks/mailu-nginx:latest
fi
