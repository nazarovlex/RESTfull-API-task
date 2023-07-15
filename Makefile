
.PHONY: build
build:
	docker-compose build

.PHONY: start
start:
	docker-compose up

.PHONY: clean
clean:
	rm -rf .pg_data
	docker system prune


.PHONY: restart
restart:
	make build
	make start