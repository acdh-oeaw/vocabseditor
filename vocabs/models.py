from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.functional import cached_property
from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from guardian.shortcuts import assign_perm, remove_perm
from django.dispatch import receiver
import reversion
from mptt.models import MPTTModel, TreeForeignKey


DEFAULT_URI = "https://vocabs.acdh.oeaw.ac.at/"

try:
    DEFAULT_NAMESPACE = settings.VOCABS_SETTINGS['default_nsgg']
except KeyError:
    DEFAULT_NAMESPACE = "https://vocabs.acdh.oeaw.ac.at/provide-some-namespace"

try:
    DEFAULT_PREFIX = settings.VOCABS_SETTINGS['default_prefix']
except KeyError:
    DEFAULT_PREFIX = "provideSome"

try:
    DEFAULT_LANG = settings.VOCABS_SETTINGS['default_lang']
except KeyError:
    DEFAULT_LANG = "en"


LABEL_TYPES = (
    ('prefLabel', 'prefLabel'),
    ('altLabel', 'altLabel'),
    ('hiddenLabel', 'hiddenLabel'),
)

NOTE_TYPES = (
    ('note', 'note'),
    ('scopeNote', 'scopeNote'),
    ('changeNote', 'changeNote'),
    ('editorialNote', 'editorialNote'),
    ('historyNote', 'historyNote'),
    ('definition', 'definition'),
    ('example', 'example'),
)



######################################################################
#
# SkosConceptScheme
#
######################################################################

@reversion.register()
class SkosConceptScheme(models.Model):
    """
    A SKOS concept scheme can be viewed as an aggregation of one or more SKOS concepts.
    Semantic relationships (links) between those concepts
    may also be viewed as part of a concept scheme.

    Miles, Alistair, and Sean Bechhofer. "SKOS simple knowledge
    organization system reference. W3C recommendation (2009)."
    """
    title = models.CharField(
        max_length=300,
        help_text="Title of a Concept Scheme",
        verbose_name="dc:title"
    )
    title_lang = models.CharField(
        max_length=3, blank=True,
        verbose_name="dc:title language", default=DEFAULT_LANG,
        help_text="Language of a given title"
    )
    identifier = models.URLField(
        blank=True, help_text="URI that unambiguously identifies current Concept Scheme"
    )
    creator = models.TextField(
        blank=True, verbose_name="dc:creator",
        help_text="If more than one list all using a semicolon ;"
    )
    contributor = models.TextField(
        blank=True, verbose_name="dc:contributor",
        help_text="A Person or Organisation that made contributions to the vocabulary<br>"
        "If more than one list all using a semicolon ;"
    )
    language = models.TextField(
        blank=True, verbose_name="dc:language",
        help_text="Language(s) used in Concept Scheme<br>"
        "If more than one list all using a semicolon ;"
    )
    subject = models.TextField(
        blank=True, verbose_name="dc:subject",
        help_text="The subject of the vocabulary<br>"
        "If more than one list all using a semicolon ;"
    )
    version = models.CharField(
        max_length=300, blank=True,
        help_text="Current version"
    )
    publisher = models.CharField(
        max_length=300, blank=True,
        help_text="An Organisation responsible for making the vocabulary available",
        verbose_name="dc:publisher"
    )
    license = models.CharField(
        max_length=300, blank=True,
        verbose_name="dct:license",
        help_text="Information about license applied to a vocabulary"
    )
    owner = models.CharField(
        max_length=300, blank=True,
        help_text="A Person or Organisation that own rights for the vocabulary"
    )
    relation = models.URLField(
        blank=True, verbose_name="dc:relation",
        help_text="E.g. in case of relation to a project, add link to a project website"
    )
    coverage = models.TextField(
        blank=True, verbose_name="dc:coverage",
        help_text="The spatial or temporal coverage of a vocabulary<br>"
        "If more than one list all using a semicolon ;"
    )
    legacy_id = models.CharField(
        max_length=200, blank=True
    )
    date_created = models.DateTimeField(
        editable=False, default=timezone.now
    )
    date_modified = models.DateTimeField(
        editable=False, default=timezone.now
    )
    date_issued = models.DateField(
        blank=True, null=True,
        help_text="Date of official resource publication"
    )
    created_by = models.ForeignKey(
        User, related_name="skos_cs_created",
        blank=True, null=True,
        on_delete=models.SET_NULL
    )
    curator = models.ManyToManyField(
        User, related_name="skos_cs_curated",
        blank=True,
        help_text="The selected user(s) will be able to view and edit current Concept Scheme"
    )

    class Meta:
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.id:
            self.date_created = timezone.now()
        self.date_modified = timezone.now()

        if not self.identifier:
            self.identifier = DEFAULT_URI + slugify(self.title, allow_unicode=True)
        super(SkosConceptScheme, self).save(*args, **kwargs)

    def creator_as_list(self):
        return self.creator.split(';')

    def contributor_as_list(self):
        return self.contributor.split(';')

    def language_as_list(self):
        return self.language.split(';')

    def subject_as_list(self):
        return self.subject.split(';')

    def coverage_as_list(self):
        return self.coverage.split(';')

    @classmethod
    def get_listview_url(self):
        return reverse('vocabs:browse_schemes')

    @classmethod
    def get_createview_url(self):
        return reverse('vocabs:skosconceptscheme_create')

    def get_absolute_url(self):
        return reverse('vocabs:skosconceptscheme_detail', kwargs={'pk': self.id})

    def get_next(self):
        next = SkosConceptScheme.objects.filter(id__gt=self.id)
        if next:
            return next.first().id
        return False

    def get_prev(self):
        prev = SkosConceptScheme.objects.filter(id__lt=self.id).order_by('-id')
        if prev:
            return prev.first().id
        return False

    def __str__(self):
        return self.title


