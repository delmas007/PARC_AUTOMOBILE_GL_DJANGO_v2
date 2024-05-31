
from utilisateurs.views import Accueil_user, Connexion_user, Compte, vehicule_details, list_vehicule, liste_mission, prolongement, \
    liste_demandes, declare_incident, sendIncident, ChangerMotDePassee, ChangerMotDePasseConducteur, ProfilUser, \
    deplacement_s, erreur, dismiss_notification, prolongement_lu_details, detail_prolongement, ajouter_motif
from django.urls import path

app_name = 'utilisateur'

urlpatterns = [
    path('Accueil', Accueil_user, name='Accueil_user'),
    path('Vehicule', list_vehicule, name='list_vehicule'),
    path('Compte', Compte, name='compte'),
    # path('Inscription/', inscription_user, name='Inscription_user'),
    path('Connexion/', Connexion_user.as_view(), name='connexion_user'),
    path('Vehicule/<int:vehicule_id>/', vehicule_details, name='Vehicule_details'),
    # path('activate/<uidb64>/<token>', activate, name='activate'),
    # path("password_reset", password_reset_request, name="password_reset"),
    # path('reset/<uidb64>/<token>', passwordResetConfirm, name='réinitialisation'),
    path('compte/liste_mission/', liste_mission, name='liste_mission'),
    path('prolongement/', prolongement, name='prolongement'),
    path('compte/list_de_demande_prolongement/', liste_demandes, name='list_de_demande_prolongement'),
    path('compte/declare_incident/', declare_incident, name='declare_incident'),
    path('sendIncident/', sendIncident, name='sendIncident'),
    path('Profil/', ProfilUser, name='Profil_User'),
    path('Changer_mot_de_passe', ChangerMotDePassee, name='ChangerMotDePassee'),
    path('ChangerMotDePasseConducteur', ChangerMotDePasseConducteur, name='ChangerMotDePasseConducteur'),
    path('recherche_prolongement/<str:prolongement_nom>/', deplacement_s, name='prolongementt'),
    path('erreur/', erreur, name='erreur'),
    path('dismiss_notification/', dismiss_notification, name='dismiss_notification'),
    path('prolongement_lu_details/', prolongement_lu_details, name='prolongement_lu_details'),
    path('detail_mission/<int:deplacement_id>/', detail_prolongement, name='detail_prolongement'),
    path('ajouter_motif/', ajouter_motif, name='ajouter_motif'),

]
