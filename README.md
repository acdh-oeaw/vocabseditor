# Vocabseditor

## About

The purpose of the Vocabseditor is to provide a service for collaborative work on controlled vocabularies development.

The editor follows **SKOS data model** for the main elements of a vocabulary. The **Dublin core** schema is used to capture the metadata (such as date created, date modified, creator, contributor, source and other) about each element. Each concept scheme can be downloaded in **RDF/XML** and *Turtle* format as well as each individual concept.

**The user management** system allows a user to share a concept scheme she/he created with other users (called 'curators') to create new, edit and delete concepts and collections within this concept scheme. Each user can find a summary of their latest activity on user's page.


## Technical setup

The application is implemented using Python and [Django](https://www.djangoproject.com/). It uses modules developed within [DjangoBaseProject](https://github.com/acdh-oeaw/djangobaseproject). It also provides REST API implemented with [Django Rest Framework](https://www.django-rest-framework.org/). 

## Install

1. Clone the repo
2. Create virtual environment and run `pip install -r requirements.txt`