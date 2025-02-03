from functools import cached_property
from typing import Dict
import json

from core.models import TrackerMixin
from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from data_collection.constants import (
    CSV_DATA_TYPE, JSON_DATA_TYPE, STATUS_COMPLETED, STATUS_IN_PROGRESS, STR_DATA_TYPE, RESUME_DATA_TYPE, STATUS_PENDING, STATUS_ERROR,
    GLOBAL_TECH_ATS
)

class Statuses(models.TextChoices):
    PENDING = 'pending', _(STATUS_PENDING)
    ERROR = 'error', _(STATUS_ERROR)
    PROCESSING = 'in_progress', _(STATUS_IN_PROGRESS)
    PROCESSED = 'completed', _(STATUS_COMPLETED)


class DataRequest(TrackerMixin):
    raw_data: QuerySet['RawData']
    class Services(models.TextChoices):
        GLOBAL_TECH_ATS = 'global_tech_ats', _(GLOBAL_TECH_ATS)

    status = models.CharField(max_length=16, choices=Statuses.choices, null=False, blank=False, default=Statuses.PENDING)
    service = models.CharField(max_length=32, choices=Services.choices, null=False, blank=False, default=Services.GLOBAL_TECH_ATS)


class RawData(TrackerMixin):

    class DataFormats(models.TextChoices):
        CSV = 'csv', _(CSV_DATA_TYPE)
        JSON = 'json', _(JSON_DATA_TYPE)
        STR = 'str', _(STR_DATA_TYPE)

    class DataTypes(models.TextChoices):
        RESUME = 'resume', _(RESUME_DATA_TYPE)

    data_format = models.CharField(max_length=8, choices=DataFormats.choices, null=False, blank=False, default=DataFormats.JSON)
    data_type = models.CharField(max_length=8, choices=DataTypes.choices, null=False, blank=False, default=DataTypes.RESUME)
    raw_data = models.TextField(null=False, blank=False)
    status = models.CharField(max_length=16, choices=Statuses.choices, null=False, blank=False, default=Statuses.PENDING)
    data_request = models.ForeignKey(DataRequest, on_delete=models.CASCADE, related_name='raw_data')

    @cached_property
    def parsed_data(self) -> Dict:
        if self.data_format == JSON_DATA_TYPE:
            return json.loads(self.raw_data)
        raise NotImplementedError(f'data format {self.data_format} is not implemented')