######################################################################
#   Classes  to store titles and descriptions for ConceptScheme
######################################################################

class ConceptSchemeTitle(models.Model):
    """
    A Class for ConceptScheme titles in other languages.
    
    """
    concept_scheme = models.ForeignKey(
        SkosConceptScheme,
        related_name="has_titles",
        verbose_name="skos:ConceptScheme",
        help_text="Which Skos:ConceptScheme current Title belongs to",
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=500, verbose_name="Dc:title",
        help_text="Title of a Concept Scheme"
    )
    language = models.CharField(
        max_length=3, verbose_name="Dc:title language",
        help_text="Language of a given title"
    )

    def __str__(self):
        return "{}".format(self.name)


class ConceptSchemeDescription(models.Model):
    """
    A Class for ConceptScheme descriptions in other languages.
    
    """
    concept_scheme = models.ForeignKey(
        SkosConceptScheme,
        related_name="has_descriptions",
        verbose_name="skos:ConceptScheme",
        help_text="Which Skos:ConceptScheme current Description belongs to",
        on_delete=models.CASCADE
    )
    name = models.TextField(
        verbose_name="Dc:description",
        help_text="Description of a Concept Scheme"
    )
    language = models.CharField(
        max_length=3, verbose_name="Dc:description language",
        help_text="Language of a given description"
    )

    def __str__(self):
        return self.name


class ConceptSchemeSource(models.Model):
    """
    A Class for ConceptScheme source information.
    
    """
    concept_scheme = models.ForeignKey(
        SkosConceptScheme,
        related_name="has_sources",
        verbose_name="skos:ConceptScheme",
        help_text="Which Skos:ConceptScheme current source belongs to",
        on_delete=models.CASCADE
    )
    name = models.TextField(
        verbose_name="Dc:source",
        help_text="A verbose description of a Concept Scheme's source"
    )
    language = models.CharField(
        max_length=3, verbose_name="Dc:source language",
        help_text="Language of a given source"
    )

    def __str__(self):
        return "{}".format(self.name)



######################################################################
#
# SkosCollection
#
######################################################################

