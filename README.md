# Web Application Exercise

## Team members
Sagynbek - https://github.com/sagynbek001 \
Harvey - https://github.com/junyid \
Manny - https://github.com/MannySotoRuiz \
Amaan - https://github.com/Amaanmkhwaja

## Product vision statement

An app designed for families to make grocery shopping easy allowing a shopping list to be shared and organized.

## User stories

[[Link](https://github.com/software-students-fall2022/web-app-exercise-team-16-1/issues)]

## Task boards

[[Link](https://github.com/software-students-fall2022/web-app-exercise-team-16-1/projects)]

## How to run (instructions)

### Build and launch the database

- install and run [docker desktop](https://www.docker.com/get-started)
- create a [dockerhub](https://hub.docker.com/signup) account
- run command, `docker run --name mongodb_dockerhub -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=secret -d mongo:latest`

### Create a `.env` file with following content

```
MONGO_DBNAME=example_db
MONGO_URI="mongodb://admin:secret@localhost:27017/example?authSource=admin&retryWrites=true&w=majority"
FLASK_APP=app.py
```

### Set up a Python virtual environment and activate it

### Install dependencies into the virtual environment

```bash
pip3 install -r requirements.txt
```

### Run the app

`flask run`
