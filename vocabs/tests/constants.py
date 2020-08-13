USER = {
    "username": "testuser",
    "password": "12345"
}

def concept_scheme(user):
    return {
        "title": "Test Concept Scheme",
        "title_lang": "en",
        "created_by": user
    }


def collection(concept_scheme, user):
    return {
        "name": "Test Collection",
        "label_lang": "en",
        "scheme": concept_scheme,
        "created_by": user
    }


def concept(concept_scheme, label, user, broader=None):
    return {
        "pref_label": label,
        "pref_label_lang": "en",
        "scheme": concept_scheme,
        "broader_concept": broader,
        "created_by": user
    }
