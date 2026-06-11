HASH=git-$(git rev-parse --short HEAD)-$(date +%s)
docker build -t weynwebworks/mailu-postfix:$HASH -t weynwebworks/mailu-postfix:latest .
echo "Built weynwebworks/mailu-postfix:$HASH"
if [ "$1" == "--push" ]; then
  docker push weynwebworks/mailu-postfix:$HASH
  docker push weynwebworks/mailu-postfix:latest
fi
