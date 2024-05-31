# nom_de_l_application/forms.py

from django import forms

from Model.models import Conducteur


class ConducteurForm(forms.ModelForm):
    class Meta:
        model = Conducteur
        exclude = ['disponibilite', 'supprimer']

    def __init__(self, *args, **kwargs):
        super(ConducteurForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name != 'disponibilite' and field_name != 'image':
                self.fields[field_name].required = True

        self.fields['numero_permis_conduire'].error_messages = {
            'unique': 'ce numéro de permis existe déjà.',
            'required': 'Ce champ est obligatoire.'
        }

        self.fields['numero_telephone'].error_messages = {
            'unique': 'Ce numéro de téléphone existe déjà.',
            'required': 'Ce champ est obligatoire.'
        }

        self.fields['num_cni'].error_messages = {
            'unique': 'Ce numéro de carte d\'identité existe déjà.',
            'required': 'Ce champ est obligatoire.'
        }


class ConducteurSearchForm(forms.Form):
    q = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Rechercher un conducteur: Nom, Prénoms, Numéro...',
                   'class': 'form-control conducteur-search'}),
    )
