HASH=$(tar cf - . | sha1sum | awk '{print $1}')
docker build -t weynwebworks/mailu-imap:$HASH -t weynwebworks/mailu-imap:latest .
if [ "$1" == "--push" ]; then
  docker push weynwebworks/mailu-imap:$HASH
  docker push weynwebworks/mailu-imap:latest
fi
