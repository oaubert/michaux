from .models import Work
from haystack import indexes
from haystack import site

class WorkIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    tags = indexes.MultiValueField(null=True, faceted=True)
    creator = indexes.CharField(model_attr='creator', faceted=True)
    creation_date_start = indexes.IntegerField(model_attr='creation_date_start', faceted=True, null=True)
    creation_date_end = indexes.IntegerField(model_attr='creation_date_end', faceted=True, null=True)
    serie = indexes.CharField(model_attr='serie', faceted=True, null=True)
    medium = indexes.CharField(model_attr='medium', faceted=True)
    support = indexes.CharField(model_attr='support', faceted=True)
    height = indexes.IntegerField(model_attr='height', faceted=True)
    width = indexes.IntegerField(model_attr='width', faceted=True)

    def get_model(self):
        return Work

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(master__isnull=True)

    def prepare_tags(self, work):
        return [ unicode(t) for t in work.tags.all() ]

    def get_updated_field(self):
        return "modified"

site.register(Work, WorkIndex)
