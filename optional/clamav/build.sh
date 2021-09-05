HASH=$(tar cf - . | sha1sum | awk '{print $1}')
docker build -t weynwebworks/mailu-clamav:$HASH -t weynwebworks/mailu-clamav:latest .
if [ "$1" == "--push" ]; then
  docker push weynwebworks/mailu-clamav:$HASH
  docker push weynwebworks/mailu-clamav:latest
fi
