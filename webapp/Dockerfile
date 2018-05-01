FROM node:9-alpine

RUN apk add --no-cache yarn

WORKDIR /tmp/app

COPY package.json .
COPY yarn.lock .

RUN yarn install

WORKDIR /src/app

COPY entrypoint.sh .
ENTRYPOINT ["/src/app/entrypoint.sh"]
CMD ["yarn run start"]
