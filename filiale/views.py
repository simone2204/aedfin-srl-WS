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


def contatti(request):
    """Pagina contatti con form e pre-compilazione da richiesta preventivo"""
    filiale = Filiale.objects.first()

    initial_data = {}

    importo = request.GET.get('importo')
    durata = request.GET.get('durata')
    rata = request.GET.get('rata')

    if importo and durata and rata:
        try:

            importo_pulito = importo.replace('.', '').replace(',', '.')
            rata_pulito = rata.replace('.', '').replace(',', '.')

            importo_f = float(importo_pulito)
            durata_i = int(durata)
            rata_f = float(rata_pulito)

            messaggio_precompilato = (
                f"Buongiorno,\n\nRichiedo un preventivo per il seguente finanziamento:\n"
                f"- Importo desiderato: €{importo_f:.2f}\n"
                f"- Durata desiderata: {durata_i} mesi\n"
                f"- Rata ideale: €{rata_f:.2f}\n\n"
                f"Attendo un vostro riscontro. Grazie."
            )
            messaggio_precompilato = messaggio_precompilato.replace('.', ',')

            initial_data['motivo'] = 'PREV'
            initial_data['messaggio'] = messaggio_precompilato
            messages.info(request, "Il campo 'Messaggio' è stato pre-compilato con i dettagli del tuo preventivo.")

        except (ValueError, TypeError) as e:
            print(f"Errore di conversione preventivo: {e}")
            pass

    # GESTIONE DEL POST (Salvataggio e Invio Email)
    if request.method == 'POST':
        form = RichiestaContattoForm(request.POST)
        if form.is_valid():
            form.save()

            nome = form.cleaned_data['nome']
            cognome = form.cleaned_data['cognome']
            email_cliente = form.cleaned_data['email']
            telefono = form.cleaned_data['telefono']
            motivo_codice = form.cleaned_data['motivo']
            messaggio_testo = form.cleaned_data['messaggio']

            motivo_display = dict(RichiestaContatto.MOTIVO_CHOICES).get(motivo_codice, 'Motivo Sconosciuto')

            subject = f"[CONTATTO WEB] Nuova Richiesta: {motivo_display} da {nome} {cognome}"

            body = f"""
                Hai ricevuto una nuova richiesta dal modulo di contatto.
                
                Dettagli Cliente:
                - Nome e Cognome: {nome} {cognome}
                - Email: {email_cliente}
                - Telefono: {telefono}
                - Motivo: {motivo_display}
                - Data Ricezione: {timezone.localtime().strftime('%d/%m/%Y %H:%M')}
                
                Contenuto del Messaggio:
                --------------------------------------------------
                {messaggio_testo}
                --------------------------------------------------
                """

            to_email = ['aedfinsrl@gmail.com']

            try:
                email = EmailMessage(
                    subject,
                    body,
                    to=to_email,
                    reply_to=[email_cliente]
                )
                email.send()
            except Exception as e:
                print(f"Errore nell'invio dell'email: {e}")

            messages.success(
                request,
                'Richiesta inviata con successo! Ti contatteremo presto.'
            )
            return redirect('filiale:contatti')


    else:
        form = RichiestaContattoForm(initial=initial_data)

    # Logica per il giorno corrente
    oggi = timezone.localtime().date()
    indice_giorno = oggi.weekday()
    giorni_it = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    giorno_corrente_it = giorni_it[indice_giorno]

    context = {
        'filiale': filiale,
        'form': form,  # 'form' è SEMPRE definito a questo punto
        'giorno_corrente': giorno_corrente_it,
    }
    return render(request, 'filiale/contatti.html', context)


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


def richiedi_preventivo(request):
    """Acquisizione dei dati per richiedere un preventivo personalizzato"""
    risultato = None

    if request.method == 'GET' and 'importo' in request.GET:
        try:
            # Acquisizione dei tre parametri chiave
            importo = float(request.GET.get('importo', 0))
            durata = int(request.GET.get('durata', 0))
            rata_desiderata = float(request.GET.get('rata', 0))

            # Semplice validazione
            if importo <= 0 or durata <= 0 or rata_desiderata <= 0:
                 messages.error(request, 'Errore. Assicurati che tutti i valori siano maggiori di zero.')
            else:
                # Si prepara l'oggetto risultato per la visualizzazione/conferma
                risultato = {
                    'importo': round(importo, 2),
                    'durata': durata,
                    'rata_desiderata': round(rata_desiderata, 2),
                }
                messages.success(
                    request,
                    'I tuoi dati sono stati registrati. Prosegui per inviare la richiesta.'
                )

        except (ValueError, TypeError):
            messages.error(request, 'Errore di formato. Verifica i dati numerici inseriti.')

    context = {
        'risultato': risultato,
    }
    return render(request, 'filiale/richiedi_preventivo.html', context)




