from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Movie, Show, Genre, Language  # Added Language model if you have it
from django.http import HttpResponse
from .tasks import send_ticket_confirmation_email
from .models import Booking
import json
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Seat # Make sure Seat is imported at the top
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Sum, F
from django.db.models.functions import ExtractHour
from django.core.cache import cache
from django.contrib.admin.views.decorators import staff_member_required


def movie_list(request):
    # 1. Fetch baseline filter options for the sidebar checkboxes
    all_genres = Genre.objects.all()
    all_languages = Language.objects.all()

    # 2. Capture parameters from the URL query string
    selected_genres = request.GET.getlist('genres')
    selected_languages = request.GET.getlist('languages')
    sort_by = request.GET.get('sort', '-release_date')  # Default to newest movies

    # 3. Optimized Base Queryset (Prevents N+1 Query Problem via prefetch_related)
    movies_queryset = Movie.objects.prefetch_related('genres', 'languages').all()

    # 4. Server-Side Filtering (Utilizes database indexes automatically)
    if selected_genres:
        movies_queryset = movies_queryset.filter(genres__name__in=selected_genres)
    if selected_languages:
        movies_queryset = movies_queryset.filter(languages__name__in=selected_languages)

    # 5. Server-Side Sorting on Indexed Fields
    if sort_by in ['release_date', '-release_date', 'rating', '-rating']:
        movies_queryset = movies_queryset.order_by(sort_by)

    # Prevent duplicate results due to multi-select ManyToMany intersections
    movies_queryset = movies_queryset.distinct()

    # 6. DYNAMIC FILTER COUNTS: Compute exact genre counts based on the CURRENT search results
    dynamic_genre_counts = Genre.objects.filter(movies__in=movies_queryset).annotate(
        available_count=Count('movies')
    ).values('name', 'available_count')
    
    # Transform into a quick-lookup dictionary: {'Action': 5, 'Sci-Fi': 2}
    genre_counts_dict = {item['name']: item['available_count'] for item in dynamic_genre_counts}

    # 7. Pagination (12 movies per page to optimize load speed and prevent full scans)
    paginator = Paginator(movies_queryset, 12)
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 8. Define the Context Data Structure for the template
    context = {
        'movies': page_obj,               # This is now a Paginator page object instead of a raw list
        'all_genres': all_genres,
        'all_languages': all_languages,
        'selected_genres': selected_genres,
        'selected_languages': selected_languages,
        'genre_counts': genre_counts_dict,
        'current_sort': sort_by,
    }

    # Optional AJAX handling: if user filters via JS, return a partial HTML grid instead of reloading the page
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('partials/movie_grid.html', context, request=request)
        return JsonResponse({'html': html, 'has_next': page_obj.has_next()})

    return render(request, 'movie_list.html', context)


def show_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    shows = movie.shows.all() 
    return render(request, 'show_list.html', {'movie': movie, 'shows': shows})


def seat_map(request, show_id):
    show = get_object_or_404(Show, id=show_id)
    seats = show.seats.all()
    return render(request, 'seat_map.html', {'show': show, 'seats': seats})

def test_email_task(request):
    # Grab the first available booking in your database to test with
    booking = Booking.objects.first()
    
    if booking:
        # THE MAGIC LINE: .delay() sends it to the Celery queue in the background!
        send_ticket_confirmation_email.delay(booking.id)
        
        return HttpResponse(f"✅ Success! Task sent to Celery for Booking ID: {booking.id}. Check your Celery terminal!")
    else:
        return HttpResponse("⚠️ No bookings found in the database. Go to the Admin panel and create a dummy booking first.")


