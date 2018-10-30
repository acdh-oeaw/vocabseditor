from .base import *

SECRET_KEY = 'whatever'
DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS + [
    'django_nose',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-coverage',          # generate coverage
    '--cover-package=vocabseditor,vocabs,webpage',
    '--cover-html',             # generate a html cover report
    '--nocapture',              # needed to show print output in console
    '--nologcapture',           # needed to show print output in console
    '--cover-erase',            # without cover erase test coverage artifacts could remain
]
