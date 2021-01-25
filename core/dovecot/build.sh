HASH=$(cat * */* | sha1sum | awk '{print $1}')
docker build -t weynwebworks/mailu-imap:$HASH .
if [ "$1" == "--push" ]; then
  docker push weynwebworks/mailu-imap:$HASH
fi
