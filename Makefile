.PHONY: build tag push image deploy logs
PROJ_NAME = chameleon
SRC_JS = $(wildcard assets/src/*)
PUBLIC_FILES = $(wildcard assets/public/*)
BUILT = assets/build/.made

all: $(BUILT)

$(BUILT): $(SRC_JS) $(PUBLIC_FILES)
	cd assets/ && yarn build
	touch $(BUILT)

build: $(BUILT)
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
