from django.contrib import admin
from .models import Filiale, TipoPrestito, Testimonial, RichiestaContatto, DocumentoInfo, Appuntamento

@admin.register(Filiale)
class FilialeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'citta', 'telefono', 'email']
    search_fields = ['nome', 'citta', 'indirizzo']

@admin.register(TipoPrestito)
class TipoPrestitoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'tasso_interesse_da', 'importo_minimo', 'importo_massimo', 'attivo', 'ordine']
    list_filter = ['categoria', 'attivo']
    search_fields = ['nome', 'descrizione_breve']
    list_editable = ['attivo', 'ordine']
    ordering = ['ordine', 'nome']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['nome_cliente', 'iniziale_cognome', 'tipo_servizio', 'valutazione', 'data_pubblicazione', 'approvato']
    list_filter = ['approvato', 'valutazione', 'tipo_servizio']
    search_fields = ['nome_cliente', 'testimonianza']
    list_editable = ['approvato']
    date_hierarchy = 'data_pubblicazione'

@admin.register(RichiestaContatto)
class RichiestaContattoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cognome', 'email', 'motivo', 'data_richiesta', 'gestita']
    list_filter = ['motivo', 'gestita', 'data_richiesta']
    search_fields = ['nome', 'cognome', 'email', 'messaggio']
    list_editable = ['gestita']
    date_hierarchy = 'data_richiesta'
    readonly_fields = ['data_richiesta']

@admin.register(DocumentoInfo)
class DocumentoInfoAdmin(admin.ModelAdmin):
    list_display = ['titolo', 'categoria', 'data_pubblicazione']
    list_filter = ['categoria', 'data_pubblicazione']
    search_fields = ['titolo', 'descrizione']
    date_hierarchy = 'data_pubblicazione'

# Registrazione del modello Appuntamento
@admin.register(Appuntamento)
class AppuntamentoAdmin(admin.ModelAdmin):
    list_display = ('giorno', 'ora', 'nome', 'cognome', 'telefono', 'data_prenotazione')
    list_filter = ('giorno', 'data_prenotazione')
    search_fields = ('nome', 'cognome', 'telefono', 'motivo')
    ordering = ('giorno', 'ora')