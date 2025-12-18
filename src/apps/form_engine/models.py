from django.db import models
from django.conf import settings

from db.base import BaseModel
# Create your models here.


class FormMaster(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    form_id = models.CharField(max_length=24)

    class Meta:
        unique_together = ("user", "form_id")
    