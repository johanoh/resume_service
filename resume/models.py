from core.models import TrackerMixin

from django.contrib.postgres.fields import ArrayField
from django.db import models

from data_collection.models import RawData


class Resume(TrackerMixin):
    external_id = models.CharField(max_length=128, blank=False, null=False, unique=True)
    skills = ArrayField(
        base_field=models.CharField(max_length=128, blank=False, null=False)
    )
    work_experiences = ArrayField(
        base_field=models.CharField(max_length=128, blank=False, null=False)
    )
    raw_data = models.ForeignKey(RawData, on_delete=models.CASCADE)
