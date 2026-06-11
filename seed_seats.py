import os
import django

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()


def generate_seats():
    from users.models import Show, Seat
    # Grab the very first show in the database
    show = Show.objects.first()
    
    if not show:
        print("Error: Please add at least one Show in the admin panel first!")
        return

    # Create a list of 100 seats (A1 to J10) using a short list comprehension
    # chr(65) is 'A', chr(66) is 'B', etc.
    seats_to_create = [
        Seat(show=show, seat_number=f"{chr(65+row)}{col}") 
        for row in range(10) for col in range(1, 11)
    ]

    # Bulk create pushes them to the database in a single efficient query
    Seat.objects.bulk_create(seats_to_create)
    print(f"Success! {len(seats_to_create)} seats added to: {show}")

if __name__ == '__main__':
    generate_seats()