TAG?=dev
REPO=app

build-docker:
	docker build . -t ${REPO}:${TAG}

run: build-docker
	docker run --rm -it -p 80:80 -v $(shell pwd):/src/app ${REPO}:${TAG}

build-content: build-docker
	docker run --rm -v $(shell pwd):/src/app ${REPO}:${TAG} yarn run build

test:
	docker run --rm ${REPO}:${TAG} yarn run test

clean:
	rm -r dist

serve: build-content
	docker run --rm -p 80:80 -v $(shell pwd)/dist:/usr/share/nginx/html:ro nginx:alpine

shell: build-docker
	docker run --rm -it -p 80:80 -v $(shell pwd):/src/app ${REPO}:${TAG} sh

deploy:
	aws s3 sync dist/ s3://${BUCKET}
	aws cloudfront create-invalidation --distribution-id ${DIST-ID} --paths /index.html
