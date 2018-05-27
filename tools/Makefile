TAG?=dev

build:
	docker build . -t tlemmon/minecraft-spot-tools:$(TAG)

push: build
	docker push tlemmon/minecraft-spot-tools:$(TAG)

push-latest: push
	docker tag tlemmon/minecraft-spot-tools:$(TAG) tlemmon/minecraft-spot-tools:latest
	docker push tlemmon/minecraft-spot-tools:latest
