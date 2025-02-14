#!/usr/bin/env bash
docker-compose run --rm --build app "${@:1}"
