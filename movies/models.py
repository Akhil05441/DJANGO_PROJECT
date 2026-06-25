from django.db import models

class Genre(models.Model):
    # unique=True automatically creates a high-speed B-Tree index in the database
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=255)
    genres = models.ManyToManyField(Genre, related_name='movies')
    languages = models.ManyToManyField(Language, related_name='movies')
    
    # db_index=True forces the database to keep a sorted list of these dates.
    # When a user sorts by "Newest", the database doesn't have to scan all 5,000 rows.
    release_date = models.DateField(db_index=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, db_index=True, default=0.0)

    class Meta:
        # A composite index if users frequently search by title
        indexes = [
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title