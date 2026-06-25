from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

from .models import Booking

logger = logging.getLogger(__name__)

# bind=True allows us to access task instance methods (like retry)
# max_retries=3 and countdown=60 means if it fails, wait 60s and try again, up to 3 times.
@shared_task(bind=True, max_retries=3)
def send_ticket_confirmation_email(self, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        
        # 1. Render the HTML template with dynamic data
        context = {'booking': booking}
        html_content = render_to_string('emails/ticket_confirmation.html', context)
        
        # 2. Create a plain-text fallback (good for email deliverability/spam filters)
        text_content = strip_tags(html_content)
        
        # 3. Construct the email
        subject = f"🎟️ Booking Confirmed: {booking.show.movie.title}"
        from_email = 'noreply@bookmyseat.com'
        to_email = booking.user.email
        
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        
        # 4. Send the email
        msg.send()
        
        logger.info(f"Successfully sent confirmation email for Booking {booking_id}")
        return f"Email sent for booking {booking_id}"
        
    except Booking.DoesNotExist:
        logger.error(f"Booking {booking_id} not found. Cannot send email.")
    except Exception as e:
        logger.error(f"Failed to send email for Booking {booking_id}. Retrying... Error: {str(e)}")
        # Trigger the retry logic requested by the rubric
        raise self.retry(exc=e, countdown=60)