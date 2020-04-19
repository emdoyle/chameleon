# The Chameleon

To run the app:
```
> make
> docker-compose up
```

The frontend is built with `make` or `make build`.

A docker image is built and pushed with `make image`.

Services (`postgres`, `redis`, and `web`) come up with `docker-compose up`,
and if `web` needs to be rebuilt, run `docker-compose build`.

The frontend can be 'hot reloaded' by simply rebuilding (with `make`/`make build`),
since the `assets/build` folder is mounted into the docker image.

Data is persistent until `docker-compose down`.