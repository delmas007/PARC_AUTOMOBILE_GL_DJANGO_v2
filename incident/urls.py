from django.urls import path
from incident.views import enregistrer_incident, liste_incidents_externe, liste_incidents_interne, incidents_search, \
    incident_interne_detail, modifier_incident_interne, incidents_externe_search, incident_externe_detail

app_name = 'incident'

urlpatterns = [
    path('enregistrer_incident/', enregistrer_incident, name='enregistrer_incident'),
    path('liste_incidents_externe/', liste_incidents_externe, name='liste_incidents_externe'),
    path('liste_incidents_interne/', liste_incidents_interne, name='liste_incidents_interne'),
    path('recherche_incidents_interne/', incidents_search, name='incidents_search'),
    path('incidents_externe_search/', incidents_externe_search, name='incidents_externe_search'),
    path('detail_incidents_interne-<int:pk>/', incident_interne_detail, name='incident_interne_detail'),
    path('detail_incidents_externe-<int:pk>/', incident_externe_detail, name='incident_externe_detail'),
    path('modifier_incident_interne-<int:pk>', modifier_incident_interne, name='modifier_incident_interne')
]
