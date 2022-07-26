import os
from django.conf import settings
from github import Github
from github import InputGitTreeElement


def push_to_gh(
    files,
    ghpat=settings.GHPAT,
    repo_name=settings.GHREPO,
    branch="master",
    commit_message="some message"
):
    g = Github(ghpat)
    repo = g.get_repo(repo_name)
    master_ref = repo.get_git_ref(f'heads/{branch}')
    master_sha = master_ref.object.sha
    base_tree = repo.get_git_tree(master_sha)
    element_list = list()
    for entry in files:
        _, file_name = os.path.split(entry)
        with open(entry) as input_file:
            data = input_file.read()
        element = InputGitTreeElement(f"dumps/{file_name}", '100644', 'blob', data)
        element_list.append(element)
    tree = repo.create_git_tree(element_list, base_tree)
    parent = repo.get_git_commit(master_sha)
    commit = repo.create_git_commit(commit_message, tree, [parent])
    master_ref.edit(commit.sha)


RDF_FORMATS = {
    "xml": "rdf",
    "n3": "n3",
    "turtle": "ttl",
    "nt": "nt",
    "pretty-xml": "rdf",
    "trix": "trix",
    "trig": "trig",
    "nquads": "nq",
    "json-ld": ".jsonld",
}


def handle_uploaded_file(file):
    file_name = file.name
    full_file_name = os.path.join(
        settings.MEDIA_ROOT,
        'uploads',
        file_name
    )
    with open(full_file_name, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return full_file_name