FASCE_ORARIE = [
    time(9, 0), time(10, 0), time(12, 0), time(15, 0), time(16, 0), time(17, 0)
]

FASCE_DISPLAY = {
    time(9, 0): '9:00 - 10:00',
    time(10, 0): '10:00 - 11:00',
    time(12, 0): '12:00 - 12:30',
    time(15, 0): '15:00 - 16:00',
    time(16, 0): '16:00 - 17:00',
    time(17, 0): '17:00 - 18:00',
}


def prenota_appuntamento(request):

    GIORNI_IT = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    MESI_IT = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto",
        "Settembre", "Ottobre", "Novembre", "Dicembre"
    ]

    oggi = timezone.localdate()
    giorni_disponibili = {}

    # Ottieni la data corrente e l'orario locale
    oggi = timezone.localdate()
    now_time = timezone.localtime().time()

    # 🌟 MODIFICA FONDAMENTALE 🌟
    # 1. Calcola l'ultima ora prenotabile
    ultima_ora_prenotabile = FASCE_ORARIE[-1]

    # 2. Determina la data di inizio (start_date)

    # Se è Sabato (5) o Domenica (6) O se l'ultima ora prenotabile di oggi è passata
    # (Usiamo time(17,0) che è l'ultima fascia oraria)
    if oggi.weekday() >= 4 or now_time >= ultima_ora_prenotabile:
        # Calcola il Lunedì della SETTIMANA SUCCESSIVA
        giorni_al_lunedi_succ = 7 - oggi.weekday()
        start_date = oggi + timedelta(days=giorni_al_lunedi_succ)
    else:
        # Altrimenti, si parte da OGGI
        start_date = oggi


    # 🌟 MODIFICA CHIAVE: AUMENTA IL RANGE 🌟
    # Iteriamo su 12 giorni per coprire i rimanenti della settimana corrente + i 5 giorni della prossima.
    for i in range(12):
        giorno = start_date + timedelta(days=i)

        # 🛑 Salta i giorni passati (non dovrebbe avvenire dopo la logica start_date, ma è una sicurezza)
        if giorno < oggi:
            continue

        # 🛑 Salta Sabato (5) e Domenica (6)
        if giorno.weekday() > 4:
            continue

        # Nome del giorno in italiano
        nome_giorno = GIORNI_IT[giorno.weekday()]
        nome_mese = MESI_IT[giorno.month - 1]
        display_giorno_completo = f"{nome_giorno} {giorno.day} {nome_mese} {giorno.year}"

        # Recupera gli orari già prenotati per quel giorno
        appuntamenti_prenotati = Appuntamento.objects.filter(giorno=giorno).values_list('ora', flat=True)

        orari_disponibili = []
        for ora in FASCE_ORARIE:
            # 🌟 LOGICA CHIAVE: Escludi gli orari già trascorsi OGGI 🌟
            # Usiamo start_date perché se è Venerdì, start_date sarà Lunedì prossimo
            is_passed = (giorno == oggi and ora <= now_time)

            # L'orario è disponibile solo se:
            # 1. Non è già stato prenotato.
            # 2. NON è un orario già passato (solo se giorno == oggi).
            if ora not in appuntamenti_prenotati and not is_passed:
                orari_disponibili.append(
                    {'value': ora.isoformat(), 'display': FASCE_DISPLAY.get(ora, ora.strftime('%H:%M'))})

        # Aggiungi il giorno solo se ha slot disponibili
        if orari_disponibili:
            giorni_disponibili[giorno.isoformat()] = {
                'nome': display_giorno_completo,
                'orari': orari_disponibili
            }

    # --- GESTIONE DELLO STEP 2: DATI CLIENTE ---

    if request.method == 'POST':
        # ... (il resto della logica POST rimane invariato) ...
        giorno_str = request.POST.get('giorno_selezionato')
        ora_str = request.POST.get('ora_selezionata')

        if not giorno_str or not ora_str:
            messages.error(request, "Errore: Giorno o ora non validi. Riprova.")
            return redirect('filiale:prenota_appuntamento')

        # Conversione dei dati in oggetti Python
        giorno_obj = date.fromisoformat(giorno_str)
        ora_obj = time.fromisoformat(ora_str)

        nome_giorno = GIORNI_IT[giorno_obj.weekday()]
        nome_mese = MESI_IT[giorno_obj.month - 1]

        # Veloce ricontrollo di disponibilità per evitare race condition
        if Appuntamento.objects.filter(giorno=giorno_obj, ora=ora_obj).exists():
            messages.error(request,
                           f"L'appuntamento per il {giorno_obj.strftime('%d/%m/%Y')} alle {ora_obj.strftime('%H:%M')} è stato appena prenotato. Scegli un altro orario.")
            return redirect('filiale:prenota_appuntamento')

        # Inizializza il form con i dati POST del cliente
        form = DatiClienteAppuntamentoForm(request.POST)

        if form.is_valid():
            appuntamento = form.save(commit=False)
            appuntamento.giorno = giorno_obj
            appuntamento.ora = ora_obj
            appuntamento.save()

            # --------------------- INVIO EMAIL DI CONFERMA (MODIFICATO PER DEBUG) ---------------------

            # Recuperiamo l'orario display per l'email
            display_ora_completa = FASCE_DISPLAY.get(ora_obj, ora_obj.strftime('%H:%M'))

            subject = f"[PRENOTAZIONE] Appuntamento per {giorno_obj.strftime('%d/%m/%Y')} alle {display_ora_completa}"

            body = f"""
            Hai ricevuto una nuova prenotazione di appuntamento:

            - Nome: {appuntamento.nome}
            - Cognome: {appuntamento.cognome}
            - Telefono: {appuntamento.telefono}
            - Data Appuntamento: {giorno_obj.strftime('%d/%m/%Y')}
            - Ora Appuntamento: {display_ora_completa}

            Motivo della richiesta:
            --------------------------------------------------
            {appuntamento.motivo}
            --------------------------------------------------
            """
            to_email = ['aedfinsrl@gmail.com']  # Indirizzo di destinazione

            # 🛑 DEBUG: Rimuoviamo il try/except per vedere l'errore a console.
            email = EmailMessage(
                subject,
                body,
                to=to_email,
                # Reply-to omesso perché il modello Appuntamento non ha il campo email
            )
            email.send()

            # --------------------- FINE INVIO EMAIL ---------------------

            messages.success(request,
                             f"Appuntamento confermato per il {giorno_obj.strftime('%d/%m/%Y')} alle {ora_obj.strftime('%H:%M')}. Riceverai una nostra chiamata per eventuale conferma.")
            return redirect('filiale:home')

        else:
            # Se il form non è valido, mostra nuovamente lo step 2 con gli errori
            context = {
                'form': form,
                'giorno_selezionato': giorno_str,
                'ora_selezionata': ora_str,
                'display_ora': FASCE_DISPLAY.get(ora_obj, ora_obj.strftime('%H:%M')),
                'step_due': True
            }
            return render(request, 'filiale/prenota_appuntamento.html', context)

    # --- GESTIONE DEL GET E STEP 1: SCELTA GIORNO/ORA ---

    # Recupera le selezioni se presenti
    giorno_selezionato = request.GET.get('giorno')
    ora_selezionata = request.GET.get('ora')

    if giorno_selezionato and ora_selezionata:
        # L'utente ha selezionato giorno e ora, passa allo step 2
        try:
            giorno_obj = date.fromisoformat(giorno_selezionato)
            ora_obj = time.fromisoformat(ora_selezionata)

            nome_giorno = GIORNI_IT[giorno_obj.weekday()]
            nome_mese = MESI_IT[giorno_obj.month - 1]
            display_giorno_completo = f"{nome_giorno} {giorno_obj.day} {nome_mese} {giorno_obj.year}"

            # Re-verifica rapida di disponibilità
            if Appuntamento.objects.filter(giorno=giorno_obj, ora=ora_obj).exists():
                messages.error(request, "L'orario selezionato non è più disponibile. Scegli un altro slot.")
                return redirect('filiale:prenota_appuntamento')

            context = {
                'form': DatiClienteAppuntamentoForm(),
                'giorno_selezionato': giorno_selezionato,
                'ora_selezionata': ora_selezionata,
                'display_ora': FASCE_DISPLAY.get(ora_obj, ora_obj.strftime('%H:%M')),
                'display_data_completa': display_giorno_completo,
                'step_due': True  # Flag per mostrare il secondo template
            }
            return render(request, 'filiale/prenota_appuntamento.html', context)

        except (ValueError, TypeError):
            messages.error(request, "Selezione di giorno/ora non valida. Riprova.")
            return redirect('filiale:prenota_appuntamento')

    # Step 1: Mostra la selezione giorno/ora
    context = {
        'giorni_disponibili': giorni_disponibili,
        'step_due': False
    }
    return render(request, 'filiale/prenota_appuntamento.html', context)