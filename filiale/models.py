from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date


class Filiale(models.Model):
    nome = models.CharField(max_length=200, default="Santander Filiale")
    indirizzo = models.CharField(max_length=300)
    citta = models.CharField(max_length=100)
    cap = models.CharField(max_length=10)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    orario_apertura = models.TextField(help_text="Orari di apertura")
    descrizione = models.TextField()
    immagine = models.ImageField(upload_to='filiale/', blank=True, null=True)

    def __str__(self):
        return f"{self.nome} - {self.citta}"

    class Meta:
        verbose_name_plural = "Filiali"


class TipoPrestito(models.Model):
    CATEGORIA_CHOICES = [
        ('personale', 'Prestito Personale'),
        ('auto', 'Prestito Auto'),
        ('casa', 'Mutuo Casa'),
        ('ristrutturazione', 'Prestito Ristrutturazione'),
        ('liquidita', 'Prestito Liquidità'),
    ]

    nome = models.CharField(max_length=200)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    descrizione_breve = models.CharField(max_length=300)
    descrizione_completa = models.TextField()
    tasso_interesse_da = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Tasso di interesse minimo (%)"
    )
    importo_minimo = models.DecimalField(max_digits=10, decimal_places=2)
    importo_massimo = models.DecimalField(max_digits=10, decimal_places=2)
    durata_mesi_min = models.IntegerField(help_text="Durata minima in mesi")
    durata_mesi_max = models.IntegerField(help_text="Durata massima in mesi")
    vantaggi = models.TextField(help_text="Elenco vantaggi (uno per riga)")
    requisiti = models.TextField(help_text="Requisiti necessari")
    icona = models.CharField(max_length=50, blank=True, help_text="Classe icona CSS")
    attivo = models.BooleanField(default=True)
    ordine = models.IntegerField(default=0)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Tipi di Prestito"
        ordering = ['ordine', 'nome']


class Testimonial(models.Model):
    nome_cliente = models.CharField(max_length=100)
    iniziale_cognome = models.CharField(max_length=1, help_text="Es: M.")
    tipo_servizio = models.ForeignKey(
        TipoPrestito,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    testimonianza = models.TextField()
    valutazione = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    data_pubblicazione = models.DateField(auto_now_add=True)
    approvato = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nome_cliente} {self.iniziale_cognome}. - {self.valutazione}★"

    class Meta:
        verbose_name_plural = "Testimonial"
        ordering = ['-data_pubblicazione']


class RichiestaContatto(models.Model):
    MOTIVO_CHOICES = [
        ('info_prestito', 'Informazioni su Prestito'),
        ('info_mutuo', 'Informazioni su Mutuo'),
        ('appuntamento', 'Richiesta Appuntamento'),
        ('reclamo', 'Reclamo'),
        ('PREV', 'Richiesta di Preventivo'),
        ('altro', 'Altro'),
    ]

    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    motivo = models.CharField(max_length=50, choices=MOTIVO_CHOICES, default='altro')
    messaggio = models.TextField()
    privacy_accettata = models.BooleanField(default=False)
    data_richiesta = models.DateTimeField(auto_now_add=True)
    gestita = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nome} {self.cognome} - {self.get_motivo_display()}"

    class Meta:
        verbose_name_plural = "Richieste di Contatto"
        ordering = ['-data_richiesta']


class DocumentoInfo(models.Model):
    titolo = models.CharField(max_length=200)
    descrizione = models.TextField()
    file = models.FileField(upload_to='documenti/')
    categoria = models.CharField(max_length=100)
    data_pubblicazione = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.titolo

    class Meta:
        verbose_name_plural = "Documenti Informativi"
        ordering = ['-data_pubblicazione']


class Appuntamento(models.Model):

    giorno = models.DateField()
    ora = models.TimeField()
    data_prenotazione = models.DateTimeField(default=timezone.now)

    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    motivo = models.TextField(max_length=500, verbose_name="Motivo dell'Appuntamento")

    class Meta:
        verbose_name_plural = "Appuntamenti"
        unique_together = ('giorno', 'ora')
        ordering = ['giorno', 'ora']

    def __str__(self):
        return f"Appuntamento di {self.nome} {self.cognome} il {self.giorno.strftime('%d/%m/%Y')} alle {self.ora.strftime('%H:%M')}"
