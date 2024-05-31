from django.urls import path

from Model.views import deconnexion, Deconnexion2

app_name = 'Model'

urlpatterns = [
    # path('Connexion/', Connexion.as_view(), name='connexion'),
    path('Deconnexion/', deconnexion, name='deconnexion'),
    path('Deconnexion2/', Deconnexion2.as_view(), name='Deconnexion2'),

]
