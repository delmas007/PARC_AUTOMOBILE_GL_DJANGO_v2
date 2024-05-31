from datetime import date, timedelta
import os

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.serializers import serialize
from django.db.models import Subquery, Q, ExpressionWrapper, F, fields
from django.http import JsonResponse
from django.shortcuts import render, redirect

from Model.models import Demande_prolongement, EtatArrive, Conducteur, Vehicule, Deplacement, Utilisateur
from Model.models import Incident


@login_required(login_url='Connexion')
def Accueil(request):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)
    aujourd_hui = date.today()
    incidents_externe = Incident.objects.filter(conducteur_id__isnull=False).count()
    incidents_interne = Incident.objects.filter(conducteur_id__isnull=True).count()

    nombre_vehicules = Vehicule.objects.filter(supprimer=False).count()
    nombre_conducteurs = Utilisateur.objects.exclude(conducteur_id__isnull=True).filter(is_active=True).count()
    nombre_incidents = incidents_interne + incidents_externe
    nombre_deplacement_en_attente = Deplacement.objects.filter(Q(date_depart__gt=aujourd_hui)).count()
    nombre_deplacement_termine = Deplacement.objects.all().count()
    nombre_deplacements_en_cours = Deplacement.objects.filter(Q(date_depart__lte=aujourd_hui)).exclude(
        Q(id__in=deplacements_etat_arrive_ids)).count()

    deplacement_termine = (
                              EtatArrive.objects.filter(date_arrive__gte=aujourd_hui - timedelta(days=7)).exclude(
                                  date_arrive__gt=aujourd_hui).annotate(
                                  hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
                              ).order_by('-hour')
                          )[:2]

    deplacement_en_cours = (
                               Deplacement.objects.filter(Q(date_depart__lte=aujourd_hui)).exclude(
                                   Q(id__in=deplacements_etat_arrive_ids)).annotate(
                                   hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
                               ).order_by('-hour')
                           )[:2]

    deplacement_en_attente = (
                                 Deplacement.objects.filter(Q(date_depart__gt=aujourd_hui)).annotate(
                                     hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
                                 ).order_by('-hour')
                             )[:2]

    deplacements_planifies = Deplacement.objects.filter(date_depart__isnull=False)

    # Récupérer les véhicules disponibles
    vehicule_disponible = (
        Vehicule.objects.filter(disponibilite=True).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )
    # Configurer la pagination avec 6 véhicules par page
    paginator = Paginator(vehicule_disponible, 6)
    page = request.GET.get('page', 1)

    try:
        vehicules_page = paginator.page(page)
    except PageNotAnInteger:
        vehicules_page = paginator.page(1)
    except EmptyPage:
        vehicules_page = paginator.page(paginator.num_pages)

    context = {
        'nombre_vehicules': nombre_vehicules,
        'nombre_conducteurs': nombre_conducteurs,
        'nombre_deplacements_en_cours': nombre_deplacements_en_cours,
        'nombre_incidents': nombre_incidents,
        'nombre_deplacement_en_attente': nombre_deplacement_en_attente,
        'nombre_deplacement_termine': nombre_deplacement_termine,
        'vehicule_disponible': vehicules_page,
        'deplacements_planifies': deplacements_planifies,
        'now': aujourd_hui,
        'deplacement_termine': deplacement_termine,
        'deplacement_en_cours': deplacement_en_cours,
        'deplacement_en_attente': deplacement_en_attente,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        vehicules_json = list(vehicules_page.object_list.values())
        return JsonResponse({'vehicules': vehicules_json})

    return render(request, 'index.html', context)


def deplacements_planifies(request):
    deplacements_planifies = Deplacement.objects.filter(date_depart__isnull=False)
    out = []
    for event in deplacements_planifies:
        conducteur = event.conducteur  # Récupérer l'objet Conducteur associé à l'événement
        utilisateur = conducteur.utilisateur  # Récupérer l'objet Utilisateur associé au conducteur
        nom_conducteur = f"{utilisateur.nom} {utilisateur.prenom}" if utilisateur else ''

        out.append({
            'title': f"{event.vehicule.marque}-{event.vehicule.type_commercial}-{event.vehicule.numero_immatriculation}",
            'id': event.id,
            'start': event.date_depart.strftime("%m/%d/%Y, %H:%M:%S"),
            'duree': event.duree_deplacement,
            'conducteur': nom_conducteur
        })

    return JsonResponse(out, safe=False)


