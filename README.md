# Issues Tracking Project

## Setting up development environment

You must have docker-compose installed.

To setup project:

`./run init`

And 

`./run django-manage creategeo`

Run this on one terminal:

`./run django-manage-runserver`

And on another terminal:

`./run vue-watch`

## Deploying to Google Cloud Run

Create a Project on GCP. We get an id like `project-311206`

Login to Cloud Shell.

`gcloud cloud-shell ssh --authorize-session`

To use Google's container registry

`gcloud auth configure-docker`

Clone the repo to nayan directory.

`git clone https://github.com/aitchnyu/nayan.git`

Then `cd nayan` to enter the directory

Create a postgres DB.

`./create_gc_infra db <instance name> <region> <root password>`

`./deploygc build`

`./deploygc manage migrate`

todo move this down

`./deploygc manage creategeo`


```
export SITE=[site name]
# Infra details
export PROJECT_ID=[project id generated]
export REGION=[region, asia-south1 for Mumbai]
export SERVICE_NAME=markerae
# Resources
export POSTGRES_DB=[db name]
export POSTGRES_USER=postgres
export  POSTGRES_PASSWORD=[password]
export  POSTGRES_INSTANCE=[instance name]
```

```
cd markerae
./create_gc_infra.sh db [instance name] [region] [root password]
./deploy_on_gc.sh manage build
./deploy_on_gc.sh manage showmigrations
./deploy_on_gc.sh manage migrate
./deploy_on_gc.sh manage createsuperuser
./deploy_on_gc.sh deploy
```

## Technologies used
- Django, GeoDjango
- Postgres, Postgis
- Mapbox
- Ubuntu
- Google Cloud Run, Cloud SQL
- Docker, Docker Compose
- Selenium
- Vue, Webcomponents
- Bulma CSS