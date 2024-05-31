from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

from Model.forms import ConnexionForm, UserRegistrationForm
from Model.models import Roles


# Create your views here.

class Connexion(LoginView):
    template_name = 'connexion.html'
    form_class = ConnexionForm

    def get_success_url(self) -> str:
        if self.request.user.roles.role == 'ADMIN':
            return reverse('admins:dashboard_admins')
        elif self.request.user.roles.role == 'GESTIONNAIRE':
            return reverse('Accueil')


def deconnexion(request):
    logout(request)
    return redirect(reverse('utilisateur:connexion_user'))


class Deconnexion2(LogoutView):
    def get_success_url(self):
        return reverse('Connexion')
