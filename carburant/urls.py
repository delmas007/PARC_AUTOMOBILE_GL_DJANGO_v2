from django.urls import path

from carburant.views import Ajouter_carburant, liste_carburant, Modifier_carburant, carburant_search, details_carburant, \
    get_TypeCarburant

app_name = 'carburant'

urlpatterns = [
    path('Ajouter_carburant/', Ajouter_carburant, name='Ajouter_carburant'),
    path('liste_carburant/', liste_carburant, name='Liste_carburant'),
    path('Modifier_carburant/<int:pk>/', Modifier_carburant, name='Modifier_carburant'),
    path('recherche/', carburant_search, name='carburant_search'),
    path('Detail_carburant/<int:pk>/', details_carburant, name='details_carburant'),
    path('carburant/get_TypeCarburant/', get_TypeCarburant, name='get_TypeCarburant'),

]
