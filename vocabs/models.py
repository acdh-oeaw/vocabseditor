import reversion
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from guardian.shortcuts import assign_perm, remove_perm
from mptt.models import MPTTModel, TreeForeignKey
from rdflib import XSD, Literal, URIRef

try:
    notation_for_uri = settings.VOCABS_SETTINGS["notation_for_uri"]
except KeyError:
    notation_for_uri = False

VOCABS_SEPARATOR = getattr(settings, "VOCABS_SEPARATOR", "/")

DEFAULT_URI = "https://vocabs.acdh.oeaw.ac.at/"

try:
    DEFAULT_NAMESPACE = settings.VOCABS_SETTINGS["default_nsgg"]
except KeyError:
    DEFAULT_NAMESPACE = "https://vocabs.acdh.oeaw.ac.at/provide-some-namespace"

try:
    DEFAULT_PREFIX = settings.VOCABS_SETTINGS["default_prefix"]
except KeyError:
    DEFAULT_PREFIX = "provideSome"

try:
    DEFAULT_LANG = settings.VOCABS_SETTINGS["default_lang"]
except KeyError:
    DEFAULT_LANG = "en"


try:
    CUSTOM_PROPS = settings.VOCAPS_CUSTOM_PROPERTIES
except AttributeError:
    CUSTOM_PROPS = [
        {
            "prop_uri": "http://xmlns.com/foaf/0.1/homepage",
            "prop_type": "object",
            "prop_label": "Homepage",
        },
    ]

CUSTOM_PROPS_URIS = [(x["prop_uri"], x["prop_label"]) for x in CUSTOM_PROPS]
CUSTOM_PORPS_TYPES = {}
for x in CUSTOM_PROPS:
    CUSTOM_PORPS_TYPES[x["prop_uri"]] = x["prop_type"]

LABEL_TYPES = (
    ("prefLabel", "prefLabel"),
    ("altLabel", "altLabel"),
    ("hiddenLabel", "hiddenLabel"),
)

NOTE_TYPES = (
    ("note", "note"),
    ("scopeNote", "scopeNote"),
    ("changeNote", "changeNote"),
    ("editorialNote", "editorialNote"),
    ("historyNote", "historyNote"),
    ("definition", "definition"),
    ("example", "example"),
)


SKOS_RELATION_TYPES = [
    ("related", "related"),
    ("broadMatch", "broad_match"),
    ("narrowMatch", "narrow_match"),
    ("exactMatch", "exact_match"),
    ("relatedMatch", "related_match"),
    ("closeMatch", "close_match"),
]


