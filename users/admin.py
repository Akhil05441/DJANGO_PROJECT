from django.contrib import admin
from .models import Movie, Show, Seat, Booking, Genre, Language

# Register our new filter models
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    # Replaced 'genre' and 'language' with custom callable methods
    list_display = ('id', 'title', 'display_genres', 'display_languages', 'duration_minutes', 'release_date', 'rating')
    
    # Custom method to display ManyToMany fields as comma-separated text
    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])
    display_genres.short_description = 'Genres'

    def display_languages(self, obj):
        return ", ".join([lang.name for lang in obj.languages.all()])
    display_languages.short_description = 'Languages'

@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    # Removed 'price' since it is not in our current Show model
    list_display = ('id', 'movie', 'screen_name', 'start_time')

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    # Removed 'locked_by' since it is not in our current Seat model
    list_display = ('id', 'show', 'seat_number', 'status')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # Changed 'total_amount' -> 'total_price' & 'booked_at' -> 'booking_time'
    list_display = ('id', 'user', 'show', 'total_price', 'payment_status', 'booking_time')