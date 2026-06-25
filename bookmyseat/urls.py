from django.contrib import admin
from django.urls import path, include
import debug_toolbar

urlpatterns = [
    # The admin panel route
    path('admin/', admin.site.urls),
    
    # This sends all homepage traffic to your users app
    path('', include('users.urls')), 
    
    # The debug toolbar path
    path('__debug__/', include(debug_toolbar.urls)),
]