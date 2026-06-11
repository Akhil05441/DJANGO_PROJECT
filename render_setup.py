import os
import django
from django.utils import timezone
from datetime import datetime


def main():
    # 1. Initialize Django before importing models
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
    django.setup()
    
    # 2. Imports can now safely happen
    from django.contrib.auth.models import User
    from users.models import Movie, Show
    from seed_seats import generate_seats  

    # 3. Automatically create the Superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser 'admin' created automatically.")

    # 4. Automatically create a default Movie and Show if none exist
    if not Movie.objects.exists():
        movie = Movie.objects.create(
            title="Render Live Movie", 
            genre="Action", 
            duration_minutes=120, 
            language="English"
        )
        
        # Creating a timezone-aware datetime to prevent log warnings
        naive_datetime = datetime.strptime("2026-06-15 18:00:00", "%Y-%m-%d %H:%M:%S")
        aware_datetime = timezone.make_aware(naive_datetime)
        
        Show.objects.create(
            movie=movie, 
            screen_name="Main Screen", 
            start_time=aware_datetime
        )
        print("Default Movie and Show created.")

    # 5. Generate seats (Keep it outside the IF block if it checks all shows dynamically)
    generate_seats()


if __name__ == '__main__':
    main()