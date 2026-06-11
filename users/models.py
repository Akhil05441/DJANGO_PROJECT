from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    duration_minutes = models.IntegerField()
    language = models.CharField(max_length=50)

    def __str__(self):
        return self.title

class Show(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='shows')
    screen_name = models.CharField(max_length=50, default="Screen 1")
    start_time = models.DateTimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2, default=150.00)

    def __str__(self):
        return f"{self.movie.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

class Seat(models.Model):
    STATUS_CHOICES = [
        (0, 'Available'),
        (1, 'Locked'),
        (2, 'Booked'),
    ]
    
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10) # e.g., A1, A2, B5
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    locked_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='locked_seats')
    locked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.seat_number} - {self.show}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    # Ensure this is exactly models.ManyToManyField(Seat) without any 'through' arguments
    seats = models.ManyToManyField(Seat, related_name='bookings')
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} by {self.user.username}"