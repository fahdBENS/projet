from django import forms
from .models import Lot, Processus, Message

class LotForm(forms.ModelForm):
    class Meta:
        model = Lot
        fields = ['ref', 'quantite']
        widgets = {
            'ref': forms.TextInput(attrs={'size': '20'}),  # Réduit la taille du champ 'ref'
            'quantite': forms.NumberInput(attrs={'size': '10'})  # Réduit la taille du champ 'quantite'
        }

class ProcessForm(forms.Form):
    lot = forms.ModelChoiceField(
        queryset=Lot.objects.all(),
        label="Lot",
        widget=forms.Select(attrs={'style': 'width: 200px;'})
    )
    processus = forms.ModelChoiceField(
        queryset=Processus.objects.all(),
        label="Processus",
        widget=forms.Select(attrs={'style': 'width: 200px;'})
    )

class UploadFileForm(forms.Form):
    file = forms.FileField(label='Choisir un fichier Excel')

class ReclamationForm(forms.Form):
    lot = forms.ModelChoiceField(
        queryset=Lot.objects.all(),
        label="Lot",
        widget=forms.Select(attrs={'style': 'width: 200px;'})
    )
    processus = forms.ModelChoiceField(
        queryset=Processus.objects.all(),
        label="Processus",
        widget=forms.Select(attrs={'style': 'width: 200px;'})
    )
    le_message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={'style': 'width: 200px; height: 100px;'})
    )
    responsable = forms.CharField(
        label="Responsable",
        max_length=255,
        widget=forms.TextInput(attrs={'style': 'width: 200px;'})
    )