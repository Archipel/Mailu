HASH=$(cat * */* | sha1sum | awk '{print $1}')
docker build -t weynwebworks/mailu-postfix:$HASH .
if [ "$1" == "--push" ]; then
  docker push weynwebworks/mailu-postfix:$HASH
fi
