#!/bin/bash

if [[ -z $(which docker-compose) ]]
then
  echo "You don't have docker-compose installed. Exiting"
  exit 1
fi

suggest () {
  read -ei "$*"
  history -s "$REPLY"
  fc -s
}

docker-compose up -d

if [[ $1 == 'init' ]]
then
     docker-compose exec webdev python3 -m venv /code/venv
     docker-compose exec webdev /code/venv/bin/pip3 install -r /code/backend/requirements.txt
     docker-compose exec webdev /code/venv/bin/python3 /code/backend/manage.py migrate
     docker-compose exec jsdev npm install
elif [[ $1 == 'clean' ]]
then
  # Since docker is run as root, its generated files are root owned
  docker-compose exec webdev rm -rf /code/venv && \
    rm -rf /code/pgdata && \
    rm -rf /code/vueapp/node_modules && \
    rm -rf /code/backend/static && \
    rm /code/backend/app/static/app/webpack-dist
elif [[ $1 == 'django-manage' ]]
then
  shift
  echo running docker-compose exec webdev /code/venv/bin/python3 /code/backend/manage.py ...
  docker-compose exec webdev /code/venv/bin/python3 /code/backend/manage.py "$@"
elif [[ $1 == 'django-manage-runserver' ]]
then
  echo running docker-compose exec webdev /code/venv/bin/python3 /code/backend/manage.py runserver 0.0.0.0:8000
  docker-compose exec webdev /code/venv/bin/python3 /code/backend/manage.py runserver 0.0.0.0:8000
elif [[ $1 == 'vue-watch' ]]
then
  echo running docker-compose exec jsdev ./node_modules/.bin/vue-cli-service build --watch --target wc-async --inline-vue --name webcomponents 'src/*.vue'
  docker-compose exec jsdev ./node_modules/.bin/vue-cli-service build --watch --target wc-async --inline-vue --name webcomponents 'src/*.vue'
else
  # todo document this
  echo nothing
fi