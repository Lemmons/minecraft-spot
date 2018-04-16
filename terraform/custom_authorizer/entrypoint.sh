#!/usr/bin/env sh
if test -d node_modules; then
  echo node_modules_exists 
else
  ln -s /tmp/node_modules /src/node_modules
fi 

if ! $(cmp -s /tmp/package.json /src/package.json); then
  cp /tmp/package.json /src/package.json
fi

exec $@
