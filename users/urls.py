from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('movie/<int:movie_id>/', views.show_list, name='show_list'),
    path('show/<int:show_id>/', views.seat_map, name='seat_map'),
]