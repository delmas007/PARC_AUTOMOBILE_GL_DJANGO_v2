from django import forms
from django.forms import ClearableFileInput
from django.forms.widgets import Input

from Model.models import Vehicule, Marque, Type_Commerciale, Carburant, type_carburant


class XYZ_DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        kwargs.setdefault('attrs', {})
        kwargs['attrs'].update({
            'class': 'form-control',
            'required': False,
        })
        kwargs["format"] = "%m-%d-%Y"
        # kwargs["format"] = "%d-%m-%Y"
        super().__init__(**kwargs)


class XYZ_DateInpute(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        kwargs.setdefault('attrs', {})
        kwargs['attrs'].update({
            'class': 'form-control',
            'required': False,
        })
        kwargs["format"] = "%m-%d-%Y"
        # kwargs["format"] = "%d-%m-%Y"
        super().__init__(**kwargs)


class MultipleFileInput(Input):
    template_name = 'ajouter_vehicule.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['value'] = value
        return context


class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        exclude = ['disponibilite']

    marque = forms.ModelChoiceField(queryset=Marque.objects.all(), required=True)
    images = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=False)
    energie = forms.ModelChoiceField(queryset=type_carburant.objects.all(), required=True)
    type_commercial = forms.ModelChoiceField(queryset=Type_Commerciale.objects.all(), required=True)

    def __init__(self, *args, **kwargs):
        super(VehiculeForm, self).__init__(*args, **kwargs)
        self.fields['marque'].widget.attrs.update({
            'class': "form-control",
            'id': "selectMarque",
            'required': True,
        })

        self.fields['type_commercial'].widget.attrs.update({
            'class': "form-control",
            'id': "selectModel",
            'required': True,
        })

        self.fields['image_recto'].required = True
        self.fields['image_verso'].required = True
        self.fields['date_expiration_assurance'].required = True
        self.fields['date_visite_technique'].required = True
        self.fields['videnge'].required = True
        self.fields['taille_reservoir'].required = True
        self.fields['date_mise_circulation'].required = True
        self.fields['energie'].widget.attrs.update({
            'class': "form-control",
            'id': "energie",
            'required': True,
        })
        self.fields['place_assises'].widget.attrs.update({
            'class': "form-control",
            'id': "place_assises",
            'required': True,
        })
        self.fields['carrosserie'].widget.attrs.update({
            'class': "form-control",
            'id': "carrosserie",
            'required': True,
        })
        self.fields['numero_immatriculation'].widget.attrs.update({
            'class': "form-control",
            'id': "numero_immatriculation",
            'required': True,
        })
        self.fields['kilometrage'].widget.attrs.update({
            'class': "form-control",
            'id': "kilometrage",
            'required': True,
        })
        self.fields['carte_grise'].widget.attrs.update({
            'class': "form-control",
            'id': "carte_grise",
            'required': True,
        })
        self.fields['couleur'].widget.attrs.update({
            'class': "form-control",
            'id': "couleur",
            'required': True,
        })
        self.fields['numero_chassis'].widget.attrs.update({
            'class': "form-control",
            'id': "numero_chassis",
            'required': True,

        })

        self.fields['date_expiration_assurance'].widget.attrs.update({
            'class': "form-control",
            'id': "date_expiration_assurance",
        })
        self.fields['date_mise_circulation'].widget.attrs.update({
            'class': "form-control",
            'id': "date_mise_circulation",

        })

        self.fields['date_visite_technique'].widget.attrs.update({
            'class': "form-control",
            'id': "date_visite_technique",
        })
        self.fields['taille_reservoir'].widget.attrs.update({
            'class': "form-control",
            'id': "taille_reservoir ",
        })
        self.fields['videnge'].widget.attrs.update({
            'class': "form-control",
            'id': "videnge ",
        })

        self.fields['numero_immatriculation'].error_messages = {
            'unique': 'Un véhicule a déjà été enregistré avec ce numéro d\'immatriculation.',
            'required': 'Ce champ est obligatoire.'
        }
        self.fields['numero_chassis'].error_messages = {
            'unique': 'Un véhicule a déjà été enregistré avec ce numéro VIN/CHASSIS.',
            'required': 'Ce champ est obligatoire.'
        }
        self.fields['carte_grise'].error_messages = {
            'unique': 'Un véhicule a déjà été enregistré avec ce numéro de carte grise.',
            'required': 'Ce champ est obligatoire.'
        }
        self.fields['image_taxe'].widget.attrs.update({
            'class': "form-control",
            'id': "image_taxe",
        })
        self.fields['image_recepisse'].widget.attrs.update({
            'class': "form-control",
            'id': "image_recepisse",
        })
        self.fields['image_rapport_identification'].widget.attrs.update({
            'class': "form-control",
            'id': "image_rapport_identification",
        })
        self.fields['image_attestation_assurance'].widget.attrs.update({
            'class': "form-control",
            'id': "image_attestation_assurance",
        })
        self.fields['image_assurance_carte_brune'].widget.attrs.update({
            'class': "form-control",
            'id': "image_assurance_carte_brune",
        })
        self.fields['date_limite_recepisse'].widget.attrs.update({
            'class': "form-control",
            'id': "date_limite_recepisse",
        })
        self.fields['date_limite_assurance_carteBrune'].widget.attrs.update({
            'class': "form-control",
            'id': "date_limite_assurance_carteBrune",
        })
        self.fields['date_limite_taxe'].widget.attrs.update({
            'class': "form-control",
            'id': "date_limite_taxe",
        })
        self.fields['date_limite_certificatVignette'].widget.attrs.update({
            'class': "form-control",
            'id': "date_limite_certificatVignette",
        })


class VehiculeModifierForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        exclude = ['disponibilite', 'marque', 'supprimer']

    images = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=False)
    energie = forms.ModelChoiceField(queryset=type_carburant.objects.all(), required=True)

    def __init__(self, *args, **kwargs):
        super(VehiculeModifierForm, self).__init__(*args, **kwargs)
        self.fields['energie'].widget.attrs.update({
            'class': "form-control",
            'id': "energie",
        })
        self.fields['place_assises'].widget.attrs.update({
            'class': "form-control",
            'id': "place_assises",
            'required': True,
        })
        self.fields['carrosserie'].widget.attrs.update({
            'class': "form-control",
            'id': "carrosserie",
            'required': True,
        })
        self.fields['numero_immatriculation'].widget.attrs.update({
            'class': "form-control",
            'id': "numero_immatriculation",
            'required': True,
        })
        self.fields['kilometrage'].widget.attrs.update({
            'class': "form-control",
            'id': "kilometrage",
            'required': True,
        })
        self.fields['carte_grise'].widget.attrs.update({
            'class': "form-control",
            'id': "carte_grise",
            'required': True,
        })
        self.fields['couleur'].widget.attrs.update({
            'class': "form-control",
            'id': "couleur",
            'required': True,
        })
        self.fields['numero_chassis'].widget.attrs.update({
            'class': "form-control",
            'id': "numero_chassis",
            'required': True,
        })
        self.fields['type_commercial'].widget.attrs.update({
            'class': "form-control",
            'id': "type_commercial",
        })
        self.fields['date_visite_technique'].widget.attrs.update({
            'class': "form-control",
            'id': "date_visite_technique",
        })
        self.fields['date_expiration_assurance'].widget.attrs.update({
            'class': "form-control",
            'id': "date_expiration_assurance",
        })
        self.fields['date_mise_circulation'].widget.attrs.update({
            'class': "form-control",
            'id': "date_mise_circulation",

        })
        self.fields['taille_reservoir'].widget.attrs.update({
            'class': "form-control",
            'id': "taille_reservoir",
        })
        self.fields['videnge'].widget.attrs.update({
            'class': "form-control",
            'id': "videnge ",
        })
        self.fields['image_taxe'].widget.attrs.update({
            'class': "form-control",
            'id': "image_taxe",
        })
        self.fields['image_recepisse'].widget.attrs.update({
            'class': "form-control",
            'id': "image_recepisse",
        })
        self.fields['image_rapport_identification'].widget.attrs.update({
            'class': "form-control",
            'id': "image_rapport_identification",
        })
        self.fields['image_attestation_assurance'].widget.attrs.update({
            'class': "form-control",
            'id': "image_attestation_assurance",
        })
        self.fields['image_assurance_carte_brune'].widget.attrs.update({
            'class': "form-control",
            'id': "image_assurance_carte_brune",
        })
        self.fields['date_limite_recepisse'].widget.attrs.update({
            'class': "form-control",
            'id': "date_limite_recepisse",
        })
        self.fields['date_limite_assurance_carteBrune'].widget.attrs.update({
            'class': "form-control",
            'id': "date_limite_assurance_carteBrune",
        })
        self.fields['date_limite_taxe'].widget.attrs.update({
            'class': "form-control",
            'id': "date_limite_taxe",
        })
        self.fields['date_limite_certificatVignette'].widget.attrs.update({
            'class': "form-control",
            'id': "date_limite_certificatVignette",
        })


class VehiculSearchForm(forms.Form):
    q = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Rechercher un véhicule : Marque, matricule...', 'class': 'form-control'}),
    )


class marqueForm(forms.ModelForm):
    class Meta:
        model = Marque
        fields = '__all__'


class typeForm(forms.ModelForm):
    class Meta:
        model = Type_Commerciale
        fields = '__all__'

class typeCarburantForm(forms.ModelForm):
    class Meta:
        model = type_carburant
        fields = '__all__'