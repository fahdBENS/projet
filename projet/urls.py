# projet/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('suivi.urls')),  # Inclure les URLs de l'application 'suivi'
]
