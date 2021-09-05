HASH=$(tar cf - . | sha1sum | awk '{print $1}')
docker build -t weynwebworks/mailu-roundcube:$HASH -t weynwebworks/mailu-roundcube:latest .
if [ "$1" == "--push" ]; then
  docker push weynwebworks/mailu-roundcube:$HASH
  docker push weynwebworks/mailu-roundcube:latest
fi
