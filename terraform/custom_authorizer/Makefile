REPO=custom_auth
TAG?=latest

build:
	docker build . -t ${REPO}:${TAG}

test: build
	docker run --rm -v $(shell pwd):/src/ ${REPO}:${TAG} npm test

bundle: build
	docker run --rm -v $(shell pwd):/src/ ${REPO}:${TAG} npm run bundle
