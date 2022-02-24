# Issues Tracking Project

## Setting up development environment

You must have docker-compose installed.

To setup project:
```
$ ./run init

$ `./run django-manage creategeo`

# Run this on one terminal:

$ ./run django-manage-runserver

# And on another terminal:

$ ./run vue-watch

```

To do unit testing and linting for Django and Vue:

`$ ./run checkall`

This is used in CI too.

## Deploying to Google Cloud Run

Create a Project on GCP. We get an id like `project-311206`

Login to Cloud Shell.

`gcloud cloud-shell ssh --authorize-session`

To use Google's container registry

`gcloud auth configure-docker`

In a cloud shell, clone the repo to nayan directory.

`git clone https://github.com/aitchnyu/nayan.git`

Then `cd nayan` to enter the directory

Export these:

```shell
$ export SITE=[site name]
# Infra details
$ export PROJECT_ID=[project id generated]
$ export REGION=[region, asia-south1 for Mumbai]
$ export SERVICE_NAME=markerae
# Resources
$ export POSTGRES_DB=[db name]
$ export POSTGRES_USER=postgres
$ export  POSTGRES_PASSWORD=[password]
$ export  POSTGRES_INSTANCE=[instance name]
```


```shell
# Create a postgres DB.

$ ./create_gc_infra db <instance name> <region> <root password>

$ ./deploygc build

$ ./deploygc manage migrate

# Create post offices 
$ ./deploygc manage creategeo
# Create tags
$ ./deploygc manage createtags

# Deploy to Cloud Run
$ ./deploygc deploy
```

## Technologies used
- Django, GeoDjango with Postgres, Postgis
- Vue.js
- Leaflet with Mapbox
- Cloudflare
- Google Cloud Run, Cloud SQL, Ubuntu
- Docker, Docker Compose
- Playwright
- Bulma CSS