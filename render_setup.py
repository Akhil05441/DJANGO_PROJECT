import os
import django
from django.utils import timezone
from datetime import datetime, timedelta

def main():
    # 1. Initialize Django before importing models
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
    django.setup()
    
    # 2. Imports can now safely happen
    from django.contrib.auth.models import User
    from users.models import Movie, Show, Genre, Language
    from seed_seats import generate_seats  

    # 3. Automatically create the Superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser 'admin' created automatically.")

    # 4. List of 6 movies to add to the platform
    movies_data = [
        {"title": "The Dark Knight", "genre": "Action", "duration_minutes": 152, "language": "English"},
        {"title": "Interstellar", "genre": "Sci-Fi", "duration_minutes": 169, "language": "English"},
        {"title": "Inception", "genre": "Action", "duration_minutes": 148, "language": "English"},
        {"title": "Avatar: The Way of Water", "genre": "Sci-Fi", "duration_minutes": 192, "language": "English"},
        {"title": "Spiderman: No Way Home", "genre": "Action", "duration_minutes": 148, "language": "English"},
        {"title": "The Avengers", "genre": "Action", "duration_minutes": 143, "language": "English"},
    ]

    base_time = datetime.strptime("2026-06-15 18:00:00", "%Y-%m-%d %H:%M:%S")

    # 5. Loop through and create movies and shows if they don't exist
    for index, data in enumerate(movies_data):
        if not Movie.objects.filter(title=data["title"]).exists():
            
            # Step A: Create the movie WITHOUT genre and language first
            movie = Movie.objects.create(
                title=data["title"], 
                duration_minutes=data["duration_minutes"]
            )
            
            # Step B: Get or create the Genre and Language objects in their own tables
            genre_obj, _ = Genre.objects.get_or_create(name=data["genre"])
            lang_obj, _ = Language.objects.get_or_create(name=data["language"])
            
            # Step C: Link them to the movie using the ManyToMany .add() method
            movie.genres.add(genre_obj)
            movie.languages.add(lang_obj)
            
            # Stagger show times by 2 hours
            show_time = base_time + timedelta(hours=index * 2)
            aware_datetime = timezone.make_aware(show_time)
            
            Show.objects.create(
                movie=movie, 
                screen_name=f"Audi { (index % 3) + 1 }", 
                start_time=aware_datetime
            )
            print(f"Created movie and show for: {data['title']}")

    # 6. Run seat generation to make sure all newly created shows have seats ready
    generate_seats()
    print("Seat verification and generation completed.")

if __name__ == '__main__':
    main()