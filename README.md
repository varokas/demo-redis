# Redis Demo

## Prerequisite
* Python 3
* pipenv
* docker

## Install
```
pipenv install

pipenv run alembic upgrade head
```

## Run
```
pipenv run uvicorn main:app --port 8001 --reload
```