
.PHONY: build
build:
	docker-compose build

.PHONY: start
start:
	docker-compose up

.PHONY: clean
clean:
	rm -rf .pg_data

.PHONY: restart
restart:
	make build
	make start