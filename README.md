# Booking Manager Django Backend

> Booking Manager web application's backend repository

### Prerequisite

1. [Install Python 3.9.0](https://www.python.org/downloads/)
2. [Install Pipenv](https://pipenv.pypa.io/en/latest/install/#installing-pipenv)
3. [Install Django 4.0.6](https://docs.djangoproject.com/en/4.0/topics/install/)
4. [Install PyCharm (Preferred IDE)](https://www.jetbrains.com/pycharm/download/)

#### Getting Started

- Clone the repo from `https://github.com/adnan9867/booking_manager.git`
- Install Pipenv

```shell
python -m pip install --upgrade pip
pip install pipenv
```

### Database Setup

**1.**
Run this command:

```shell
sudo su postgres -c psql
```

**2.**
Run this command:

```sql
CREATE USER booking_user WITH ENCRYPTED PASSWORD 'booking_user';
```

**3**
Run these command:

```sql
CREATE DATABASE booking_db with owner booking_user;
```

### Run the Backend

```shell
cd django_backend
```

Proceed to **django-backend** folder, there you will find requirements.txt file

#### Run this command to install the required packages:

```shell
pipenv install
```

### create the environment configuration

Copy the variables mentioned below in a file e.g **config** in root folder (_You have to create this file first and also you can
assign any name you want_)

```shell
  #!/bin/bash

  export ALLOWED_HOSTS=localhost
  export DATABASE_URL=psql://booking_user:booking_user@127.0.0.1:5432/booking_db
  export TEST_DATABASE_NAME='booking_db_test'
  export DEBUG=True

  export PASSWORD_RESET_INTERVAL=300
  export PASSWORD_RESET_EXPIRY=600

  export SURMOUNT_LOG_LEVEL=INFO
  export DJANGO_LOG_LEVEL=INFO
  export DJANGO_LOG_FILE=django.log
```

### Run this command

```shell
source config
```

### Make the migration

```shell
pipenv run python manage.py makemigrations
```

Run the migration

```shell
pipenv run python manage.py migrate
```

### Populate the lookup data into the database

```shell
pipenv run python populate_initial_data.py
```

### Run the backend server

```shell
pipenv run python manage.py runserver
```

## Code formatting and alignment

Before commit and pushing the code, run the following script for auto formatting and alignment the code according to the standard.

Run on terminal:

```shell
./shellscripts/black.sh
./shellscripts/docformatter.sh
./shellscripts/unify.sh
```

## Run Test Cases

For Unit test cases run :

```shell
pipenv run python manage.py test
```

For running specific unit test case use tag name ie.

```shell
pipenv run python manage.py test --tag=<tag-name>
```

For running specific unit test by class name ie.

```shell
pipenv run python manage.py test tests.unittests.endpoints.test_user_views
```

For inspecting and keeping the test database add the "--keepdb"

#### but you will need to drop the test database manually for next test run

```bash
pipenv run python manage.py test --keepdb
```

## Run Server

```bash
pipenv run python manage.py runserver --settings=django_backend.settings.test
```


