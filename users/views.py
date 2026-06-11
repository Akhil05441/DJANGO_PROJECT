from django.shortcuts import render, get_object_or_404
from .models import Movie, Show

def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movie_list.html', {'movies': movies})
def show_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    # Reverted back to .shows.all()
    shows = movie.shows.all() 
    return render(request, 'show_list.html', {'movie': movie, 'shows': shows})

def seat_map(request, show_id):
    show = get_object_or_404(Show, id=show_id)
    seats = show.seats.all()
    return render(request, 'seat_map.html', {'show': show, 'seats': seats})