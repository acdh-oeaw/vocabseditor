import os
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.functional import cached_property
from django.core.exceptions import ValidationError


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


def validate_only_one_instance(obj):
    # limit number of created instances https://stackoverflow.com/a/6436008/7101197
    model = obj.__class__
    if (model.objects.count() > 0 and
            obj.id != model.objects.get().id):
        raise ValidationError("Can only create 1 %s instance" % model.__name__)


class Metadata(models.Model):
    """Class to collect metadata for Main Concept Scheme"""

    title = models.CharField(max_length=300, blank=True)
    indentifier = models.URLField(
        blank=True, default=DEFAULT_NAMESPACE, help_text="URI")
    description = models.TextField(
        blank=True, help_text="Description of current vocabulary")
    description_lang = models.CharField(
        max_length=3, blank=True, default=DEFAULT_LANG,
        verbose_name="Description language")
    language = models.TextField(
        blank=True,
        help_text="If more than one list all using a semicolon ;")
    version = models.CharField(
        max_length=300, blank=True,
        help_text="Current version")
    creator = models.TextField(
        blank=True,
        help_text="A Person or Organisation responsible for making the vocabulary<br>"
        "If more than one list all using a semicolon ;")
    contributor = models.TextField(
        blank=True,
        help_text="A Person or Organisation that made contributions to the vocabulary<br>"
        "If more than one list all using a semicolon ;")
    subject = models.TextField(
        blank=True,
        help_text="The subject of the vocabulary<br>"
        "If more than one list all using a semicolon ;")
    owner = models.CharField(
        max_length=300, blank=True,
        help_text="A Person or Organisation that own rights for the vocabulary")
    license = models.CharField(
        max_length=300, blank=True,
        help_text="A license applied to the vocabulary"
        )
    date_created = models.DateTimeField(
        editable=False, default=timezone.now)
    date_modified = models.DateTimeField(
        editable=False, default=timezone.now)
    date_issued = models.DateField(
        blank=True, null=True,
        help_text="Date of official resource publication<br>YYYY-MM-DD")
    relation = models.URLField(
        blank=True,
        help_text="e.g. in case of relation to a project, add link to a project website")

    def save(self, *args, **kwargs):
        if not self.id:
            self.date_created = timezone.now()
        self.date_modified = timezone.now()
        return super(Metadata, self).save(*args, **kwargs)

    @classmethod
    def get_listview_url(self):
        return reverse('vocabs:metadata')

    def __str__(self):
        return "{}".format(self.title)

    def get_absolute_url(self):
        return reverse('vocabs:metadata_detail', kwargs={'pk': self.id})

    def subject_as_list(self):
        return self.subject.split(';')

    def language_as_list(self):
        return self.language.split(';')

    def creator_as_list(self):
        return self.creator.split(';')

    def contributor_as_list(self):
        return self.contributor.split(';')

    def clean(self):
        validate_only_one_instance(self)


class SkosNamespace(models.Model):
    namespace = models.URLField(blank=True, default=DEFAULT_NAMESPACE)
    prefix = models.CharField(max_length=50, blank=True, default=DEFAULT_PREFIX)

    def __str__(self):
        return "{}".format(self.prefix)


