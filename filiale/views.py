from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from .models import Filiale, TipoPrestito, Testimonial, RichiestaContatto, DocumentoInfo, Appuntamento
from .forms import RichiestaContattoForm, DatiClienteAppuntamentoForm
from django.utils import timezone
from datetime import timedelta, time, date
from django.db.models import Q
import calendar
import locale

def home(request):
    """Homepage con presentazione filiale e servizi principali"""
    filiale = Filiale.objects.first()
    # Rimuovi questa riga, non è più necessaria:
    # servizi_in_evidenza = TipoPrestito.objects.filter(attivo=True)[:3]
    testimonial = Testimonial.objects.filter(approvato=True)[:3]

    context = {
        'filiale': filiale,
        # Rimuovi 'servizi' dal contesto:
        # 'servizi': servizi_in_evidenza,
        'testimonial': testimonial,
    }
    return render(request, 'filiale/home.html', context)


def servizi(request):
    """Pagina con tutti i servizi di finanziamento e prestiti (senza filtri GET)"""

    # Rimuoviamo la logica di filtro basata su request.GET.get('categoria', None)

    prestiti = TipoPrestito.objects.filter(attivo=True)

    # Nota: Rimuovo anche 'categorie' e 'categoria_selezionata' dal contesto,
    # poiché non sono più usati nel template per i filtri.

    context = {
        'prestiti': prestiti,
    }
    return render(request, 'filiale/servizi.html', context)


def dettaglio_servizio(request, pk):
    """Dettaglio di un singolo servizio di prestito"""
    prestito = get_object_or_404(TipoPrestito, pk=pk, attivo=True)
    servizi_correlati = TipoPrestito.objects.filter(
        attivo=True,
        categoria=prestito.categoria
    ).exclude(pk=pk)[:2]

    context = {
        'prestito': prestito,
        'servizi_correlati': servizi_correlati,
    }
    return render(request, 'filiale/dettaglio_servizio.html', context)


def chi_siamo(request):
    """Pagina informativa sulla filiale"""
    filiale = Filiale.objects.first()

    context = {
        'filiale': filiale,
    }
    return render(request, 'filiale/chi_siamo.html', context)



def documentazione(request):
    """Pagina con documenti informativi e guide"""
    documenti = DocumentoInfo.objects.all()

    # Paginazione
    paginator = Paginator(documenti, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'filiale/documentazione.html', context)


