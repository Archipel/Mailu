HASH=$(tar cf - . | sha1sum | awk '{print $1}')
docker build -t weynwebworks/mailu-postfix:$HASH -t weynwebworks/mailu-postfix:latest .
if [ "$1" == "--push" ]; then
  docker push weynwebworks/mailu-postfix:$HASH
  docker push weynwebworks/mailu-postfix:latest
fi