class SkosConceptScheme(models.Model):
    """
    A SKOS concept scheme can be viewed as an aggregation of one or more SKOS concepts.
    Semantic relationships (links) between those concepts
    may also be viewed as part of a concept scheme.

    Miles, Alistair, and Sean Bechhofer. "SKOS simple knowledge
    organization system reference. W3C recommendation (2009)."
    """
    dc_title = models.CharField(
        max_length=300, blank=True,
        verbose_name="dc:title")
    dc_title_lang = models.CharField(
        max_length=3, blank=True,
        verbose_name="dc:title language", default=DEFAULT_LANG)
    namespace = models.ForeignKey(
        SkosNamespace,
        blank=True, null=True,
        on_delete=models.SET_NULL
    )
    dc_creator = models.TextField(
        blank=True, verbose_name="dc:creator",
        help_text="If more than one list all using a semicolon ;")
    dc_description = models.TextField(
        blank=True, verbose_name="dc:description")
    dc_description_lang = models.CharField(
        max_length=3, blank=True,
        verbose_name="dc:description language", default=DEFAULT_LANG)
    legacy_id = models.CharField(
        max_length=200, blank=True)
    date_created = models.DateTimeField(
        editable=False, default=timezone.now)
    date_modified = models.DateTimeField(
        editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        if self.namespace is None:
            temp_namespace, _ = SkosNamespace.objects.get_or_create(
                namespace=DEFAULT_NAMESPACE, prefix=DEFAULT_PREFIX)
            temp_namespace.save()
            self.namespace = temp_namespace
        else:
            pass

        if not self.id:
            self.date_created = timezone.now()
        self.date_modified = timezone.now()

        super(SkosConceptScheme, self).save(*args, **kwargs)

    def dc_creator_as_list(self):
        return self.dc_creator.split(';')

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
        return "{}:{}".format(self.namespace, self.dc_title)


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
        max_length=300, blank=True, verbose_name="skos:prefLabel",
        help_text="Collection title or name"
    )
    label_lang = models.CharField(
        max_length=3, blank=True,
        default=DEFAULT_LANG,
        verbose_name="skos:prefLabel language"
    )
    creator = models.TextField(
        blank=True, verbose_name="dc:creator",
        help_text="A Person or Organisation that created a current collection<br>"
        "If more than one list all using a semicolon ;"
    )
    legacy_id = models.CharField(
        max_length=200, blank=True
    )
    # documentation properties
    skos_note = models.CharField(
        max_length=500, blank=True,
        verbose_name="skos:note",
        help_text="Provide some information about a collection"
    )
    skos_note_lang = models.CharField(
        max_length=3, blank=True, default=DEFAULT_LANG,
        verbose_name="skos:note language")
    skos_scopenote = models.TextField(
        blank=True, verbose_name="skos:scopeNote",
        help_text="Provide detailed description of the collection purpose")
    skos_scopenote_lang = models.CharField(
        max_length=3, blank=True,
        verbose_name="skos:scopeNote language", default=DEFAULT_LANG)
    skos_changenote = models.CharField(
        max_length=500, blank=True,
        verbose_name="skos:changeNote",
        help_text="Describe significant changes to a collection"
    )
    skos_editorialnote = models.CharField(
        max_length=500, blank=True,
        verbose_name="skos:editorialNote",
        help_text="Provide any administrative information, for the "
        "purposes of administration and maintenance. E.g. comments on "
        "reviewing this collection"
    )
    skos_example = models.CharField(
        max_length=500, blank=True,
        verbose_name="skos:example"
    )
    skos_historynote = models.CharField(
        max_length=500, blank=True,
        verbose_name="skos:historyNote",
        help_text="Describe significant changes to a collection over a time"
    )
    date_created = models.DateTimeField(
        editable=False, default=timezone.now
    )
    date_modified = models.DateTimeField(
        editable=False, default=timezone.now
    )

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
        return "{}".format(self.name)

    def creator_as_list(self):
        return self.creator.split(';')


class SkosLabel(models.Model):
    """
    SKOS lexical labels are the expressions that are used to refer to concepts in natural language.

    Antoine Isaac and Ed Summers. "SKOS Simple Knowledge Organization System Primer.
    W3C Working Group Note (2009)."
    """
    name = models.CharField(
        max_length=100, blank=True, help_text="The entities label or name.",
        verbose_name="Label")
    label_type = models.CharField(
        max_length=30, blank=True, choices=LABEL_TYPES, help_text="The type of the label.")
    isoCode = models.CharField(
        max_length=3, blank=True, help_text="The ISO 639-3 code for the label's language.")

    @classmethod
    def get_listview_url(self):
        return reverse('vocabs:browse_skoslabels')

    @classmethod
    def get_createview_url(self):
        return reverse('vocabs:skoslabel_create')

    def get_absolute_url(self):
        return reverse('vocabs:skoslabel_detail', kwargs={'pk': self.id})

    def get_next(self):
        next = SkosLabel.objects.filter(id__gt=self.id)
        if next:
            return next.first().id
        return False

    def get_prev(self):
        prev = SkosLabel.objects.filter(id__lt=self.id).order_by('-id')
        if prev:
            return prev.first().id
        return False

    def __str__(self):
        if self.label_type != "":
            return "{} @{} ({})".format(self.name, self.isoCode, self.label_type)
        else:
            return "{} @{}".format(self.name, self.isoCode)


