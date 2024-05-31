
from django import forms

from Model.models import Carburant


class AjouterCarburantForm(forms.ModelForm):
    class Meta:
        model = Carburant
        fields = ['vehicule', 'quantite']

    def __init__(self, *args, **kwargs):
        super(AjouterCarburantForm, self).__init__(*args, **kwargs)
        self.fields['vehicule'].widget.attrs.update({'class': 'form-control', 'id': 'selectVehicule'})
        self.fields['quantite'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ajouter le litre de carburant', 'min': '1', 'required': 'required'})

    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        return quantite


class ModifierCarburantForm(forms.ModelForm):
    class Meta:
        model = Carburant
        fields = ['vehicule', 'quantite']

    def __init__(self, *args, **kwargs):
        super(ModifierCarburantForm, self).__init__(*args, **kwargs)
        self.fields['vehicule'].widget.attrs.update({'class': 'form-control', 'id': 'selectVehicule'})
        self.fields['quantite'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ajouter le litre de carburant ', 'min': '1', 'required': 'required'})

    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        # Ajoutez ici d'autres validations personnalisées selon vos besoins
        return quantite

    class CarburantSearchForm(forms.Form):
        q = forms.CharField(
            label='',
            required=False,
            #     widget=forms.TextInput(
            #         attrs={'placeholder': 'Rechercher un incident : Marque, matricule...', 'class': 'form-control'}),
        )


class CarburantSearchForm(forms.Form):
    q = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Rechercher un véhicule : Marque, matricule...', 'class': 'form-control'}),
    )