@reversion.register()
class SkosCollection(models.Model):
    """
    SKOS collections are labeled and/or ordered groups of SKOS concepts.
    Collections are useful where a group of concepts shares something in common,
    and it is convenient to group them under a common label, or
    where some concepts can be placed in a meaningful order.

    Miles, Alistair, and Sean Bechhofer. "SKOS simple knowledge
    organization system reference. W3C recommendation (2009)."

    """
    name = models.CharField(
        max_length=300, verbose_name="skos:prefLabel",
        help_text="Collection label or name"
    )
    label_lang = models.CharField(
        max_length=3, blank=True,
        default=DEFAULT_LANG,
        verbose_name="skos:prefLabel language"
    )
    # relation to SkosConceptScheme to inherit all objects permissions
    scheme = models.ForeignKey(SkosConceptScheme,
        related_name="has_collections",
        verbose_name="skos:ConceptScheme",
        help_text="Which Skos:ConceptScheme current collection belongs to",
        on_delete=models.CASCADE
    )
    creator = models.TextField(
        blank=True, verbose_name="dc:creator",
        help_text="A Person or Organisation that created a current collection<br>"
        "If more than one list all using a semicolon ;"
    )
    contributor = models.TextField(
        blank=True, verbose_name="dc:contributor",
        help_text="A Person or Organisation that made contributions to the collection<br>"
        "If more than one list all using a semicolon ;"
    )
    legacy_id = models.CharField(
        max_length=200, blank=True
    )
    # meta autosaved fields
    date_created = models.DateTimeField(
        editable=False, default=timezone.now
    )
    date_modified = models.DateTimeField(
        editable=False, default=timezone.now
    )
    created_by = models.ForeignKey(
        User, related_name="skos_collection_created",
        blank=True, null=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.id:
            self.date_created = timezone.now()
        self.date_modified = timezone.now()
        return super(SkosCollection, self).save(*args, **kwargs)

    @classmethod
    def get_listview_url(self):
        return reverse('vocabs:browse_skoscollections')

    @classmethod
    def get_createview_url(self):
        return reverse('vocabs:skoscollection_create')

    def get_absolute_url(self):
        return reverse('vocabs:skoscollection_detail', kwargs={'pk': self.id})

    def get_next(self):
        next = SkosCollection.objects.filter(id__gt=self.id)
        if next:
            return next.first().id
        return False

    def get_prev(self):
        prev = SkosCollection.objects.filter(id__lt=self.id).order_by('-id')
        if prev:
            return prev.first().id
        return False

    def __str__(self):
        return self.name

    def creator_as_list(self):
        return self.creator.split(';')

    def contributor_as_list(self):
        return self.contributor.split(';')


######################################################################
#   Classes  to store labels and notes for Collection
######################################################################


class CollectionLabel(models.Model):
    """
    A Class for Collection labels/names in other languages.
    
    """
    collection = models.ForeignKey(
        SkosCollection,
        related_name="has_labels",
        verbose_name="skos:Collection",
        help_text="Which Skos:Collection current label belongs to",
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=500, verbose_name="Label",
        help_text="Collection label (name)"
    )
    language = models.CharField(
        max_length=3, verbose_name="Language",
        help_text="Language of a given label"
    )
    label_type = models.CharField(
        choices=LABEL_TYPES, default='altLabel',
        max_length=12, help_text="Choose label type"
    )

    def __str__(self):
        return "{}".format(self.name)


class CollectionNote(models.Model):
    """
    A Class for SKOS documentary notes that are used
    for general documentation pusposes.

    """
    collection = models.ForeignKey(
        SkosCollection,
        related_name="has_notes",
        verbose_name="skos:Collection",
        help_text="Which Skos:Collection current documentary note belongs to",
        on_delete=models.CASCADE
    )
    name = models.TextField(
        verbose_name="Documentary note",
        help_text="Provide some information about Collection"
    )
    language = models.CharField(
        max_length=3,
        help_text="Language of a given note"
    )
    note_type = models.CharField(
        choices=NOTE_TYPES, default='note',
        max_length=15, help_text="Choose note type"
    )

    def __str__(self):
        return "{}".format(self.name)


class CollectionSource(models.Model):
    """
    A Class for Collection source information.
    
    """
    collection = models.ForeignKey(
        SkosCollection,
        related_name="has_sources",
        verbose_name="skos:Collection",
        help_text="Which Skos:Collection current source belongs to",
        on_delete=models.CASCADE
    )
    name = models.TextField(
        verbose_name="Source",
        help_text="A verbose description of the collection's source"
    )
    language = models.CharField(
        max_length=3, help_text="Language of a given source"
    )

    def __str__(self):
        return "{}".format(self.name)


######################################################################
#
# SkosConcept
#
######################################################################

@reversion.register()
class SkosConcept(MPTTModel):
    """
    A SKOS concept can be viewed as an idea or notion; a unit of thought.
    However, what constitutes a unit of thought is subjective,
    and this definition is meant to be suggestive, rather than restrictive.

    Miles, Alistair, and Sean Bechhofer. "SKOS simple knowledge
    organization system reference. W3C recommendation (2009)."
    """
    pref_label = models.CharField(
        max_length=300,
        verbose_name="skos:prefLabel",
        help_text="Preferred label for a concept"
    )
    pref_label_lang = models.CharField(
        max_length=3, blank=True,
        verbose_name="skos:prefLabel language",
        help_text="Language code of preferred label according to ISO 639-1",
        default=DEFAULT_LANG
    )
    # relation to SkosConceptScheme to inherit all objects permissions
    scheme = models.ForeignKey(
        SkosConceptScheme,
        verbose_name="skos:inScheme",
        related_name="has_concepts",
        on_delete=models.CASCADE,
        help_text="A Concept Scheme to which this concept belongs"
    )
    top_concept = models.BooleanField(
        null=True,
        help_text="Is this concept a top concept of main Concept Scheme?"
    )
    collection = models.ManyToManyField(
        SkosCollection, blank=True,
        verbose_name="member of skos:Collection",
        related_name="has_members",
    )
    notation = models.CharField(
        max_length=300, blank=True,
        verbose_name="skos:notation",
        help_text="A notation is a unique string used\
        to identify the concept in current vocabulary"
    )
    same_as_external = models.TextField(
        blank=True,
        verbose_name="owl:sameAs",
        help_text="URL of an external Concept with the same meaning<br>"
        "If more than one list all using a semicolon ; ",
    )
    broader_concept = TreeForeignKey(
        'self',
        verbose_name="skos:broader",
        blank=True, null=True, on_delete=models.CASCADE,
        related_name="narrower_concepts",
        help_text="A concept with a broader meaning that a current concept inherits from"
    )
    ################# semantic relationships via autocomplete #################
    related = models.TextField(
        blank=True, verbose_name="skos:related",
        help_text="An associative relationship among two concepts"
    )
    broad_match = models.TextField(
        blank=True, verbose_name="skos:broadMatch",
        help_text="A concept in an external Concept Scheme with a broader meaning"
    )    
    narrow_match = models.TextField(
        blank=True, verbose_name="skos:narrowMatch",
        help_text="A concept in an external Concept Scheme with a narrower meaning"
    )
    exact_match = models.TextField(
        blank=True, verbose_name="skos:exactMatch",
        help_text="A concept in an external Concept Scheme "
        "that can be used interchangeably and has an exact same meaning"
    )
    related_match = models.TextField(
        blank=True, verbose_name="skos:relatedMatch",
        help_text="A concept in an external Concept Scheme that has an associative "
        "relationship with a current concept"
    )
    close_match = models.TextField(
        blank=True, verbose_name="skos:closeMatch",
        help_text="A concept in an external Concept Scheme that has a similar meaning"
    )
    ###########################################################################
    # if using legacy_id as URI change it for URLField
    legacy_id = models.CharField(max_length=200, blank=True)
    creator = models.TextField(
        blank=True, verbose_name="dc:creator",
        help_text="A Person or Organisation that created a current concept<br>"
        "If more than one list all using a semicolon ;",

    )
    contributor = models.TextField(
        blank=True, verbose_name="dc:contributor",
        help_text="A Person or Organisation that made contributions to the concept<br>"
        "If more than one list all using a semicolon ;"
    )
    date_created = models.DateTimeField(
        editable=False, default=timezone.now,
        verbose_name="dct:created"
    )
    date_modified = models.DateTimeField(
        editable=False, default=timezone.now,
        verbose_name="dct:modified"
    )
    created_by = models.ForeignKey(
        User, related_name="skos_concept_created",
        blank=True, null=True,
        on_delete=models.SET_NULL
    )

    class MPTTMeta:
        order_insertion_by = ['pref_label']
        parent_attr = 'broader_concept'

    def get_vocabs_uri(self):
        return "{}{}".format("https://whatever", self.get_absolute_url)

    def save(self, *args, **kwargs):
        if self.notation == "":
            temp_notation = slugify(self.pref_label, allow_unicode=True)
            concepts = len(SkosConcept.objects.filter(notation=temp_notation))
            if concepts < 1:
                self.notation = temp_notation
            else:
                self.notation = "{}-{}".format(temp_notation, concepts)
        else:
            pass

        if not self.id:
            self.date_created = timezone.now()
        self.date_modified = timezone.now()
        super(SkosConcept, self).save(*args, **kwargs)

    # change for template tag
    def creator_as_list(self):
        return self.creator.split(';')

    def contributor_as_list(self):
        return self.contributor.split(';')

    def same_as_external_as_list(self):
        return self.same_as_external.split(';')

    def broad_match_as_list(self):
        return self.broad_match.split(',')

    def related_as_list(self):
        return self.related.split(',')

    def narrow_match_as_list(self):
        return self.narrow_match.split(',')

    def exact_match_as_list(self):
        return self.exact_match.split(',')

    def related_match_as_list(self):
        return self.related_match.split(',')

    def close_match_as_list(self):
        return self.close_match.split(',')

    @classmethod
    def get_listview_url(self):
        return reverse('vocabs:browse_vocabs')

    @classmethod
    def get_createview_url(self):
        return reverse('vocabs:skosconcept_create')

    def get_absolute_url(self):
        return reverse('vocabs:skosconcept_detail', kwargs={'pk': self.id})

    def __str__(self):
        return self.pref_label


######################################################################
#   Classes  to store labels and notes for Concept
######################################################################


class ConceptLabel(models.Model):
    """
    A Class for Concept labels of any type.
    
    """
    concept = models.ForeignKey(
        SkosConcept,
        related_name="has_labels",
        verbose_name="skos:Concept",
        help_text="Which Skos:Concept current label belongs to",
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=500, verbose_name="Label",
        help_text="Other label for a current concept"
    )
    language = models.CharField(
        max_length=3, verbose_name="Language",
        help_text="Language of a given label"
    )
    label_type = models.CharField(
        choices=LABEL_TYPES, default='altLabel',
        max_length=12, help_text="Choose label type"
    )

    def __str__(self):
        return "{}".format(self.name)
    

class ConceptNote(models.Model):
    """
    A Class for SKOS documentary notes that are used
    for general documentation pusposes.

    """
    concept = models.ForeignKey(
        SkosConcept,
        related_name="has_notes",
        verbose_name="skos:Concept",
        help_text="Which Skos:Concept current documentary note belongs to",
        on_delete=models.CASCADE
    )
    name = models.TextField(
        verbose_name="Documentary note",
        help_text="Provide some information about Concept"
    )
    language = models.CharField(
        max_length=3, verbose_name="Language",
        help_text="Language of a given note"
    )
    note_type = models.CharField(
        choices=NOTE_TYPES, default='note',
        max_length=15, help_text="Choose note type"
    )

    def __str__(self):
        return "{}".format(self.name)


class ConceptSource(models.Model):
    """
    A Class for Concept source information.
    
    """
    concept = models.ForeignKey(
        SkosConcept,
        related_name="has_sources",
        verbose_name="skos:Concept",
        help_text="Which Skos:Concept current source belongs to",
        on_delete=models.CASCADE
    )
    name = models.TextField(
        verbose_name="Source",
        help_text="A verbose description of the concept's source"
    )
    language = models.CharField(
        max_length=3, verbose_name="Language",
        help_text="Language of a given source"
    )

    def __str__(self):
        return "{}".format(self.name)



def get_all_children(self, include_self=True):
    # many thanks to https://stackoverflow.com/questions/4725343
    r = []
    if include_self:
        r.append(self)
    for c in SkosConcept.objects.filter(broader_concept=self):
        _r = get_all_children(c, include_self=True)
        if 0 < len(_r):
            r.extend(_r)
    return r

#############################################################################
#
# Permissions on signals
#
#############################################################################


@receiver(post_save, sender=SkosConceptScheme, dispatch_uid="create_perms_cs_created_by")
def create_perms_cs_created_by(sender, instance, **kwargs):
    assign_perm('delete_skosconceptscheme', instance.created_by, instance)
    assign_perm('change_skosconceptscheme', instance.created_by, instance)
    assign_perm('view_skosconceptscheme', instance.created_by, instance)


@receiver(post_save, sender=SkosCollection, dispatch_uid="create_perms_collection_created_by")
def create_perms_collection_created_by(sender, instance, **kwargs):
    assign_perm('delete_skoscollection', instance.created_by, instance)
    assign_perm('change_skoscollection', instance.created_by, instance)
    assign_perm('view_skoscollection', instance.created_by, instance)
    for curator in instance.scheme.curator.all():
        assign_perm('delete_skoscollection', curator, instance)
        assign_perm('change_skoscollection', curator, instance)
        assign_perm('view_skoscollection', curator, instance)
        if curator is not instance.scheme.created_by:
            assign_perm('delete_skoscollection', instance.scheme.created_by, instance)
            assign_perm('change_skoscollection', instance.scheme.created_by, instance)
            assign_perm('view_skoscollection', instance.scheme.created_by, instance)


@receiver(post_save, sender=SkosConcept, dispatch_uid="create_perms_concept_created_by")
def create_perms_concept_created_by(sender, instance, **kwargs):
    assign_perm('delete_skosconcept', instance.created_by, instance)
    assign_perm('change_skosconcept', instance.created_by, instance)
    assign_perm('view_skosconcept', instance.created_by, instance)
    for curator in instance.scheme.curator.all():
        assign_perm('delete_skosconcept', curator, instance)
        assign_perm('change_skosconcept', curator, instance)
        assign_perm('view_skosconcept', curator, instance)
        if curator is not instance.scheme.created_by:
            assign_perm('delete_skosconcept', instance.scheme.created_by, instance)
            assign_perm('change_skosconcept', instance.scheme.created_by, instance)
            assign_perm('view_skosconcept', instance.scheme.created_by, instance)


############### Adding new curator (user) to a Concept Scheme ###################
############### Only user who created a Concept Scheme can do it ################


@receiver(m2m_changed, sender=SkosConceptScheme.curator.through, dispatch_uid="create_perms_curator")
def create_perms_curator(sender, instance, **kwargs):
    if kwargs['action'] == 'pre_add':
        for curator in User.objects.filter(pk__in=kwargs['pk_set']):
            assign_perm('view_skosconceptscheme', curator, instance)
            assign_perm('change_skosconceptscheme', curator, instance)
            assign_perm('delete_skosconceptscheme', curator, instance)
            for obj in instance.has_collections.all():
                assign_perm('view_'+obj.__class__.__name__.lower(), curator, obj)
                assign_perm('change_'+obj.__class__.__name__.lower(), curator, obj)
                assign_perm('delete_'+obj.__class__.__name__.lower(), curator, obj)
            for obj in instance.has_concepts.all():
                assign_perm('view_'+obj.__class__.__name__.lower(), curator, obj)
                assign_perm('change_'+obj.__class__.__name__.lower(), curator, obj)
                assign_perm('delete_'+obj.__class__.__name__.lower(), curator, obj)
    elif kwargs['action'] == 'post_remove':
        for curator in User.objects.filter(pk__in=kwargs['pk_set']):
            remove_perm('view_skosconceptscheme', curator, instance)
            remove_perm('change_skosconceptscheme', curator, instance)
            # if user removed from the curators list
            # he/she won't be able to access the objects he/she created within this CS
            for obj in instance.has_collections.all():
                remove_perm('view_'+obj.__class__.__name__.lower(), curator, obj)
                remove_perm('change_'+obj.__class__.__name__.lower(), curator, obj)
                remove_perm('delete_'+obj.__class__.__name__.lower(), curator, obj)
            for obj in instance.has_concepts.all():
                remove_perm('view_'+obj.__class__.__name__.lower(), curator, obj)
                remove_perm('change_'+obj.__class__.__name__.lower(), curator, obj)
                remove_perm('delete_'+obj.__class__.__name__.lower(), curator, obj)