class SkosConcept(models.Model):
    """
    A SKOS concept can be viewed as an idea or notion; a unit of thought.
    However, what constitutes a unit of thought is subjective,
    and this definition is meant to be suggestive, rather than restrictive.

    Miles, Alistair, and Sean Bechhofer. "SKOS simple knowledge
    organization system reference. W3C recommendation (2009)."
    """
    pref_label = models.CharField(
        max_length=300, blank=True,
        verbose_name="skos:prefLabel",
        help_text="Preferred label for a concept"
    )
    pref_label_lang = models.CharField(
        max_length=3, blank=True,
        verbose_name="skos:prefLabel language",
        help_text="Language code of preferred label according to ISO 639-3",
        default=DEFAULT_LANG
    )
    collection = models.ManyToManyField(
        SkosCollection, blank=True,
        verbose_name="member of skos:Collection",
        related_name="has_members",
    )
    scheme = models.ManyToManyField(
        SkosConceptScheme, blank=True,
        verbose_name="skos:ConceptScheme",
        related_name="has_concepts"
    )
    definition = models.TextField(
        blank=True, verbose_name="skos:definition",
        help_text="Provide a complete explanation of the intended meaning of a concept"
    )
    definition_lang = models.CharField(
        max_length=3, blank=True,
        verbose_name="skos:definition language",
        default=DEFAULT_LANG
    )
    other_label = models.ManyToManyField(
        SkosLabel, blank=True,
        help_text="select other labels that represent this concept"
    )
    notation = models.CharField(
        max_length=300, blank=True,
        verbose_name="skos:notation",
        help_text="A notation is a unique string used\
        to identify the concept in current vocabulary"
    )
    namespace = models.ForeignKey(
        SkosNamespace, blank=True, null=True,
        on_delete=models.SET_NULL
    )
    broader_concept = models.ForeignKey(
        'SkosConcept',
        verbose_name="Broader Term",
        blank=True, null=True, on_delete=models.SET_NULL,
        related_name="narrower_concepts",
        help_text="A concept with a broader meaning that a current concept inherits from"
    )
    top_concept = models.BooleanField(
        default=False,
        help_text="Is this concept a top concept of main concept scheme?"
    )
    same_as_external = models.TextField(
        blank=True,
        verbose_name="owl:sameAs",
        help_text="URL of an external Concept with the same meaning<br>"
        "If more than one list all using a semicolon ; ",
    )
    source_description = models.TextField(
        blank=True,
        verbose_name="Source",
        help_text="A verbose description of the concept's source"
    )
    skos_broader = models.ManyToManyField(
        'SkosConcept', blank=True, related_name="narrower",
        verbose_name="skos:broader",
        help_text="A concept with a broader meaning"
    )
    skos_narrower = models.ManyToManyField(
        'SkosConcept', blank=True, related_name="broader",
        verbose_name="skos:narrower",
        help_text="A concept with a narrower meaning"
    )
    skos_related = models.ManyToManyField(
        'SkosConcept', blank=True, related_name="related",
        verbose_name="skos:related",
        help_text="An associative relationship among two concepts"
    )
    skos_broadmatch = models.ManyToManyField(
        'SkosConcept', blank=True, related_name="narrowmatch",
        verbose_name="skos:broadMatch",
        help_text="A concept in an external ConceptSchema with a broader meaning"
    )
    skos_narrowmatch = models.ManyToManyField(
        'SkosConcept', blank=True, related_name="broadmatch",
        verbose_name="skos:narrowMatch",
        help_text="A concept in an external ConceptSchema with a narrower meaning"
    )
    skos_exactmatch = models.ManyToManyField(
        'SkosConcept', blank=True, related_name="exactmatch",
        verbose_name="skos:exactMatch",
        help_text="A concept in an external ConceptSchema "
        "that can be used interchangeably and has an exact same meaning"
    )
    skos_relatedmatch = models.ManyToManyField(
        'SkosConcept', blank=True, related_name="relatedmatch",
        verbose_name="skos:relatedMatch",
        help_text="A concept in an external ConceptSchema that has an associative "
        "relationship with a current concept"
    )
    skos_closematch = models.ManyToManyField(
        'SkosConcept', blank=True, related_name="closematch",
        verbose_name="skos:closeMatch",
        help_text="A concept in an external ConceptSchema that has a similar meaning"

    )
    legacy_id = models.CharField(max_length=200, blank=True)
    name_reverse = models.CharField(
        max_length=255,
        verbose_name="name reverse",
        help_text="Inverse relation like: \
        'is sub-class of' vs. 'is super-class of'.",
        blank=True
    )
    # documentation properties
    skos_note = models.CharField(
        max_length=500, blank=True,
        verbose_name="skos:note",
        help_text="Provide some partial information about the meaning of a concept"
    )
    skos_note_lang = models.CharField(
        max_length=3, blank=True,
        default=DEFAULT_LANG, verbose_name="skos:note language"
    )
    skos_scopenote = models.TextField(
        blank=True, verbose_name="skos:scopeNote",
        help_text="Provide more detailed information of the intended meaning of a concept"
    )
    skos_scopenote_lang = models.CharField(
        max_length=3, blank=True,
        default=DEFAULT_LANG, verbose_name="skos:scopeNote language"
    )
    skos_changenote = models.CharField(
        max_length=500, blank=True,
        verbose_name="skos:changeNote",
        help_text="Document any changes to a concept"
    )
    skos_editorialnote = models.CharField(
        max_length=500, blank=True,
        verbose_name="skos:editorialNote",
        help_text="Provide any administrative information, for the "
        "purposes of administration and maintenance. E.g. comments on "
        "reviewing this concept"
    )
    skos_example = models.CharField(
        max_length=500, blank=True,
        verbose_name="skos:example",
        help_text="Provide an example of a concept usage"
    )
    skos_historynote = models.CharField(
        max_length=500, blank=True,
        verbose_name="skos:historyNote",
        help_text="Describe significant changes to the meaning of a concept over a time"
    )
    dc_creator = models.TextField(
        blank=True, verbose_name="dc:creator",
        help_text="A Person or Organisation that created a current concept<br>"
        "If more than one list all using a semicolon ;",

    )
    date_created = models.DateTimeField(
        editable=False, default=timezone.now,
        verbose_name="dct:created"
    )
    date_modified = models.DateTimeField(
        editable=False, default=timezone.now,
        verbose_name="dct:modified"
    )

    def get_broader(self):
        broader = self.skos_broader.all()
        broader_reverse = SkosConcept.objects.filter(skos_narrower=self)
        all_broader = set(list(broader)+list(broader_reverse))
        return all_broader

    def get_narrower(self):
        narrower = self.skos_narrower.all()
        narrower_reverse = SkosConcept.objects.filter(skos_broader=self)
        all_narrower = set(list(narrower)+list(narrower_reverse))
        return all_narrower

    def get_vocabs_uri(self):
        return "{}{}".format("https://whatever", self.get_absolute_url)

    @property
    def all_schemes(self):
        return ', '.join([x.dc_title for x in self.scheme.all()])

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

        if self.namespace is None:
            temp_namespace, _ = SkosNamespace.objects.get_or_create(
                namespace=DEFAULT_NAMESPACE, prefix=DEFAULT_PREFIX)
            temp_namespace.save()
            self.namespace = temp_namespace
        else:
            pass

        if not self.id:
            self.date_created = timezone.now()
        self.date_modified = timezone.now()

        super(SkosConcept, self).save(*args, **kwargs)

    def dc_creator_as_list(self):
        return self.dc_creator.split(';')

    def same_as_external_as_list(self):
        return self.same_as_external.split(';')

    @cached_property
    def label(self):
        # 'borrowed from https://github.com/sennierer'
        d = self
        res = self.pref_label
        while d.broader_concept:
            res = d.broader_concept.pref_label + ' >> ' + res
            d = d.broader_concept
        return res

    @classmethod
    def get_listview_url(self):
        return reverse('vocabs:browse_vocabs')

    @classmethod
    def get_createview_url(self):
        return reverse('vocabs:skosconcept_create')

    def get_absolute_url(self):
        return reverse('vocabs:skosconcept_detail', kwargs={'pk': self.id})

    def get_next(self):
        next = SkosConcept.objects.filter(id__gt=self.id)
        if next:
            return next.first().id
        return False

    def get_prev(self):
        prev = SkosConcept.objects.filter(id__lt=self.id).order_by('-id')
        if prev:
            return prev.first().id
        return False

    def __str__(self):
        return self.pref_label


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

