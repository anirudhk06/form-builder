import uuid
from django.contrib.auth import get_user_model
from django.db import models

from .mixins import AuditModel

class BaseModel(AuditModel):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True, primary_key=True
    )

    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        from crum import get_current_user
        user = get_current_user()
        if user is None or user.is_anonymous:
            self.created_by = None
            self.updated_by = None
        else:
            if self._state.adding:
                self.created_by = user
                self.updated_by = None
            else:
                self.updated_by = user

        super(BaseModel, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.id)
