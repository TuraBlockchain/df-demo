from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models import UniqueConstraint


from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone

class CardInfo(models.Model):
    username = models.CharField(max_length=150)
    bio = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=255, primary_key=True)
    profile_image = models.ImageField(upload_to='avatars/', null=True, blank=True)
    link = models.CharField(max_length=255)
    time = models.DateTimeField(null=True, blank=True, default=None)  # 用于存储创建时间
    date = models.DateField(null=True, blank=True, default=None)  # 用于存储创建日期

    class Meta:
        constraints = [
            UniqueConstraint(fields=['username', 'address'], name='unique_username_address')
        ]

    def save(self, *args, **kwargs):
        if not self.time:
            self.time = timezone.now()
        if not self.date:
            self.date = timezone.now().date()
        super().save(*args, **kwargs)



class CardKV(models.Model):
    key = models.CharField(max_length=255, unique=True)
    data = JSONField()

    def __str__(self):
        return f"{self.key}: {self.data}"

