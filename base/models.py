from django.db import models
import uuid


class BaseModel(models.Model):
    uid = models.UUIDField(primary_key = True, editable = False, default = uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now_add = True)
    order = models.PositiveBigIntegerField(default = 0)

    class Meta:
        abstract = True