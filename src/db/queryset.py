from django.db import models
from django.utils import timezone


class SoftDeletionQueryset(models.QuerySet):
    def delete(self, soft=True):
        if soft:
            return self.update(deleted_at=timezone.now())

        return super().delete()