from django.urls import path
from . import views
from django.views.generic import TemplateView

# app_name è fondamentale per l'uso dei tag {% url 'nome_rotta' %}
app_name = 'filiale'

urlpatterns = [
    # Rotte pubbliche dell'app 'filiale'
    path('', views.home, name='home'),
    path('servizi/', views.servizi, name='servizi'),
    path('servizi/<int:pk>/', views.dettaglio_servizio, name='dettaglio_servizio'),
    path('chi-siamo/', views.chi_siamo, name='chi_siamo'),
    path('documentazione/', views.documentazione, name='documentazione'),
    path('richiedi-preventivo/', TemplateView.as_view(template_name='filiale/richiedi_preventivo.html'), name='richiedi_preventivo'),
    path('prenota-appuntamento/', TemplateView.as_view(template_name='filiale/prenota_appuntamento.html'), name='prenota_appuntamento'),
    path('contatti/', TemplateView.as_view(template_name='filiale/dove_siamo.html'), name='contatti'),
]