.PHONY: openapi
openapi:
	./manage.py spectacular --color --file openapi.yml

.PHONY: dev
dev:
	./manage.py runserver
