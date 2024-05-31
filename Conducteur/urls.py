
from django.urls import path
from Conducteur.views import ajouter_conducteur, tous_les_conducteurs, supprimer_conducteur, modifier_conducteur, \
    conducteur_search, details_conducteur

app_name = 'conducteur'

urlpatterns = [
    path('ajouter_conducteur/', ajouter_conducteur, name='ajouter_conducteur'),
    path('tous_les_conducteurs/', tous_les_conducteurs, name='tous_les_conducteurs'),
    path('supprimer_conducteur/<int:conducteur_id>/', supprimer_conducteur, name='supprimer_conducteur'),
    path('modifier_conducteur/<int:conducteur_id>/', modifier_conducteur, name='modifier_conducteur'),
    path('recherche/', conducteur_search, name='conducteur_search'),
    path('details_conducteur/<int:conducteur_id>/', details_conducteur, name='details_conducteur'),
]
