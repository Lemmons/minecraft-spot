VERSION?=dev

build:
	docker build . -t tlemmon/minecraft-spot-tools:$(VERSION)

push:
	docker tag tlemmon/minecraft-spot-tools:$(VERSION) tlemmon/minecraft-spot-tools:latest
	docker push tlemmon/minecraft-spot-tools:$(VERSION)
	docker push tlemmon/minecraft-spot-tools:latest
