from django.db import models

class Anime(models.Model):
    class Meta:
        app_label = 'core'
    title = models.CharField(max_length=255, unique=True)
    #  ... other fields