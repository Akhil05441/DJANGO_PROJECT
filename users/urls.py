from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('movie/<int:movie_id>/', views.show_list, name='show_list'),
    path('show/<int:show_id>/', views.seat_map, name='seat_map'),
    path('api/lock-seat/', views.lock_seat_api, name='lock_seat'),
    # Add this temporary test route
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('admin/analytics/', views.admin_analytics_dashboard, name='admin_analytics'),
    path('test-email/', views.test_email_task, name='test_email'),
]