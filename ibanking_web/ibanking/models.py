import json
from django.db import models
from django.utils import timezone
# Create your models here.


class ScrapyItem(models.Model):
    unique_id = models.CharField(max_length=200, null=True)
    data = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.unique_id

    def to_dict(self):
        data = {
            'data': json.loads(self.data),
            'unique_id': self.unique_id,
            'timestamp': self.timestamp
        }
        return data
