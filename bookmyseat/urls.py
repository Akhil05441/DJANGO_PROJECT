from django.contrib import admin
from django.urls import path, include
import debug_toolbar
from users import views
urlpatterns = [
    # The admin panel route
    path('admin/analytics/', views.admin_analytics_dashboard, name='admin_analytics'),
    path('admin/', admin.site.urls),
    
    # This sends all homepage traffic to your users app
    path('', include('users.urls')), 
    
    # The debug toolbar path
    path('__debug__/', include(debug_toolbar.urls)),
]