# ACDH Vocabularies Editor

## About

The purpose of ACDH Vocabularies Editor is to provide a service for collaborative work on controlled vocabularies development.

The editor follows *SKOS data model* for the main elements of a controlled vocabulary. *Dublin core* schema is used to capture the metadata (such as date created, date modified, creator, contributor, source and other) about each element. Each Concept Scheme can be downloaded in *RDF/XML* and *Turtle* formats as well as each individual Concept.

*The user management* system allows a user to share a created Concept Scheme with other users (called 'curators') to create new, edit and delete Concepts and Collections within this Concept Scheme. Each user can find a summary of her/his latest activity on user's page.


## Technical setup

The application is implemented using Python and [Django](https://www.djangoproject.com/). It uses modules deleloped within [DjangoBaseProject](https://github.com/acdh-oeaw/djangobaseproject). It also provides REST API implemented with [Django Rest Framework](https://www.django-rest-framework.org/). 

## Install

1. Clone the repo
2. Create virtual environment and run `pip install -r requirements.txt`
