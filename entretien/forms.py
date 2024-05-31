from django import forms

from Model.models import Entretien, Vehicule


class EntretienForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['vehicule'].queryset = Vehicule.objects.exclude(supprimer=True)

        self.fields['type'].widget.attrs.update({
            'class': "form-control",
            'id': "selectType",
            'required': True,
        })
        self.fields['vehicule'].widget.attrs.update({
            'class': "form-control",
            'id': "selectVehicule2",
            'required': True,
        })

        self.fields['description'].widget.attrs.update({
            'class': "form-control",
            'id': "description",
            'rows': 4,
            'required': True,
        })

    class Meta:
        model = Entretien
        fields = '__all__'


class IncidentSearchForm(forms.Form):
    q = forms.CharField(
        label='',
        required=False,
    )


class EntretienModifierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['description'].widget.attrs.update({
            'class': "form-control",
            'id': "description",
            'rows': 4,
            'required': True,
        })

    class Meta:
        model = Entretien
        fields = ['description']

