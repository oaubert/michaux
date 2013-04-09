from .models import Work
from haystack import indexes
from haystack import site

class WorkIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    tags = indexes.MultiValueField(null=True, faceted=True)
    status = indexes.CharField(model_attr='status', null=True, faceted=True)
    cote = indexes.IntegerField(model_attr='cote')
    creator = indexes.CharField(model_attr='creator', faceted=True)
    creation_date_start = indexes.IntegerField(model_attr='creation_date_start', faceted=True, null=True)
    creation_date_end = indexes.IntegerField(model_attr='creation_date_end', faceted=True, null=True)
    serie = indexes.CharField(model_attr='serie', faceted=True, null=True)
    technique = indexes.MultiValueField(faceted=True)
    support = indexes.CharField(model_attr='support', faceted=True)
    height = indexes.IntegerField(model_attr='height', faceted=True)
    width = indexes.IntegerField(model_attr='width', faceted=True)
    with_revision = indexes.BooleanField(null=True)
    with_image = indexes.BooleanField(null=True)
    single_technique = indexes.BooleanField(null=True)
    exhibition = indexes.MultiValueField(faceted=True)

    # Auto fields for completion
    serie_auto = indexes.EdgeNgramField(model_attr='serie')
    support_auto = indexes.EdgeNgramField(model_attr='support')
    technique_auto = indexes.EdgeNgramField(model_attr='technique')
    authentication_source_auto = indexes.EdgeNgramField(model_attr='authentication_source')

    def get_model(self):
        return Work

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(master__isnull=True)

    def prepare_tags(self, work):
        return [ unicode(t) for t in work.tags.all() ]

    def prepare_technique(self, work):
        return [ unicode(t) for t in work.techniques ]

    def prepare_exhibition(self, work):
        return [ ei.exhibition.abbreviation for ei in work.exhibitioninstance_set.all() ]

    def prepare_with_image(self, work):
        return work.image_set.count() > 0

    def prepare_with_revision(self, work):
        return not not work.revision

    def prepare_single_technique(self, work):
        #return (not ',' in work.technique)
        return len(work.techniques) == 1

    def get_updated_field(self):
        return "modified"

site.register(Work, WorkIndex)
