# Nayan

## Setting up development environment

You must have docker-compose installed.

To setup project:

`./run_dev.sh init`

Run this on one terminal:

`./run_dev.sh django-manage-runserver`

And on another terminal:

`./run_dev.sh vue-watch`

## Deploying to Google Cloud Run

Create a Project on GCP. We get an id like `project-311206`

Login to Cloud Shell.
```
gcloud cloud-shell ssh --authorize-session
```

One time
```
git clone https://github.com/aitchnyu/markerae.git
```

To use Google's container registry
```gcloud auth configure-docker```

Create DB and Bucket. Investigate scripts to find system requirements.
```
cd markerae
./create_gc_infra.sh db [instance name] [region] [root password]
```

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
