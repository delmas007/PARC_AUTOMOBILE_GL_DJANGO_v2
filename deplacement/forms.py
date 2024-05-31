from django import forms

import deplacement
from Model.models import Deplacement, Vehicule, Utilisateur, Conducteur, EtatArrive
from django.db.models import Q
from django.forms import ClearableFileInput
from django.forms.widgets import Input


class MultipleFileInput(Input):
    template_name = 'enregister_deplacement.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['value'] = value
        return context


class DeplacementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeplacementForm, self).__init__(*args, **kwargs)
        # Récupérer l'instance de déplacement actuelle


        # Définir le queryset pour le champ 'vehicule'

            # Si aucune instance n'existe (ajout), afficher tous les véhicules/conducteurs disponibles
        self.fields['vehicule'].queryset = Vehicule.objects.filter(disponibilite=True).exclude(supprimer=True)
        self.fields['conducteur'].queryset = Conducteur.objects.filter(disponibilite=True).exclude(supprimer=True)

        # Mise à jour des attributs du widget 'vehicule'
        self.fields['vehicule'].widget.attrs.update({
            'class': "form-control",
            'id': "selectVehicule",
            'required': True,
        })

        # Mise à jour des attributs du widget 'conducteur'
        self.fields['conducteur'].widget.attrs.update({
            'class': "form-control",
            'id': "selectConducteur",
            'required': True,
        })

        # Exclure les conducteurs non disponibles

    class Meta:
        model = Deplacement
        fields = '__all__'

    images = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=False)
    photo_jauge_depart = forms.ImageField(required=False)


class deplacementModifierForm(forms.ModelForm):



    def __init__(self, *args, **kwargs):
        super(deplacementModifierForm, self).__init__(*args, **kwargs)
        self.fields['vehicule'].widget.attrs.update({
            'class': "form-control",
            'id': "selectVehicule",
            'required': True,
        })

        self.fields['conducteur'].widget.attrs.update({
            'class': "form-control",
            'id': "selectConducteur",
            'required': True,
        })
        instance = kwargs.get('instance')
        if instance:
            # Si une instance existe (modification), inclure le véhicule/le conducteur actuel
            vehicule_actuel = instance.vehicule
            conducteur_actuel = instance.conducteur
            self.fields['vehicule'].queryset = Vehicule.objects.filter(Q(disponibilite=True) | Q(pk=vehicule_actuel.pk))
            self.fields['conducteur'].queryset = Conducteur.objects.filter(
                Q(disponibilite=True) | Q(pk=conducteur_actuel.pk))


    class Meta:
        model = Deplacement
        exclude = ['utilisateur']

    images = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=False)
    photo_jauge_depart = forms.ImageField(required=False)


class deplacementModifierForm_cours(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(deplacementModifierForm_cours, self).__init__(*args, **kwargs)
        self.fields['vehicule'].widget.attrs.update({
            'class': "form-control",
            'id': "selectVehicule",
            'required': True,
        })

        self.fields['conducteur'].widget.attrs.update({
            'class': "form-control",
            'id': "selectConducteur",
            'required': True,
        })
        instance = kwargs.get('instance')
        if instance:
            # Si une instance existe (modification), inclure le véhicule/le conducteur actuel
            vehicule_actuel = instance.vehicule
            conducteur_actuel = instance.conducteur
            self.fields['vehicule'].queryset = Vehicule.objects.filter(Q(disponibilite=True) | Q(pk=vehicule_actuel.pk))
            self.fields['conducteur'].queryset = Conducteur.objects.filter(
                Q(disponibilite=True) | Q(pk=conducteur_actuel.pk))

    class Meta:
        model = Deplacement
        fields = 'vehicule', 'conducteur'

    images = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=False)
    photo_jauge_depart = forms.ImageField(required=False)


class EtatArriveForm(forms.ModelForm):
    deplacement_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = EtatArrive
        fields = ['deplacement_id', 'kilometrage_arrive', 'photo_jauge_arrive']
        images = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=False)
        photo_jauge_arrive = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DeplacementSearchForm(forms.Form):
    q = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Rechercher un deplacement : Marque, matricule...', 'class': 'form-control'}),
    )
