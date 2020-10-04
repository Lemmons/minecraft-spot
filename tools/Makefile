TAG?=dev

build:
	docker build . -t tlemmon/spot-tools:$(TAG)

push: build
	docker push tlemmon/spot-tools:$(TAG)

push-latest: push
	docker tag tlemmon/spot-tools:$(TAG) tlemmon/spot-tools:latest
	docker push tlemmon/spot-tools:latest
