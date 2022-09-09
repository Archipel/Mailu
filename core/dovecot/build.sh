HASH=git-$(git rev-parse --short HEAD)-$(date +%s)
docker build -t weynwebworks/mailu-imap:$HASH -t weynwebworks/mailu-imap:latest .
if [ "$1" == "--push" ]; then
  docker push weynwebworks/mailu-imap:$HASH
  docker push weynwebworks/mailu-imap:latest
fi
