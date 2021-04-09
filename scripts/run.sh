#! /bin/bash
docker run --name netflix_api --rm  --env-file .env.docker -p 8080:80 netflix_api