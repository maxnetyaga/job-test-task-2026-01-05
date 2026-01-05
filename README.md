# Description
This app allows organize events and invite other users to them.

# Setup
Run uv sync to initialize venv and install python packages (or use any other tool that can process pyproject.toml).

Also you need to initialize db:
```sh
./manage.py migrate
```

# Usage
Start dev server with ```make dev``` or ```./manage.py runserver```

Also you can run production version (uses nginx for static files serving & proxies other requests to uvicorn that runs django app) with docker-compose:
```sh
docker compose run -d --build

or

docker-compose run -d --build (old version of docker-compose)
```
