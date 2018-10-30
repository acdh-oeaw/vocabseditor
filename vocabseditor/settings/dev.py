from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^mm-24*i-6iecm7c@z9l+7%^ns^4g^z!8=dgffg4ulggr-4=1%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


Z_ID = "1****5"
Z_ID_TYPE = 'groups'  # or 'user'
Z_COLLECTION = "*****Z"
Z_API_KEY = "T******************A"
Z_COLLECTION_URL = "https://www.zotero.org/{}/{}/peter_handke_stage_texts".format(
    Z_ID, Z_COLLECTION
)
Z_TITLE = "Some Titel of the Zotero Library"
