from django.urls import path

from vehicule.views import Ajouter_vehicule, liste_vehicules, supprimer_vehicule, modifier_vehicule, vehicul_search, \
    ajouter_marque, details_vehicule, ajouter_type, get_modeles

app_name = 'vehicule'

urlpatterns = [
    path('Ajouter_vehicule/', Ajouter_vehicule, name='Ajouter_vehicule'),
    path('liste_vehicules/', liste_vehicules, name='liste_vehicules'),
    path('supprimer_vehicule/<int:pk>/', supprimer_vehicule, name='supprimer_vehicule'),
    path('modifier_vehicule/<int:pk>/', modifier_vehicule, name='modifier_vehicule'),
    path('recherche/', vehicul_search, name='vehicul_search'),
    path('ajouter_marque/', ajouter_marque, name='ajouter_marque'),
    path('ajouter_type/', ajouter_type, name='ajouter_type'),
    path('details_vehicule/<int:vehicule_id>/', details_vehicule, name='details_vehicule'),
    path('get_modeles/', get_modeles, name='get_modeles'),
]
