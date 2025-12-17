from django.db.models import manager

from .queryset import SoftDeletionQueryset


class SoftDeletionManager(manager.Manager):
    def get_queryset(self):

        return SoftDeletionQueryset(self.model, using=self._db).filter(
            deleted_at__isnull=True
        )