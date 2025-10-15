from django import forms
from .models import RichiestaContatto, Appuntamento


class RichiestaContattoForm(forms.ModelForm):
    class Meta:
        model = RichiestaContatto
        fields = ['nome', 'cognome', 'email', 'telefono', 'motivo', 'messaggio', 'privacy_accettata']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Il tuo nome'
            }),
            'cognome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Il tuo cognome'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'la.tua.email@esempio.it'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+39 123 456 7890'
            }),
            'motivo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'messaggio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Scrivi qui il tuo messaggio...'
            }),
            'privacy_accettata': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'nome': 'Nome',
            'cognome': 'Cognome',
            'email': 'Email',
            'telefono': 'Telefono',
            'motivo': 'Motivo del contatto',
            'messaggio': 'Messaggio',
            'privacy_accettata': 'Accetto la privacy policy',
        }

    def clean_privacy_accettata(self):
        privacy = self.cleaned_data.get('privacy_accettata')
        if not privacy:
            raise forms.ValidationError('Devi accettare la privacy policy per continuare.')
        return privacy


class DatiClienteAppuntamentoForm(forms.ModelForm):

    class Meta:
        model = Appuntamento
        fields = ['nome', 'cognome', 'telefono', 'motivo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'}),
            'cognome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cognome'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numero di Telefono'}),
            'motivo': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Motivo dell\'appuntamento'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['nome'].required = True
        self.fields['cognome'].required = True
        self.fields['telefono'].required = True
        self.fields['motivo'].required = True