#! /bin/bash
isort netflix_show_api
black netflix_show_api -t py37 -l 99
autopep8 --recursive --in-place --list-fixes --max-line-length 99 --aggressive netflix_show_api