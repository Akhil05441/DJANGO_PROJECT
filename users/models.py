from django.db import models
from django.contrib.auth.models import User
class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=255)
    
    # ManyToMany fields replacing the old string fields for scalable filtering
    genres = models.ManyToManyField(Genre, related_name='movies')
    languages = models.ManyToManyField(Language, related_name='movies')
    
    duration_minutes = models.IntegerField(default=120)
    
    # Indexed fields to prevent full-table scans during sorting
    release_date = models.DateField(db_index=True, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, db_index=True, default=0.0)

    class Meta:
        # Composite index for faster title searches
        indexes = [
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title

class Show(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='shows')
    screen_name = models.CharField(max_length=50)
    start_time = models.DateTimeField()

    def __str__(self):
        return f"{self.movie.title} - {self.screen_name}"

class Seat(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    
    # 1. Define the exact choices the internship requested
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('LOCKED', 'Locked'),
        ('BOOKED', 'Booked'),
    ]

    # 2. Add the status field with a default of 'AVAILABLE'
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='AVAILABLE'
    )

    # 3. Add the locked_until field (must allow null/blank for when a seat is free)
    locked_until = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.show.movie.title} - {self.seat_number}"
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='bookings')
    seats = models.ManyToManyField('Seat', related_name='bookings')
    
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Crucial for Task 4 (Payment Gateway) & Task 5 (Concurrency)
    payment_status = models.CharField(max_length=20, default='Pending') # Pending, Completed, Failed
    # Added unique=True to satisfy the idempotency and duplicate-prevention requirement
    payment_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    
    booking_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} by {self.user.username}"