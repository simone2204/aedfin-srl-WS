from django.urls import path
from . import views

# app_name è fondamentale per l'uso dei tag {% url 'nome_rotta' %}
app_name = 'filiale'

urlpatterns = [
    # Rotte pubbliche dell'app 'filiale'
    path('', views.home, name='home'),
    path('servizi/', views.servizi, name='servizi'),
    path('servizi/<int:pk>/', views.dettaglio_servizio, name='dettaglio_servizio'),
    path('chi-siamo/', views.chi_siamo, name='chi_siamo'),
    path('contatti/', views.contatti, name='contatti'),
    path('documentazione/', views.documentazione, name='documentazione'),
    path('richiedi-preventivo/', views.richiedi_preventivo, name='richiedi_preventivo'),
    path('prenota-appuntamento/', views.prenota_appuntamento, name='prenota_appuntamento'),
]