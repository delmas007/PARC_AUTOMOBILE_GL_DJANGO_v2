from django.urls import path

from entretien.views import Ajouter_Entretien, liste_Entretien, entretien_search, details_entretien, modifier_entretien

app_name = 'entretien'

urlpatterns = [
    path('Ajouter_Entretien/', Ajouter_Entretien, name='Ajouter_Entretien'),
    path('liste_Entretien/', liste_Entretien, name='liste_Entretien'),
    path('recherche/', entretien_search, name='entretien_search'),
    path('Details_entretien/<int:entretien_id>/', details_entretien, name='details_entretien'),
    path('modifier_entretien/<int:pk>/', modifier_entretien, name='modifier_entretien'),
]