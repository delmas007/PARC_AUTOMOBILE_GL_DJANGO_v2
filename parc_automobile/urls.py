"""
URL configuration for parc_automobile project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404
from Model.views import Connexion
from parc_automobile import settings
from parc_automobile.views import Accueil
from .views import deplacements_planifies

urlpatterns = [
                  path('Accueil', Accueil, name='Accueil'),
                  path('', Connexion.as_view(), name='Connexion'),
                  path('admins/', include('Admin.urls')),
                  path('user/', include('utilisateurs.urls')),
                  path('entretien/', include('entretien.urls')),
                  path('authentification/', include('Model.urls')),
                  path('vehicule/', include('vehicule.urls')),
                  path('deplacement/', include('deplacement.urls')),
                  path('incident/', include('incident.urls')),
                  path('carburant/', include('carburant.urls')),
                  path('admin/', admin.site.urls),
                  path('Conducteur/', include('Conducteur.urls'), name='Conducteur'),
                  path('deplacements_planifies/', deplacements_planifies, name='deplacements_planifies'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "incident.views.handler_404"
