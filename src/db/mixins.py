from django.conf import settings
from django.db import models
from django.utils import timezone

from .manager import SoftDeletionManager

class TimeAuditModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserAuditModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(class)s_created_by",
        null=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(class)s_updated_by",
        null=True,
    )

    class Meta:
        abstract = True

class SoftDeleteModel(models.Model):
    """To soft delete records"""

    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeletionManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, soft=True, *args, **kwargs):
        if not soft:
            return super().delete(using=using, *args, **kwargs)

        self.deleted_at = timezone.now()
        self.save(using=using)
        return None

class AuditModel(TimeAuditModel, UserAuditModel, SoftDeleteModel):
    class Meta:
        abstract = True