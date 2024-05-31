from datetime import date, timezone

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta

from django.db.models import Subquery, Q, F
from Model.models import Demande_prolongement, EtatArrive, Incident, Deplacement, Vehicule, Photo, Entretien, Carburant, \
    Conducteur, Utilisateur


def accueil_data(request):
    prolongements_non_lus = None
    if request.user.is_authenticated:
        prolongements_non_lus = Demande_prolongement.objects.filter(
            conducteur=request.user.conducteur,
            lu=False
        ).exclude(
            accepter=False,
            refuser=False
        ).order_by(F('date_reponse').desc(nulls_last=True))
    else:
        prolongements_non_lus = Demande_prolongement.objects.none()
    deplacements_arrives_ids = EtatArrive.objects.values('deplacement_id')
    demande = Demande_prolongement.objects.filter(en_cours=True).order_by('-date_mise_a_jour')
    incidents = Incident.objects.filter(conducteur__isnull=False).exclude(
        deplacement__in=Subquery(deplacements_arrives_ids)).order_by('-date_mise_a_jour')
    aujourd_hui = date.today()
    demande_compte = Demande_prolongement.objects.filter(en_cours=True).order_by('-date_mise_a_jour').count()
    incidents_compte = Incident.objects.filter(conducteur__isnull=False).exclude(
        deplacement__in=Subquery(deplacements_arrives_ids)).order_by('-date_mise_a_jour').count()
    # total = demande_compte + incidents_compte
    deplacement = Deplacement.objects.filter(Q(date_depart__gt=aujourd_hui))
    nombre_deplacement = deplacement.count()
    deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)
    prolongement_encours = Demande_prolongement.objects.filter(en_cours=True)
    prolongement_encours_ids = prolongement_encours.values_list('deplacement_id', flat=True)
    nombre_prolongement = Deplacement.objects.filter(id__in=prolongement_encours_ids).count()
    deplacements = Deplacement.objects.filter(Q(date_depart__lte=aujourd_hui)).exclude(
        Q(id__in=deplacements_etat_arrive_ids))

    nombre_deplacement_en_cours = deplacements.count()

    date_actuelle = timezone.now().date()
    une_semaine_plus_tard = date_actuelle + timedelta(days=7)
    vehicules_proches_expiration = Vehicule.objects.filter(date_expiration_assurance__lte=une_semaine_plus_tard)
    assurance_compte = Vehicule.objects.filter(date_expiration_assurance__lte=une_semaine_plus_tard).count()
    vehicules_et_jours_restants = {}

    for vehicule in vehicules_proches_expiration:
        jours_restants = (vehicule.date_expiration_assurance - date_actuelle).days
        if jours_restants < 0:
            vehicules_et_jours_restants[vehicule] = {'jours_restants': -1, 'photo': None}
        elif jours_restants == 0:
            vehicules_et_jours_restants[vehicule] = {'jours_restants': 0, 'photo': None}
        else:
            vehicules_et_jours_restants[vehicule] = {'jours_restants': jours_restants, 'photo': None}
        try:
            photo_vehicule = Photo.objects.filter(vehicule=vehicule).first()
            if photo_vehicule:
                vehicules_et_jours_restants[vehicule]['photo'] = photo_vehicule
        except ObjectDoesNotExist:
            pass

    vehicules_proches_vidanges = Vehicule.objects.filter(kilometrage__gte=F('videnge') - 100)
    vidanges_compte = Vehicule.objects.filter(kilometrage__gte=F('videnge') - 100).count()

    vehicules_proches_vidange = {}

    for vehiculee in vehicules_proches_vidanges:
        if vehiculee:
            vehicules_proches_vidange[vehiculee] = {'photo': None}
        try:
            photo_vehicule = Photo.objects.filter(vehicule=vehiculee).first()
            if photo_vehicule:
                vehicules_proches_vidange[vehiculee]['photo'] = photo_vehicule
        except ObjectDoesNotExist:
            pass

    date_actuelle = timezone.now().date()
    une_semaine_plus_tard = date_actuelle + timedelta(days=7)
    vehicules_proches_expiration_technique = Vehicule.objects.filter(date_visite_technique__lte=une_semaine_plus_tard)
    technique_compte = Vehicule.objects.filter(date_visite_technique__lte=une_semaine_plus_tard).count()
    vehicules_et_jours_restants_technique = {}

    for vehicule in vehicules_proches_expiration_technique:
        jours_restants = (vehicule.date_visite_technique - date_actuelle).days
        if jours_restants < 0:
            vehicules_et_jours_restants_technique[vehicule] = {'jours_restants': -1, 'photo': None}
        elif jours_restants == 0:
            vehicules_et_jours_restants_technique[vehicule] = {'jours_restants': 0, 'photo': None}
        else:
            vehicules_et_jours_restants_technique[vehicule] = {'jours_restants': jours_restants, 'photo': None}
        try:
            photo_vehicule = Photo.objects.filter(vehicule=vehicule).first()
            if photo_vehicule:
                vehicules_et_jours_restants_technique[vehicule]['photo'] = photo_vehicule
        except ObjectDoesNotExist:
            pass

    totals = demande_compte + incidents_compte + assurance_compte + vidanges_compte + technique_compte

    aujourd_hui = date.today()
    une_semaine_avant = aujourd_hui - timedelta(days=7)
    incidents_interne = Incident.objects.filter(date_mise_a_jour__gte=une_semaine_avant, conducteur_id__isnull=True)
    incidents_externe = Incident.objects.filter(date_mise_a_jour__gte=une_semaine_avant, conducteur_id__isnull=False)
    nombre_incident_interne = incidents_interne.count()
    nombre_incident_externe = incidents_externe.count()

    entretien_list = Entretien.objects.all().order_by('-date_mise_a_jour')
    nombre_entretien = entretien_list.count()
    carburant_list = Carburant.objects.all().order_by('date_mise_a_jour')
    nombre_carburant = carburant_list.count()
    etatarrive = EtatArrive.objects.filter(date_arrive__gte=aujourd_hui - timedelta(days=7)).exclude(
        date_arrive__gt=aujourd_hui)
    nombre_etatarrive = etatarrive.count()
    utilisateurs = Utilisateur.objects.exclude(conducteur_id__isnull=True).filter(is_active=True)
    nombre_conducteurs = utilisateurs.count()
    vehicules_list = Vehicule.objects.filter(supprimer=False)
    nombre_vehicule = vehicules_list.count()
    conducteurs = Conducteur.objects.all()
    vehicules = Vehicule.objects.all()
    date_aujourdhui = date.today()
    etatarrives = EtatArrive.objects.all()
    for deplacement in deplacements:
        if deplacement.date_depart == date.today():
            deplacement.kilometrage_depart = deplacement.vehicule.kilometrage
            deplacement.save()
        # Définir une valeur par défaut si aucun véhicule n'est sélectionné
        for conducteur in conducteurs:
            deplacements = Deplacement.objects.filter(conducteur=conducteur)
            for deplacement in deplacements:
                if deplacement.date_depart <= date_aujourdhui and not etatarrives.filter(
                        deplacement=deplacement).exists():
                    conducteur.disponibilite = False
                    conducteur.save()
        for vehicule in vehicules:
            deplacements = Deplacement.objects.filter(vehicule=vehicule)
            for deplacement in deplacements:
                if deplacement.date_depart <= date_aujourdhui and not etatarrives.filter(
                        deplacement=deplacement).exists():
                    vehicule.disponibilite = False
                    vehicule.save()

    return {'demandes': demande, 'inciden': incidents, 'totals': totals, 'nombre_deplacement': nombre_deplacement,
            'nombre_deplacement_en_cours': nombre_deplacement_en_cours, 'nombre_prolongement': nombre_prolongement,
            'vehicules_et_jours_restants': vehicules_et_jours_restants,
            'vehicules_et_jours_restants_technique': vehicules_et_jours_restants_technique,
            'vehicules_proches_vidange': vehicules_proches_vidange, 'nombre_incident_externe': nombre_incident_externe,
            'nombre_incident_interne': nombre_incident_interne, 'nombre_entretien': nombre_entretien,
            'nombre_carburant': nombre_carburant, 'nombre_etatarrive': nombre_etatarrive,
            'nombre_conducteurs': nombre_conducteurs, 'nombre_vehicule': nombre_vehicule,
            'prolongements_non_lus': prolongements_non_lus}
