#!/usr/bin/env bash

set -e

cleanup() {
    echo "Shutting down services..."

    if [ -n "$UVICORN_PID" ]; then
        kill "$UVICORN_PID" 2>/dev/null
        wait "$UVICORN_PID" 2>/dev/null
    fi
    if [ -n "$NGINX_PID" ]; then
        kill "$NGINX_PID" 2>/dev/null
        wait "$NGINX_PID" 2>/dev/null
    fi

    echo "Exiting in 2 minutes..."
    sleep 120
    exit 0
}
trap cleanup TERM INT

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || true

echo "Starting uvicorn..."
python -m uvicorn test_task_project.asgi:application --port 8400 &
UVICORN_PID=$!

echo "Starting nginx..."
nginx -g "daemon off;" &
NGINX_PID=$!

tail --pid=$UVICORN_PID -f /dev/null &
tail --pid=$NGINX_PID -f /dev/null &

while true; do
    if ! kill -0 "$UVICORN_PID" 2>/dev/null; then
        echo "uvicorn exited unexpectedly"
        cleanup
    fi

    if ! kill -0 "$NGINX_PID" 2>/dev/null; then
        echo "nginx exited unexpectedly"
        cleanup
    fi

    sleep 1
done
