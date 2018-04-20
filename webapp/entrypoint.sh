#!/usr/bin/env sh
if test -d node_modules; then
  echo node_modules_exists 
else
  ln -s /tmp/app/node_modules /src/app/node_modules
fi 

if ! $(cmp -s /tmp/app/package.json /src/app/package.json); then
  cp /tmp/app/package.json /src/app/package.json
fi

if ! $(cmp -s /tmp/app/yarn.lock /src/app/yarn.lock); then
  cp /tmp/app/yarn.lock /src/app/yarn.lock
fi

exec $@
