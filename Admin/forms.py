from django import forms
from django.contrib.auth.forms import UserCreationForm

from Model.models import type_carburant, Utilisateur


class typeCarburantForm(forms.ModelForm):
    class Meta:
        model = type_carburant
        fields = ['nom', 'prix']

    nom = forms.ModelChoiceField(queryset=type_carburant.objects.all(), required=True)

    def __init__(self, *args, **kwargs):
        super(typeCarburantForm, self).__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs.update({
            'class': "form-control",
            'id': "energie",
            'required': True,
            'name': 'nom'
        })


class CarburantModifierForm(forms.ModelForm):
    class Meta:
        model = type_carburant
        fields = ['nom', 'prix']

    def __init__(self, *args, **kwargs):
        super(CarburantModifierForm, self).__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs.update({'class': 'form-control', 'id': 'exampleInputdate'})
        self.fields['prix'].widget.attrs.update({'class': 'form-control', 'min': '1'})


class CarburantSearchForm(forms.Form):
    q = forms.CharField(
        label='',
        required=False,
    )


class UserRegistrationForm(UserCreationForm):
    image = forms.ImageField(required=False)  # Définir un champ de fichier pour l'image

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)

        self.fields['username'].error_messages = {
            'unique': 'Ce nom d\'utilisateur existe déjà.',
            'required': 'Ce champ est obligatoire.'
        }

        self.fields['email'].error_messages = {
            'unique': 'Cet email existe déjà.',
            'required': 'Ce champ est obligatoire.'
        }

    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'nom', 'prenom', 'conducteur',
                  'image']  # Inclure le champ 'image' dans les champs du formulaire
