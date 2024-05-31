from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.forms.widgets import Input

from Model.models import Conducteur, Utilisateur, Demande_prolongement, Incident, Vehicule, Deplacement, Motif
from django import forms


# Create your models here.

class ConducteurClientForm(forms.ModelForm):
    class Meta:
        model = Conducteur
        fields = '__all__'


class PasswordResetForme(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'type': "email",
            'class': "form-control mb-0",
            'id': "exampleInputEmail1",
            'placeholder': "name@example.com",
            'required': True,
            'name': 'email',
        })


class notificationSearchForm(forms.Form):
    q = forms.CharField(
        label='',
        required=False,
    )


class ChangerMotDePasse(SetPasswordForm):
    class Meta:
        model = Utilisateur
        fields = ['new_password1', 'new_password2']


class MultipleFileInput(Input):
    template_name = 'compte_conducteur.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['value'] = value
        return context


class DemandeProlongementForm(forms.ModelForm):
    deplacement_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Demande_prolongement
        fields = ['motif', 'duree', 'deplacement', 'photo_jauge_demande', 'kilometrage']
        images = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=True)


class DeclareIncidentForm(forms.ModelForm):
    deplacement2_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    vehicule_id = forms.ModelChoiceField(queryset=Vehicule.objects.all(), widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Incident
        exclude = ['utilisateurs', 'vehicule', 'conducteur', 'deplacement']
        images = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=True)


class MotifForm(forms.ModelForm):
    class Meta:
        model = Motif
        fields = ['descritption_modtif']