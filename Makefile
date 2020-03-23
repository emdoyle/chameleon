.PHONY: dist build tag push image deploy logs
PROJ_NAME = chameleon
SRC_JS = $(wildcard assets/src/*)
PUBLIC_FILES = $(wildcard assets/public/*)

all: dist

dist:
	cd assets/ && yarn build

build:
	docker build . -t $(PROJ_NAME):latest

tag:
	docker tag $(PROJ_NAME):latest emdoyle/$(PROJ_NAME):latest

push:
	docker push emdoyle/$(PROJ_NAME):latest

image:
	make build
	make tag
	make push

deploy:
	kubectl delete pod -lapp=$(PROJ_NAME)

logs:
	kubectl logs -f -lapp=$(PROJ_NAME)
