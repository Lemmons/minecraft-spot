FROM node:9-alpine

RUN apk add --no-cache zip

WORKDIR /src/
COPY package.json .

RUN npm install

RUN cp -r /src/node_modules /tmp/node_modules \
    && cp /src/package.json /tmp/package.json

ENTRYPOINT ["npm"]

COPY entrypoint.sh /bin/entrypoint.sh
ENTRYPOINT ["/bin/entrypoint.sh"]