# REQUIREMENT 5: Concurrency-Safe Seat Reservation
def lock_seat_api(request):
    if request.method == 'POST':
        # Assuming the frontend sends a JSON payload like {'seat_id': 12}
        try:
            data = json.loads(request.body)
            seat_id = data.get('seat_id')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        # transaction.atomic() + select_for_update() is the exact answer 
        # to the "prevent double booking" requirement.
        with transaction.atomic():
            try:
                # Lock the specific row in the database so no other user can touch it
                seat = Seat.objects.select_for_update().get(id=seat_id)
            except Seat.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Seat not found'}, status=404)

            # Check if it is still available
            if seat.status == 'AVAILABLE':
                seat.status = 'LOCKED'
                seat.locked_until = timezone.now() + timedelta(minutes=2)
                seat.save()
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Seat locked for 2 minutes. Proceed to payment.'
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'error': 'Too late! Another user just grabbed this seat.'
                }, status=409)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        # 1. Verify Signature (Crucial Requirement!)
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature (Prevents replay attacks/fraud)
        return HttpResponse(status=400)

    # 2. Handle the Event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        transaction_id = payment_intent['id']

        try:
            # Idempotency check happens naturally here. If this payment_id already
            # exists in a Completed state, we don't process it again.
            booking = Booking.objects.get(payment_id=transaction_id)
            
            if booking.payment_status != 'Completed':
                booking.payment_status = 'Completed'
                booking.save()

                # Mark all seats in this booking as permanently 'BOOKED'
                for seat in booking.seats.all():
                    seat.status = 'BOOKED'
                    seat.save()

                # TRIGGER EMAIL (Requirement 2 integration)
                send_ticket_confirmation_email.delay(booking.id)

        except Booking.DoesNotExist:
            print("Webhook received for unknown booking")

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        transaction_id = payment_intent['id']

        try:
            booking = Booking.objects.get(payment_id=transaction_id)
            booking.payment_status = 'Failed'
            booking.save()

            # Handle Partial Failure / Cancellation: Free up the seats immediately
            for seat in booking.seats.all():
                seat.status = 'AVAILABLE'
                seat.locked_until = None
                seat.save()
        except Booking.DoesNotExist:
            pass

    return HttpResponse(status=200)


# REQUIREMENT 6: Role-Based Authentication & Privilege Escalation Prevention
# @staff_member_required ensures ONLY superusers/admins can access this view.
@staff_member_required
def admin_analytics_dashboard(request):
    
    # REQUIREMENT 6: Caching Mechanisms (Prevent performance degradation)
    # We check if 'admin_dashboard_data' exists in the cache. 
    dashboard_data = cache.get('admin_dashboard_data')

    if not dashboard_data:
        # REQUIREMENT 6: Database-Level Aggregation (NO Python loops, highly optimized)
        
        # 1. Total Revenue
        total_revenue = Booking.objects.filter(payment_status='Completed').aggregate(
            total=Sum('total_price')
        )['total'] or 0.00

        # 2. Most Popular Movies (Annotate groups by movie and counts bookings)
        popular_movies = Movie.objects.annotate(
            total_bookings=Count('shows__bookings')
        ).order_by('-total_bookings')[:5]

        # 3. Peak Booking Hours (Extracts the hour from the DateTime field)
        peak_hours = Booking.objects.annotate(
            hour=ExtractHour('booking_time')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        # 4. Cancellation Rate
        total_bookings = Booking.objects.count()
        failed_bookings = Booking.objects.filter(payment_status='Failed').count()
        cancellation_rate = (failed_bookings / total_bookings * 100) if total_bookings > 0 else 0.0

        # Store calculated data in a dictionary
        dashboard_data = {
            'total_revenue': total_revenue,
            'popular_movies': popular_movies,
            'peak_hours': peak_hours,
            'cancellation_rate': round(cancellation_rate, 2),
        }

        # Save to cache for 15 minutes (900 seconds). 
        # For the next 15 mins, the database won't be queried at all.
        cache.set('admin_dashboard_data', dashboard_data, timeout=900)

    return render(request, 'admin_dashboard.html', {'data': dashboard_data})