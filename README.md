# Redis Demo

## Prerequisite
* Python 3
* pipenv
* docker

## Install
```
python3 -m pip install pipenv

pipenv install --dev

pipenv run alembic upgrade head
```

## Run
```
pipenv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```