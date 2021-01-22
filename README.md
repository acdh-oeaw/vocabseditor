# Vocabseditor

![Build Status](https://travis-ci.com/acdh-oeaw/vocabseditor.svg?branch=master&status=passed)

## About

The purpose of the Vocabseditor is to provide a service for collaborative work on controlled vocabularies development.

The editor follows **SKOS data model** for the main elements of a vocabulary. The **Dublin core** schema is used to capture the metadata (such as date created, date modified, creator, contributor, source and other) about each element. Each concept scheme can be downloaded in **RDF/XML** and *Turtle* format as well as each individual concept.

**The user management** system allows a user to share a concept scheme she/he created with other users (called 'curators') to create new, edit and delete concepts and collections within this concept scheme. Each user can find a summary of their latest activity on user's page.


## Technical setup

The application is implemented using Python and [Django](https://www.djangoproject.com/). It uses modules developed within [DjangoBaseProject](https://github.com/acdh-oeaw/djangobaseproject). It also provides REST API implemented with [Django Rest Framework](https://www.django-rest-framework.org/). 

## Install

1. Clone the repo

2. Create and activate virtual environment, run `pip install -r requirements.txt`

3. Run

    `python manage.py makemigrations --settings=vocabseditor.settings.dev`

    `python manage.py migrate --settings=vocabseditor.settings.dev`

    `python manage.py runserver --settings=vocabseditor.settings.dev`
    
4. After the above commands are executed the sqlite database is created automatically in the project's root folder 

5. Development server runs at `localhost:8000`

6. Create admin user

    `python manage.py createsuperuser --settings=vocabseditor.settings.dev`
    
 
 ## Usage
 
 Import an existing skos vocabulary (accepted formats are ttl, rdf): specify the file name, main language of the vocabulary, file format, your username
 
 Run e.g.
 
 `python manage.py import_skos_vocab your_vocabulary.ttl en ttl your_username`
 
 
 More information on how to use the tool in the [Vocabs editor Wiki](https://github.com/acdh-oeaw/vocabseditor/wiki).
 
 ## Testing
 
Tests are located in `/tests` directory in an individual app folder.

Run tests for the whole project:

 `python manage.py test --settings=vocabseditor.settings.dev`
 
 Run tests with coverage:
 
  `coverage run manage.py test --settings=vocabseditor.settings.dev `
 
  `coverage html `

## Docker

### building the image

`docker build -t vocabseditor:latest .`

### running the image

To run the image you should provide an `.env` file to pass in needed environment variables; see example below:

```
DB_NAME=vocabseditor
DB_USER=vocabseditor_user
DB_PASSWORD=verysecret
PROJECT_NAME=vocabseditor
DJANGO_SUPERUSER_USERNAME=user1
DJANGO_SUPERUSER_PASSWORD=pw1
```

`docker run -it -p 8020:8020 --rm --env-file .env_dev vocabseditor`