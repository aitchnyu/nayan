FROM ubuntu:20.04 as base
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
RUN mkdir /code
WORKDIR /code
# This was asking dialog for tzdata
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv libpq-dev python3-dev && \
    apt-get install -y binutils libproj-dev gdal-bin

FROM base as dev
RUN pip install playwright==1.18.2 && \
  playwright install && \
  playwright install-deps
EXPOSE 8000

FROM ubuntu:20.04 as jsbase
RUN apt-get update && \
    apt-get install -y curl && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs

FROM jsbase as jsdev
RUN mkdir /code
WORKDIR /code/vueapp
ENV WEBPACK_DIST=../backend/app/static/app/webpack-dist

FROM jsbase as jsprod
ENV WEBPACK_DIST ./webpack-dist
COPY vueapp/ ./
RUN npm install && ./node_modules/.bin/vue-cli-service build

FROM base as prod
COPY backend/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt && \
    pip3 install gunicorn==20.1.0
COPY backend/ ./
COPY --from=jsprod webpack-dist app/static/app/webpack-dist
# This is to allow manage.py commands
ENV POSTGRES_DB=fake POSTGRES_USER=fake POSTGRES_PASSWORD=fake POSTGRES_HOST=fake
RUN python3 manage.py collectstatic --noinput
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app