class CustomProperty(models.Model):
    prop_uri = models.CharField(
        max_length=300,
        verbose_name="URL of the property",
        help_text="e.g. foaf:homepage",
        choices=CUSTOM_PROPS_URIS,
    )
    prop_value = models.CharField(
        max_length=300,
        verbose_name="Poperty value",
        help_text="e.g. 'http://foo-bar' or a date 'YYYY-MM-DD'",
    )
    prop_lang = models.CharField(
        max_length=3,
        default=DEFAULT_LANG,
        verbose_name="Language",
        help_text=f"e.g. 'de', defaults to '{DEFAULT_LANG}'",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Custom property"
        verbose_name_plural = "Custom properties"

    def __str__(self):
        return f"{self.prop_value} ({self.prop_uri})"

    def get_predicate_object(self):
        predicate = URIRef(self.prop_uri)
        prop_type = CUSTOM_PORPS_TYPES[self.prop_uri]
        if prop_type == "object":
            obj = URIRef(self.prop_value)
        elif prop_type == "xsd:date":
            obj = Literal(self.prop_value, datatype=XSD.date)
        else:
            obj = Literal(self.prop_value, lang=self.prop_lang)
        return predicate, obj

    def save(self, *args, **kwargs):
        self.get_rdf_object()
        super(CustomProperty, self).save(*args, **kwargs)


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
        help_text="Title  for new concept scheme",
        verbose_name="dc:title",
    )
    title_lang = models.CharField(
        max_length=53,
        blank=True,
        verbose_name="dc:title language",
        default=DEFAULT_LANG,
        help_text="Language of title given above",
    )
    identifier = models.URLField(blank=True, help_text="URI to unambiguously identify current Concept Scheme")
    creator = models.TextField(
        blank=True,
        verbose_name="dc:creator",
        help_text="Person or organisation primarily responsible for making current concept scheme<br>"
        "If more than one list all using a semicolon ;",
    )
    contributor = models.TextField(
        blank=True,
        verbose_name="dc:contributor",
        help_text="Person or organisation that made contributions to the vocabulary<br>"
        "If more than one list all using a semicolon ;",
    )
    language = models.TextField(
        blank=True,
        verbose_name="dc:language",
        help_text="Language(s) used in concept scheme<br>If more than one list all using a semicolon ;",
    )
    subject = models.TextField(
        blank=True,
        verbose_name="dc:subject",
        help_text="The subject of the vocabulary<br>If more than one list all using a semicolon ;",
    )
    version = models.CharField(max_length=300, blank=True, help_text="Current version")
    publisher = models.CharField(
        max_length=300,
        blank=True,
        help_text="Organisation responsible for making the vocabulary available",
        verbose_name="dc:publisher",
    )
    license = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="dct:license",
        help_text="Information about license applied to the vocabulary",
    )
    owner = models.CharField(
        max_length=300,
        blank=True,
        help_text="Person or organisation that owns the rights for the vocabulary",
    )
    relation = models.URLField(
        blank=True,
        verbose_name="dc:relation",
        help_text="Related resource or project<br>E.g. in case of relation to a project, add link to a project website",
    )
    coverage = models.TextField(
        blank=True,
        verbose_name="dc:coverage",
        help_text="Spatial or temporal frame that the vocabulary relates to<br>"
        "If more than one list all using a semicolon ;",
    )
    legacy_id = models.CharField(max_length=200, blank=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    date_issued = models.DateField(
        blank=True,
        null=True,
        help_text="Date of official publication of this concept scheme",
    )
    created_by = models.ForeignKey(
        User,
        related_name="skos_cs_created",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    curator = models.ManyToManyField(
        User,
        related_name="skos_cs_curated",
        blank=True,
        help_text="The selected user(s) will be able to view and edit this Concept Scheme",
    )
    custom_props = models.ManyToManyField("CustomProperty", blank=True, null=True, verbose_name="Custom properties")

    class Meta:
        ordering = ["id"]
        verbose_name = "Concept Scheme"

    def save(self, *args, **kwargs):
        if not self.id:
            self.date_created = timezone.now()
        self.date_modified = timezone.now()

        if not self.identifier:
            self.identifier = DEFAULT_URI + slugify(self.title, allow_unicode=True)
        super(SkosConceptScheme, self).save(*args, **kwargs)

    def creator_as_list(self):
        return self.creator.split(";")

    def contributor_as_list(self):
        return self.contributor.split(";")

    def language_as_list(self):
        return self.language.split(";")

    def subject_as_list(self):
        return self.subject.split(";")

    def coverage_as_list(self):
        return self.coverage.split(";")

    @classmethod
    def get_listview_url(self):
        return reverse("vocabs:browse_schemes")

    @classmethod
    def get_createview_url(self):
        return reverse("vocabs:skosconceptscheme_create")

    def get_absolute_url(self):
        return reverse("vocabs:skosconceptscheme_detail", kwargs={"pk": self.id})

    def get_next(self):
        next = SkosConceptScheme.objects.filter(id__gt=self.id)
        if next:
            return next.first().id
        return False

    def get_prev(self):
        prev = SkosConceptScheme.objects.filter(id__lt=self.id).order_by("-id")
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
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=500,
        verbose_name="dc:title",
        help_text="Other title for new concept scheme",
    )
    language = models.CharField(
        max_length=53,
        verbose_name="dc:title language",
        help_text="Language of title given above",
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
        on_delete=models.CASCADE,
    )
    name = models.TextField(verbose_name="dc:description", help_text="Description of concept scheme")
    language = models.CharField(
        max_length=53,
        verbose_name="dc:description language",
        help_text="Language of description given above",
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
        on_delete=models.CASCADE,
    )
    name = models.TextField(
        verbose_name="dc:source",
        help_text="Verbal description of a concept scheme's source",
    )
    language = models.CharField(
        max_length=53,
        verbose_name="dc:source language",
        help_text="Language of source given above",
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
        max_length=300,
        verbose_name="skos:prefLabel",
        help_text="Collection label or name",
    )
    label_lang = models.CharField(
        max_length=3,
        blank=True,
        default=DEFAULT_LANG,
        verbose_name="skos:prefLabel language",
        help_text="Language of preferred label given above",
    )
    # relation to SkosConceptScheme to inherit all objects permissions
    scheme = models.ForeignKey(
        SkosConceptScheme,
        related_name="has_collections",
        verbose_name="skos:ConceptScheme",
        help_text="Concept scheme that this collection belongs to",
        on_delete=models.CASCADE,
    )
    creator = models.TextField(
        blank=True,
        verbose_name="dc:creator",
        help_text="Person or organisation that created this collection<br>"
        "If more than one list all using a semicolon ;",
    )
    contributor = models.TextField(
        blank=True,
        verbose_name="dc:contributor",
        help_text="Person or organisation that made contributions to the collection<br>"
        "If more than one list all using a semicolon ;",
    )
    legacy_id = models.CharField(max_length=200, blank=True)
    # meta autosaved fields
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(
        User,
        related_name="skos_collection_created",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Collection"

    def save(self, *args, **kwargs):
        if not self.id:
            self.date_created = timezone.now()
        self.date_modified = timezone.now()
        return super(SkosCollection, self).save(*args, **kwargs)

    @classmethod
    def get_listview_url(self):
        return reverse("vocabs:browse_skoscollections")

    @classmethod
    def get_createview_url(self):
        return reverse("vocabs:skoscollection_create")

    def get_absolute_url(self):
        return reverse("vocabs:skoscollection_detail", kwargs={"pk": self.id})

    def get_next(self):
        next = SkosCollection.objects.filter(id__gt=self.id)
        if next:
            return next.first().id
        return False

    def get_prev(self):
        prev = SkosCollection.objects.filter(id__lt=self.id).order_by("-id")
        if prev:
            return prev.first().id
        return False

    def __str__(self):
        return self.name

    def creator_as_list(self):
        return self.creator.split(";")

    def contributor_as_list(self):
        return self.contributor.split(";")

    def create_uri(self):
        mcs = self.scheme.identifier
        if mcs.endswith(VOCABS_SEPARATOR):
            pass
        else:
            mcs = f"{mcs}{VOCABS_SEPARATOR}"
        if self.legacy_id:
            item_uri = f"{self.legacy_id}"
        else:
            if notation_for_uri:
                tmp = slugify(self.notation, allow_unicode=False)
                item_uri = f"{mcs}collection__{tmp}__{self.id}"
            else:
                item_uri = f"{mcs}collection{self.id}"
        return item_uri


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
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=500,
        verbose_name="label",
        help_text="Other label for this collection",
    )
    language = models.CharField(
        max_length=53,
        verbose_name="language",
        help_text="Language of label given above",
    )
    label_type = models.CharField(
        choices=LABEL_TYPES,
        verbose_name="label type",
        default="altLabel",
        max_length=12,
        help_text="Choose label type",
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
        on_delete=models.CASCADE,
    )
    name = models.TextField(
        verbose_name="documentary note",
        help_text="Provide some information about this collection",
    )
    language = models.CharField(max_length=53, verbose_name="language", help_text="Language of note given above")
    note_type = models.CharField(
        choices=NOTE_TYPES,
        verbose_name="note type",
        default="note",
        max_length=15,
        help_text="Choose note type",
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
        on_delete=models.CASCADE,
    )
    name = models.TextField(
        verbose_name="dc:source",
        help_text="Verbal description of the collection's source",
    )
    language = models.CharField(
        max_length=53,
        verbose_name="language",
        help_text="Language of source given above",
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
        help_text="Preferred label for concept",
    )
    pref_label_lang = models.CharField(
        max_length=3,
        blank=True,
        verbose_name="skos:prefLabel language",
        help_text="Language of preferred label given above",
        default=DEFAULT_LANG,
    )
    # relation to SkosConceptScheme to inherit all objects permissions
    scheme = models.ForeignKey(
        SkosConceptScheme,
        verbose_name="skos:inScheme",
        related_name="has_concepts",
        on_delete=models.CASCADE,
        help_text="Concept scheme to which this concept belongs",
    )
    top_concept = models.BooleanField(null=True, help_text="Is this concept a top concept of concept scheme?")
    collection = models.ManyToManyField(
        SkosCollection,
        blank=True,
        verbose_name="member of skos:Collection",
        help_text="Collection that this concept is a member of",
        related_name="has_members",
    )
    notation = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="skos:notation",
        help_text="A notation is a unique string used\
        to identify the concept in current vocabulary",
    )
    broader_concept = TreeForeignKey(
        "self",
        verbose_name="skos:broader",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="narrower_concepts",
        help_text="Concept with a broader meaning that this concept inherits from",
    )
    ################# semantic relationships via autocomplete #################
    related = models.TextField(
        blank=True,
        verbose_name="skos:related",
        help_text="An associative relationship between two concepts",
    )
    broad_match = models.TextField(
        blank=True,
        verbose_name="skos:broadMatch",
        help_text="External concept with a broader meaning",
    )
    narrow_match = models.TextField(
        blank=True,
        verbose_name="skos:narrowMatch",
        help_text="External concept with a narrower meaning",
    )
    exact_match = models.TextField(
        blank=True,
        verbose_name="skos:exactMatch",
        help_text="External concept that can be used interchangeably and has the exact same meaning",
    )
    related_match = models.TextField(
        blank=True,
        verbose_name="skos:relatedMatch",
        help_text="External concept that has an associative relationship with this concept",
    )
    close_match = models.TextField(
        blank=True,
        verbose_name="skos:closeMatch",
        help_text="External concept that has a similar meaning",
    )
    ###########################################################################
    # if using legacy_id as URI change it for URLField
    legacy_id = models.CharField(max_length=200, blank=True)
    creator = models.TextField(
        blank=True,
        verbose_name="dc:creator",
        help_text="Person or organisation that created this concept<br>If more than one list all using a semicolon ;",
    )
    contributor = models.TextField(
        blank=True,
        verbose_name="dc:contributor",
        help_text="Person or organisation that made contributions to this concept<br>"
        "If more than one list all using a semicolon ;",
    )
    needs_review = models.BooleanField(null=True, help_text="Check if this concept needs to be reviewed")
    date_created = models.DateTimeField(editable=False, default=timezone.now, verbose_name="dct:created")
    date_modified = models.DateTimeField(editable=False, default=timezone.now, verbose_name="dct:modified")
    created_by = models.ForeignKey(
        User,
        related_name="skos_concept_created",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Concept"

    class MPTTMeta:
        order_insertion_by = ["pref_label"]
        parent_attr = "broader_concept"

    def get_vocabs_uri(self):
        return "{}{}".format("https://whatever", self.get_absolute_url)

    def save(self, *args, **kwargs):
        # if self.notation == "":
        #     temp_notation = slugify(self.pref_label, allow_unicode=True)
        #     concepts = len(SkosConcept.objects.filter(notation=temp_notation))
        #     if concepts < 1:
        #         self.notation = temp_notation
        #     else:
        #         self.notation = "{}-{}".format(temp_notation, concepts)
        # else:
        #     pass

        if not self.id:
            self.date_created = timezone.now()
        self.date_modified = timezone.now()
        super(SkosConcept, self).save(*args, **kwargs)

    def create_uri(self):
        mcs = self.scheme.identifier
        if mcs.endswith(VOCABS_SEPARATOR):
            pass
        else:
            mcs = f"{mcs}{VOCABS_SEPARATOR}"
        if self.legacy_id:
            item_uri = f"{self.legacy_id}"
        else:
            if notation_for_uri:
                tmp = slugify(self.notation, allow_unicode=False)
                item_uri = f"{mcs}concept__{tmp}__{self.id}"
            else:
                item_uri = f"{mcs}concept{self.id}"
        return item_uri

    # change for template tag
    def creator_as_list(self):
        return self.creator.split(";")

    def contributor_as_list(self):
        return self.contributor.split(";")

    def broad_match_as_list(self):
        return self.broad_match.split(",")

    def related_as_list(self):
        return self.related.split(",")

    def narrow_match_as_list(self):
        return self.narrow_match.split(",")

    def exact_match_as_list(self):
        return self.exact_match.split(",")

    def related_match_as_list(self):
        return self.related_match.split(",")

    def close_match_as_list(self):
        return self.close_match.split(",")

    @classmethod
    def get_listview_url(self):
        return reverse("vocabs:browse_vocabs")

    @classmethod
    def get_createview_url(self):
        return reverse("vocabs:skosconcept_create")

    def get_absolute_url(self):
        return reverse("vocabs:skosconcept_detail", kwargs={"pk": self.id})

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
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=500, verbose_name="label", help_text="Other label for this concept")
    language = models.CharField(
        max_length=53,
        verbose_name="language",
        help_text="Language of label given above",
    )
    label_type = models.CharField(
        choices=LABEL_TYPES,
        verbose_name="label type",
        default="altLabel",
        max_length=12,
        help_text="Choose label type",
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
        on_delete=models.CASCADE,
    )
    name = models.TextField(
        verbose_name="documentary note",
        help_text="Provide some information about this concept",
    )
    language = models.CharField(max_length=53, verbose_name="language", help_text="Language of note given above")
    note_type = models.CharField(
        choices=NOTE_TYPES,
        verbose_name="note type",
        default="note",
        max_length=15,
        help_text="Choose note type",
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
        on_delete=models.CASCADE,
    )
    name = models.TextField(verbose_name="dc:source", help_text="Verbal description of the concept's source")
    language = models.CharField(
        max_length=53,
        verbose_name="language",
        help_text="Language of source given above",
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
    assign_perm("delete_skosconceptscheme", instance.created_by, instance)
    assign_perm("change_skosconceptscheme", instance.created_by, instance)
    assign_perm("view_skosconceptscheme", instance.created_by, instance)


@receiver(post_save, sender=SkosCollection, dispatch_uid="create_perms_collection_created_by")
def create_perms_collection_created_by(sender, instance, **kwargs):
    assign_perm("delete_skoscollection", instance.created_by, instance)
    assign_perm("change_skoscollection", instance.created_by, instance)
    assign_perm("view_skoscollection", instance.created_by, instance)
    for curator in instance.scheme.curator.all():
        assign_perm("delete_skoscollection", curator, instance)
        assign_perm("change_skoscollection", curator, instance)
        assign_perm("view_skoscollection", curator, instance)
        if curator is not instance.scheme.created_by:
            assign_perm("delete_skoscollection", instance.scheme.created_by, instance)
            assign_perm("change_skoscollection", instance.scheme.created_by, instance)
            assign_perm("view_skoscollection", instance.scheme.created_by, instance)


@receiver(post_save, sender=SkosConcept, dispatch_uid="create_perms_concept_created_by")
def create_perms_concept_created_by(sender, instance, **kwargs):
    assign_perm("delete_skosconcept", instance.created_by, instance)
    assign_perm("change_skosconcept", instance.created_by, instance)
    assign_perm("view_skosconcept", instance.created_by, instance)
    for curator in instance.scheme.curator.all():
        assign_perm("delete_skosconcept", curator, instance)
        assign_perm("change_skosconcept", curator, instance)
        assign_perm("view_skosconcept", curator, instance)
        if curator is not instance.scheme.created_by:
            assign_perm("delete_skosconcept", instance.scheme.created_by, instance)
            assign_perm("change_skosconcept", instance.scheme.created_by, instance)
            assign_perm("view_skosconcept", instance.scheme.created_by, instance)


############### Adding new curator (user) to a Concept Scheme ###################
############### Only user who created a Concept Scheme can do it ################


@receiver(
    m2m_changed,
    sender=SkosConceptScheme.curator.through,
    dispatch_uid="create_perms_curator",
)
def create_perms_curator(sender, instance, **kwargs):
    if kwargs["action"] == "pre_add":
        for curator in User.objects.filter(pk__in=kwargs["pk_set"]):
            assign_perm("view_skosconceptscheme", curator, instance)
            assign_perm("change_skosconceptscheme", curator, instance)
            assign_perm("delete_skosconceptscheme", curator, instance)
            for obj in instance.has_collections.all():
                assign_perm("view_" + obj.__class__.__name__.lower(), curator, obj)
                assign_perm("change_" + obj.__class__.__name__.lower(), curator, obj)
                assign_perm("delete_" + obj.__class__.__name__.lower(), curator, obj)
            for obj in instance.has_concepts.all():
                assign_perm("view_" + obj.__class__.__name__.lower(), curator, obj)
                assign_perm("change_" + obj.__class__.__name__.lower(), curator, obj)
                assign_perm("delete_" + obj.__class__.__name__.lower(), curator, obj)
    elif kwargs["action"] == "post_remove":
        for curator in User.objects.filter(pk__in=kwargs["pk_set"]):
            remove_perm("view_skosconceptscheme", curator, instance)
            remove_perm("change_skosconceptscheme", curator, instance)
            # if user removed from the curators list
            # he/she won't be able to access the objects he/she created within this CS
            for obj in instance.has_collections.all():
                remove_perm("view_" + obj.__class__.__name__.lower(), curator, obj)
                remove_perm("change_" + obj.__class__.__name__.lower(), curator, obj)
                remove_perm("delete_" + obj.__class__.__name__.lower(), curator, obj)
            for obj in instance.has_concepts.all():
                remove_perm("view_" + obj.__class__.__name__.lower(), curator, obj)
                remove_perm("change_" + obj.__class__.__name__.lower(), curator, obj)
                remove_perm("delete_" + obj.__class__.__name__.lower(), curator, obj)
