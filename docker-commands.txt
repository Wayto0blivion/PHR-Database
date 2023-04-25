To start docker-compose containers:
docker-compose up -d --build

-d runs the containers in the background so that you can continue to use the terminal.
--build updates the containers with whatever changes you have made since the last build.


To stop docker containers:
docker-compose down -v

-v removes any non-persistent containers to free up disk space.

