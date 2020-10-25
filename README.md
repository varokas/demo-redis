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
pipenv run python3 main.py --redis
pipenv run python3 main.py

pipenv run locust -H http://localhost:8080 -u 100 -r 10
pipenv run locust -H http://demo-redis.varokas.com:8080 -u 100 -r 10
```