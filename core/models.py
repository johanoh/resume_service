from typing import Any

from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()


class TrackerMixin(models.Model):
    id: int
    created_at: models.DateTimeField = models.DateTimeField(default=now, editable=False)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
