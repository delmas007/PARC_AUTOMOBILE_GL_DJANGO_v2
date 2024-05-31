from django.urls import path

from Admin.views import rapport_entretien_mensuel_pdf, rapport_entretien_mensuel_admins, \
    rapport_incident_vehicule_mensuel_admins, rapport_incident_vehicule_mensuel_pdf, ProfilAdmin, inscription, \
    employer_compte, active_emp, desactive_amp, gestionnaire_inactifs, \
    gestionnaire_a_search, gestionnaire_a_search_i, Ajouter_Carburant, liste_Carburant, \
    Carburant_search, dashboard_admins, rapport_depense_admins, rapport_depense_mensuel_admins, \
    rapport_depense_mensuel_pdf, rapport_depense_pdf, \
    CustomPasswordResetConfirmView, ChangerMotDePasse_admin, rapport_carburant_mensuel_pdf, \
    rapport_carburant_mensuel_admins, rapport_incident_conducteur_mensuel_admins, \
    rapport_incident_conducteur_mensuel_pdf, liste_deplacement_arrive_admin, liste_incidents_interne_admin, \
    liste_incidents_externe_admin, \
    details_arriver_admin, incident_interne_detail_admin, incident_externe_detail_admin, incidents_search, \
    incidents_externe_search, arrive_search

app_name = 'admins'

urlpatterns = [
    path('dashboard_admins/', dashboard_admins, name='dashboard_admins'),
    path('liste_deplacement_arrive_admin/', liste_deplacement_arrive_admin, name='liste_deplacement_arrive_admin'),
    path('liste_incidents_externe_admin/', liste_incidents_externe_admin, name='liste_incidents_externe_admin'),
    path('liste_incidents_interne_admin/', liste_incidents_interne_admin, name='liste_incidents_interne_admin'),
    path('Ajout_gestionnaire/', inscription, name='Ajout_gestionnaire'),
    path('Ajouter_Carburant/', Ajouter_Carburant, name='Ajouter_Carburant'),
    path('Compte_gestionnaire/', employer_compte, name='Compte_gestionnaire'),
    path('gestionnaire_inactifs/', gestionnaire_inactifs, name='gestionnaire_inactifs'),
    path('Active_employer/<int:employer_id>/', active_emp, name='active_emp'),
    path('recherche/', gestionnaire_a_search, name='gestionnaire_a_search'),
    path('recherche_i/', gestionnaire_a_search_i, name='gestionnaire_a_search_i'),
    path('Desactive_employer/<int:employer_id>/', desactive_amp, name='desactive_amp'),
    path('liste_Carburant/', liste_Carburant, name='liste_Carburant'),
    path('recherche_carburant/', Carburant_search, name='Carburant_search'),
    path('rapport_depense_admins/', rapport_depense_admins, name='rapport_depense_admins'),
    path('rapport_depense_mensuel_admins/', rapport_depense_mensuel_admins, name='rapport_depense_mensuel_admins'),
    path('rapport_carburant_mensuel_admins/', rapport_carburant_mensuel_admins, name='rapport_carburant_mensuel_admins'),
    path('rapport_incident_conducteur_mensuel_admins/', rapport_incident_conducteur_mensuel_admins, name='rapport_incident_conducteur_mensuel_admins'),
    path('rapport_depense_mensuel-pdf/', rapport_depense_mensuel_pdf, name='rapport_depense_mensuel_pdf'),
    path('rapport_depense-pdf/', rapport_depense_pdf, name='rapport_depense_pdf'),
    path('rapport_carburant_mensuel-pdf/', rapport_carburant_mensuel_pdf, name='rapport_carburant_mensuel_pdf'),
    path('rapport_incident_conducteur_mensuel-pdf/', rapport_incident_conducteur_mensuel_pdf, name='rapport_incident_conducteur_mensuel_pdf'),
    path('reset_password_confirm/', CustomPasswordResetConfirmView, name='password_reset_confirms'),
    path('ChangerMotDePasseConducteur', ChangerMotDePasse_admin, name='ChangerMotDePasse_admin'),
    path('rapport_mensuel_pdf/', rapport_entretien_mensuel_pdf, name='rapport_entretien_mensuel_pdf'),
    path('rapport_entretien_mensuel_pdf/', rapport_entretien_mensuel_admins, name='rapport_entretien_mensuel_admins'),
    path('rapport_incident_vehicule_mensuel_admins/', rapport_incident_vehicule_mensuel_admins, name='rapport_incident_vehicule_mensuel_admins'),
    path('rapport_incident_vehicule_mensuel-pdf/', rapport_incident_vehicule_mensuel_pdf, name='rapport_incident_vehicule_mensuel_pdf'),
    path('Profil-Admin/', ProfilAdmin, name='ProfilAdmin'),
    path('details_arriver_admin/<int:etatarrive_id>/', details_arriver_admin, name='details_arriver_admin'),
    path('detail_incidents_interne-<int:pk>/', incident_interne_detail_admin, name='incident_interne_detail_admin'),
    path('detail_incidents_externe-<int:pk>/', incident_externe_detail_admin, name='incident_externe_detail_admin'),
    path('detail_incidents_externe-<int:pk>/', incident_externe_detail_admin, name='incident_externe_detail_admin'),
    path('incidents_search/', incidents_search, name='incidents_search'),
    path('incidents_externe_search/', incidents_externe_search, name='incidents_externe_search'),
    path('arrive_search/', arrive_search, name='arrive_search'),

]