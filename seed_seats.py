import os
import django

# Setup Django if this script is run completely standalone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

# Import Django models after Django is set up to avoid module-level import issues

def generate_seats():
    from users.models import Show, Seat
    shows = Show.objects.all()
    
    if not shows.exists():
        print("No shows found. Please create a show first.")
        return

    # Loop through every single show in the database
    for show in shows:
        # Only generate seats if this show doesn't have any yet
        if not Seat.objects.filter(show=show).exists():
            seats_created = 0
            # Generate 100 seats (10 rows, A through J)
            for row in range(10):
                row_letter = chr(65 + row) # A, B, C, etc.
                for num in range(1, 11):
                    seat_number = f"{row_letter}{num}"
                    Seat.objects.create(show=show, seat_number=seat_number, status=0)
                    seats_created += 1
            
            print(f"Success! {seats_created} seats added to: {show.movie.title}")
        else:
            print(f"Seats already exist for: {show.movie.title}")

if __name__ == '__main__':
    generate_seats()