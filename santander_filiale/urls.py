from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static  # Importa la funzione static

urlpatterns = [
    # Rotta per il pannello di amministrazione
    path('admin/', admin.site.urls),

    # Includi tutte le URL dell'app 'filiale' a partire dalla radice del sito
    path('', include('filiale.urls')),
]

# Servire i file media (immagini caricate) SOLO in ambiente di sviluppo (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)