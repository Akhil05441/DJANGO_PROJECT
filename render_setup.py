import os
import django


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
    django.setup()
    from django.contrib.auth.models import User
    from users.models import Movie, Show
    from seed_seats import generate_seats  # Imports the script we wrote earlier

    # 1. Automatically create the Superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser 'admin' created automatically.")

    # 2. Automatically create a default Movie and Show if none exist
    if not Movie.objects.exists():
        movie = Movie.objects.create(title="Render Live Movie", genre="Action", duration_minutes=120, language="English")
        Show.objects.create(movie=movie, screen_name="Main Screen", start_time="2026-06-15 18:00:00")
        print("Default Movie and Show created.")

        # 3. Generate the seats for this new show
        generate_seats()


if __name__ == '__main__':
    main()