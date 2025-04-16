from django.db import models
from django.utils.text import slugify

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Anime(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    release_date = models.DateField(null=True, blank=True)
    genres = models.ManyToManyField(Genre)
    episodes = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, blank=True)
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True)
    trailer_url = models.URLField(blank=True)
    rating = models.FloatField(null=True, blank=True)
    studio = models.CharField(max_length=100, blank=True)
    director = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title