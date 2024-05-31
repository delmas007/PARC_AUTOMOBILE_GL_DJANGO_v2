from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET
from Model.models import Deplacement, Photo, EtatArrive, Demande_prolongement, Conducteur, Vehicule
from deplacement.forms import DeplacementForm, deplacementModifierForm, EtatArriveForm, DeplacementSearchForm, \
    deplacementModifierForm_cours
from datetime import date, timedelta
from django.db.models import Q, Exists, OuterRef, ExpressionWrapper, F, fields
import json


@login_required(login_url='Connexion')
def enregistrer_deplacement(request):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')

    if request.method == 'POST':

        form = DeplacementForm(request.POST)
        if form.is_valid():

            deplacement = form.save(commit=False)

            deplacement.utilisateur = request.user

            # Obtenez l'instance du véhicule associé à ce déplacement (hypothétique)
            vehicule = deplacement.vehicule

            # Obtenez l'instance du conducteur associé à ce déplacement (hypothétique)
            conducteur = deplacement.conducteur

            photo_jauge_depart = request.FILES.get('photo_jauge_depart')
            if photo_jauge_depart:
                deplacement.photo_jauge_depart = photo_jauge_depart
            vehicule.save()
            deplacement.save()
            images = request.FILES.getlist('images')
            if len(images) <= 6:
                for uploaded_file in images:
                    photo = Photo.objects.create(deplacement=deplacement, images=uploaded_file)
            else:
                form.add_error('images', 'Vous ne pouvez sélectionner que 6 images.')

            messages.success(request, 'Déplacement enregistré avec succès !')
            return redirect('deplacement:enregistrer_deplacement')
    else:
        form = DeplacementForm()

    return render(request, 'enregistrer_deplacement.html', {'form': form})


@login_required(login_url='Connexion')
def liste_deplacement(request):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    aujourd_hui = date.today()
    deplacement = (
        Deplacement.objects.filter(Q(date_depart__gt=aujourd_hui)).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )
    deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)
    deplacements = Deplacement.objects.filter(Q(date_depart__lte=aujourd_hui)).exclude(
        Q(id__in=deplacements_etat_arrive_ids))
    paginator = Paginator(deplacement, 15)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        deplacement = paginator.page(page)
    except EmptyPage:

        deplacement = paginator.page(paginator.num_pages())
    return render(request, 'afficher_deplacement.html', {'deplacements': deplacement})


@login_required(login_url='Connexion')
def depart(request, pk):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    deplacement = get_object_or_404(Deplacement, pk=pk)
    deplacement.depart = True
    deplacement.statut = 'en cours'
    deplacement.save()  # Ligne corrigée
    return redirect('deplacement:liste_deplacement')


@login_required(login_url='Connexion')
def liste_deplacement_en_cours(request):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    aujourd_hui = date.today()
    prolongement = Demande_prolongement.objects.all()

    deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)
    deplacements = (
        Deplacement.objects.filter(Q(date_depart__lte=aujourd_hui)).exclude(
            Q(id__in=deplacements_etat_arrive_ids)).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )
    deplacement_ids = deplacements.values_list('id', flat=True)
    prolongement_encours = Demande_prolongement.objects.filter(en_cours=True)
    prolongement_arrive = Demande_prolongement.objects.filter(refuser=True)
    prolongement_accepte = Demande_prolongement.objects.filter(accepter=True)

    # recuperer liste des id de demandes de prolongement
    prolongement_encours_ids = prolongement_encours.values_list('deplacement_id', flat=True)
    prolongement_arrive_ids = prolongement_arrive.values_list('deplacement_id', flat=True)
    prolongement_accepte_ids = prolongement_accepte.values_list('deplacement_id', flat=True)

    paginator = Paginator(deplacements, 15)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        deplacement = paginator.page(page)
    except EmptyPage:

        deplacement = paginator.page(paginator.num_pages())
    return render(request, 'afficher_deplacement_en_cours.html',
                  {'deplacements': deplacement, 'prolongement_encours': prolongement_encours_ids,
                   'prolongement_arrive': prolongement_arrive_ids, 'prolongement_accepte': prolongement_accepte_ids,
                   'prolongements': prolongement, 'aujourd_hui': aujourd_hui,})


@login_required(login_url='Connexion')
def arrivee(request, pk):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    deplacement = get_object_or_404(Deplacement, pk=pk)
    deplacement.arrivee = True
    deplacement.statut = 'arrivée'
    deplacement.save()  # Ligne corrigée
    return redirect('deplacement:liste_deplacement_en_cours')


@login_required(login_url='Connexion')
def liste_deplacement_arrive(request):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    aujourd_hui = date.today()
    etatarrive = (
        EtatArrive.objects.filter(date_arrive__gte=aujourd_hui - timedelta(days=7)).exclude(
            date_arrive__gt=aujourd_hui).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )

    paginator = Paginator(etatarrive, 15)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        etatarrive = paginator.page(page)
    except EmptyPage:

        etatarrive = paginator.page(paginator.num_pages())
    return render(request, 'afficher_deplacement_arrive.html', {'etatarrives': etatarrive})


@login_required(login_url='Connexion')
def modifier_deplacement_cours(request, pk):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    deplacement = get_object_or_404(Deplacement, pk=pk)
    ancien_deplacement = get_object_or_404(Deplacement, pk=pk)
    photos = Photo.objects.filter(deplacement=pk)
    if request.method == 'POST':
        form = deplacementModifierForm_cours(request.POST, request.FILES, instance=deplacement)
        if form.is_valid():
            if ancien_deplacement.vehicule != deplacement.vehicule:
                ancien_deplacement.vehicule.disponibilite = True
                ancien_deplacement.vehicule.save()
            if ancien_deplacement.conducteur != deplacement.conducteur:
                ancien_deplacement.conducteur.disponibilite = True
                ancien_deplacement.conducteur.save()
            deplacement.kilometrage_depart = deplacement.vehicule.kilometrage
            deplacement.conducteur.disponibilite = False
            deplacement.conducteur.save()
            deplacement.vehicule.disponibilite = False
            deplacement.vehicule.save()
            form.save()

            return redirect('deplacement:liste_deplacement_en_cours')
    else:

        form = deplacementModifierForm_cours(instance=deplacement, initial={
            'vehicule': deplacement.vehicule,
            'conducteur': deplacement.conducteur,
        })
        # if deplacement.photo_jauge_depart:
        #     initial_data['photo_jauge_depart'] = deplacement.image_jauge

    return render(request, 'modifier_deplacement_cours.html',
                  {'form': form, 'deplacement': deplacement, 'photos': photos})


@login_required(login_url='Connexion')
def modifier_deplacement(request, pk):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    deplacement = get_object_or_404(Deplacement, pk=pk)
    ancien_deplacement = get_object_or_404(Deplacement, pk=pk)
    photos = Photo.objects.filter(deplacement=pk)
    if request.method == 'POST':
        form = deplacementModifierForm(request.POST, request.FILES, instance=deplacement)
        if form.is_valid():
            if request.FILES.getlist('images'):
                Photo.objects.filter(deplacement=deplacement).delete()
                for image in request.FILES.getlist('images'):
                    Photo.objects.create(deplacement=deplacement, images=image)
                if request.FILES.getlist('images'):
                    Photo.objects.filter(deplacement=deplacement).delete()
                    for image in request.FILES.getlist('images'):
                        Photo.objects.create(deplacement=deplacement, images=image)
            if ancien_deplacement.vehicule != deplacement.vehicule:
                ancien_deplacement.vehicule.disponibilite = True
                ancien_deplacement.vehicule.save()
            if ancien_deplacement.conducteur != deplacement.conducteur:
                ancien_deplacement.conducteur.disponibilite = True
                ancien_deplacement.conducteur.save()
            deplacement.kilometrage_depart = deplacement.vehicule.kilometrage
            form.save()

            return redirect('deplacement:liste_deplacement')
    else:

        form = deplacementModifierForm(instance=deplacement, initial={
            'vehicule': deplacement.vehicule,
            'conducteur': deplacement.conducteur,
            'date_depart': deplacement.date_depart,
            'duree_deplacement': deplacement.duree_deplacement,
            'kilometrage_depart': deplacement.vehicule.kilometrage,
            'photo_jauge_depart': deplacement.photo_jauge_depart,
            'description': deplacement.description
        })
        # if deplacement.photo_jauge_depart:
        #     initial_data['photo_jauge_depart'] = deplacement.image_jauge

    return render(request, 'modifier_deplacement.html', {'form': form, 'deplacement': deplacement, 'photos': photos})


@login_required(login_url='Connexion')
def details_deplacement(request, deplacement_id):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    deplacement = get_object_or_404(Deplacement, id=deplacement_id)
    image = Photo.objects.filter(deplacement=deplacement_id)
    return render(request, 'deplacement_details.html', {'deplacement': deplacement, 'image': image})


@login_required(login_url='Connexion')
def delete_deplacement(request, deplacement_id):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    deplacement = get_object_or_404(Deplacement, id=deplacement_id)
    image = Photo.objects.filter(deplacement=deplacement_id)
    image.delete()
    deplacement.delete()
    return redirect('deplacement:liste_deplacement')


@login_required(login_url='Connexion')
def delete_deplacement_cours(request, deplacement_id):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    deplacement = get_object_or_404(Deplacement, id=deplacement_id)
    deplacement.conducteur.disponibilite =True
    deplacement.conducteur.save()
    deplacement.vehicule.disponibilite =True
    deplacement.vehicule.save()
    image = Photo.objects.filter(deplacement=deplacement_id)
    image.delete()
    deplacement.delete()
    return redirect('deplacement:liste_deplacement_en_cours')


@login_required(login_url='Connexion')
def enregistrer_etatArriver(request):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        form = EtatArriveForm(request.POST)
        if form.is_valid():
            etat_arrive = form.save(commit=False)

            etat_arrive.utilisateur = request.user

            deplacement_id = form.cleaned_data['deplacement_id']

            deplacement = Deplacement.objects.get(id=deplacement_id)
            etat_arrive.deplacement = deplacement

            vehicule = etat_arrive.deplacement.vehicule
            conducteur = etat_arrive.deplacement.conducteur

            if vehicule:
                vehicule.disponibilite = True
                vehicule.kilometrage = etat_arrive.kilometrage_arrive
                vehicule.save()
            if conducteur:
                conducteur.disponibilite = True
                conducteur.save()
            photo_jauge_arrive = request.FILES.get('photo_jauge_arrive')
            if photo_jauge_arrive:
                etat_arrive.photo_jauge_arrive = photo_jauge_arrive
            etat_arrive.save()
            images = request.FILES.getlist('images')
            if len(images) <= 6:
                for uploaded_file in images:
                    photo = Photo.objects.create(etat_arrive=etat_arrive, images=uploaded_file)
            else:
                form.add_error('images', 'Vous ne pouvez sélectionner que 6 images.')
            return redirect('deplacement:liste_deplacement_en_cours')
        else:
            print(form.errors)
    else:
        form = EtatArriveForm()

    context = {'form': form}
    return render(request, 'afficher_deplacement_en_cours.html', context)


@login_required(login_url='Connexion')
def details_arriver(request, etatarrive_id):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    etat_arrive = get_object_or_404(EtatArrive, id=etatarrive_id)
    deplacement_id = etat_arrive.deplacement.id
    deplacement = get_object_or_404(Deplacement, id=deplacement_id)
    image = Photo.objects.filter(etat_arrive=etatarrive_id)
    images = Photo.objects.filter(deplacement=deplacement_id)
    return render(request, 'arriver_details.html',
                  {'etat_arrive': etat_arrive, 'deplacement': deplacement, 'image': image, 'images': images})


@require_GET
def get_deplacements_data(request):
    conducteur_id = request.GET.get('conducteur_id')
    # Vérifier si l'identifiant du conducteur est fourni
    if conducteur_id is not None:
        # Filtrer les déplacements pour ceux ayant l'ID du conducteur spécifié
        deplacements = Deplacement.objects.filter(conducteur_id=conducteur_id).annotate(
            has_etat_arrive=Exists(EtatArrive.objects.filter(deplacement_id=OuterRef('pk')))
        ).filter(has_etat_arrive=False).order_by('date_depart')
        data = [{'date_depart': deplacement.date_depart, 'duree_deplacement': deplacement.duree_deplacement}
                for deplacement in deplacements]
        return JsonResponse({'deplacements': data})
    else:
        return JsonResponse({'error': 'Identifiant du conducteur non spécifié'}, status=400)


def get_deplacements_data2(request):
    vehicule_id = request.GET.get('vehicule_id')
    # Vérifier si l'identifiant du conducteur est fourni
    if vehicule_id is not None:
        # Filtrer les déplacements pour ceux ayant l'ID du conducteur spécifié
        deplacements = Deplacement.objects.filter(vehicule_id=vehicule_id).annotate(
            has_etat_arrive=Exists(EtatArrive.objects.filter(deplacement_id=OuterRef('pk')))
        ).filter(has_etat_arrive=False).order_by('date_depart')
        data = [{'date_depart': deplacement.date_depart, 'duree_deplacement': deplacement.duree_deplacement}
                for deplacement in deplacements]
        return JsonResponse({'deplacements': data})
    else:
        return JsonResponse({'error': 'Identifiant du conducteur non spécifié'}, status=400)


# def get_info_prolongement(request):
#   if request.method == 'GET':
#      id_deplacement = request.GET.get('id_deplacement')
#     try:
#        demande_prolongement = Demande_prolongement.objects.get(deplacement_id=id_deplacement)
#       motif_prolongement = demande_prolongement.motif
#      duree_prolongement = demande_prolongement.duree
#     prolongement_id = demande_prolongement.id  # Récupérer l'ID de la demande de prolongement
#    return JsonResponse({'id': prolongement_id, 'motif': motif_prolongement, 'duree': duree_prolongement})
# except Demande_prolongement.DoesNotExist:
#    return JsonResponse({'error': 'Demande de prolongement non trouvée pour cet ID de déplacement.'}, status=404)
# else:
#    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)

def get_photos_demande_prolongement(request):
    if request.method == 'GET':
        id_deplacement = request.GET.get('id_deplacement')
        if id_deplacement is not None:
            try:
                demande_prolongement = Demande_prolongement.objects.get(deplacement_id=id_deplacement)
                photos = Photo.objects.filter(demande_prolongement=demande_prolongement)
                photo_urls = [photo.images.url for photo in photos]
                return JsonResponse({'photos': photo_urls})
            except Demande_prolongement.DoesNotExist:
                return JsonResponse({'error': 'Demande de prolongement non trouvée pour cet ID de déplacement.'},
                                    status=404)
        else:
            return JsonResponse({'error': 'L\'ID de déplacement est requis dans la requête.'}, status=400)
    else:
        return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)


@login_required(login_url='Connexion')
def accept_prolongement(request, prolongement_id):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    prolongement = get_object_or_404(Demande_prolongement, pk=prolongement_id)
    deplacement = Deplacement.objects.get(id=prolongement.deplacement.id)
    deplacement.duree_deplacement = deplacement.duree_deplacement + prolongement.duree
    prolongement.en_cours = False
    prolongement.refuser = False
    prolongement.accepter = True
    prolongement.date_reponse = timezone.now()
    deplacement.save()
    prolongement.save()
    return redirect('deplacement:liste_deplacement_en_cours')


@login_required(login_url='Connexion')
def refuse_prolongement(request, prolongement_id):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    prolongement = get_object_or_404(Demande_prolongement, pk=prolongement_id)
    prolongement.en_cours = False
    prolongement.refuser = True
    prolongement.accepter = False
    prolongement.date_reponse = timezone.now()
    prolongement.motif_refus = request.POST.get('motif_refus')
    prolongement.save()

    return redirect('deplacement:liste_deplacement_en_cours')


def deplacement_search(request):
    form = DeplacementSearchForm(request.GET)
    aujourdhui = date.today()
    deplacement = (
        Deplacement.objects.filter(Q(date_depart__gt=aujourdhui)).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            query_parts = query.split()
            if len(query_parts) > 1:
                nom = query_parts[0]  # First part is considered the last name (nom)
                prenoms = query_parts[1:]  # All parts except the first one are considered first names (prenoms)
                # Recherchez le nom
                deplacement = deplacement.filter(
                    Q(vehicule__marque__marque__icontains=query) |
                    Q(vehicule__numero_immatriculation__icontains=query) |
                    Q(vehicule__type_commercial__modele__icontains=query) |
                    Q(conducteur__utilisateur__nom__icontains=nom)
                )
                # Filter by each first name (prenoms)
                for prenom in prenoms:
                    deplacement = deplacement.filter(conducteur__utilisateur__prenom__icontains=prenom)
            else:
                # Si la requête ne contient pas exactement deux parties, recherchez normalement
                deplacement = deplacement.filter(
                    Q(vehicule__marque__marque__icontains=query) |
                    Q(vehicule__numero_immatriculation__icontains=query) |
                    Q(vehicule__type_commercial__modele__icontains=query) |
                    Q(conducteur__utilisateur__nom__icontains=query) |
                    Q(conducteur__utilisateur__prenom__icontains=query)
                )

    paginator = Paginator(deplacement, 15)
    page = request.GET.get("page", 1)
    try:
        deplacements = paginator.page(page)
    except EmptyPage:
        deplacements = paginator.page(paginator.num_pages)

    context = {'deplacements': deplacements, 'form': form}

    # Ajouter la logique pour gérer les cas où aucun résultat n'est trouvé
    if deplacement.count() == 0 and form.is_valid():
        context['no_results'] = True

    return render(request, 'afficher_deplacement.html', context)


def deplacement_encours_search(request):
    form = DeplacementSearchForm(request.GET)
    aujourdhui = date.today()
    deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)
    deplacement = (
        Deplacement.objects.filter(Q(date_depart__lte=aujourdhui)).exclude(
            Q(id__in=deplacements_etat_arrive_ids)).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )
    prolongement = Demande_prolongement.objects.all()

    deplacements = Deplacement.objects.filter(Q(date_depart__lte=aujourdhui)).exclude(
        Q(id__in=deplacements_etat_arrive_ids))
    deplacement_ids = deplacements.values_list('id', flat=True)
    prolongement_encours = Demande_prolongement.objects.filter(en_cours=True)
    prolongement_arrive = Demande_prolongement.objects.filter(refuser=True)
    prolongement_accepte = Demande_prolongement.objects.filter(accepter=True)

    # recuperer liste des id de demandes de prolongement
    prolongement_encours_ids = prolongement_encours.values_list('deplacement_id', flat=True)
    prolongement_arrive_ids = prolongement_arrive.values_list('deplacement_id', flat=True)
    prolongement_accepte_ids = prolongement_accepte.values_list('deplacement_id', flat=True)

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            query_parts = query.split()
            if len(query_parts) > 1:
                nom = query_parts[0]  # First part is considered the last name (nom)
                prenoms = query_parts[1:]  # All parts except the first one are considered first names (prenoms)
                # Recherchez le nom
                deplacement = deplacement.filter(
                    Q(vehicule__marque__marque__icontains=query) |
                    Q(vehicule__numero_immatriculation__icontains=query) |
                    Q(vehicule__type_commercial__modele__icontains=query) |
                    Q(conducteur__utilisateur__nom__icontains=nom)
                )
                # Filter by each first name (prenoms)
                for prenom in prenoms:
                    deplacement = deplacement.filter(conducteur__utilisateur__prenom__icontains=prenom)
            else:
                # Si la requête ne contient pas exactement deux parties, recherchez normalement
                deplacement = deplacement.filter(
                    Q(vehicule__marque__marque__icontains=query) |
                    Q(vehicule__numero_immatriculation__icontains=query) |
                    Q(vehicule__type_commercial__modele__icontains=query) |
                    Q(conducteur__utilisateur__nom__icontains=query) |
                    Q(conducteur__utilisateur__prenom__icontains=query)
                )

    paginator = Paginator(deplacement, 15)
    page = request.GET.get("page", 1)
    try:
        deplacements = paginator.page(page)
    except EmptyPage:
        deplacements = paginator.page(paginator.num_pages)

    context = {'deplacements': deplacements, 'form': form,
               'deplacement': deplacement, 'prolongement_encours': prolongement_encours_ids,
               'prolongement_arrive': prolongement_arrive_ids, 'prolongement_accepte': prolongement_accepte_ids,
               'prolongements': prolongement}

    # Ajouter la logique pour gérer les cas où aucun résultat n'est trouvé
    if deplacement.count() == 0 and form.is_valid():
        context['no_results'] = True

    return render(request, 'afficher_deplacement_en_cours.html', context)


def arrive_search(request):
    form = DeplacementSearchForm(request.GET)
    aujourd_hui = date.today()
    arrivee = (
        EtatArrive.objects.filter(date_arrive__gte=aujourd_hui - timedelta(days=7)).exclude(
            date_arrive__gt=aujourd_hui).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            query_parts = query.split()
            if len(query_parts) > 1:
                nom = query_parts[0]  # First part is considered the last name (nom)
                prenoms = query_parts[1:]  # All parts except the first one are considered first names (prenoms)

                arrivee = arrivee.filter(
                    Q(deplacement__vehicule__marque__marque__icontains=query) |
                    Q(deplacement__vehicule__numero_immatriculation__icontains=query) |
                    Q(deplacement__vehicule__type_commercial__modele__icontains=query) |
                    Q(deplacement__conducteur__utilisateur__nom__icontains=nom)
                )
                for prenom in prenoms:
                    arrivee = arrivee.filter(deplacement__conducteur__utilisateur__prenom__icontains=prenom)

            else:
                # Si la requête ne contient pas exactement deux parties, recherchez normalement
                arrivee = arrivee.filter(
                    Q(deplacement__vehicule__marque__marque__icontains=query) |
                    Q(deplacement__vehicule__numero_immatriculation__icontains=query) |
                    Q(deplacement__vehicule__type_commercial__modele__icontains=query) |
                    Q(deplacement__conducteur__utilisateur__nom__icontains=query) |
                    Q(deplacement__conducteur__utilisateur__prenom__icontains=query)
                )

    paginator = Paginator(arrivee, 15)
    page = request.GET.get("page", 1)
    try:
        etatarrives = paginator.page(page)
    except EmptyPage:
        etatarrives = paginator.page(paginator.num_pages)

    context = {'etatarrives': etatarrives, 'form': form}

    # Ajouter la logique pour gérer les cas où aucun résultat n'est trouvé
    if arrivee.count() == 0 and form.is_valid():
        context['no_results'] = True

    return render(request, 'afficher_deplacement_arrive.html', context)

# def get_kilometrage_actuel(request):
#     vehicule_id = request.GET.get('vehicule_id')
#     if vehicule_id:
#         try:
#             vehicule = Vehicule.objects.get(pk=vehicule_id)
#             kilometrage_actuel = vehicule.kilometrage
#             return JsonResponse({'kilometrage_actuel': kilometrage_actuel})
#         except Vehicule.DoesNotExist:
#             return JsonResponse({'error': 'Véhicule non trouvé'}, status=404)
#     else:
#         return JsonResponse({'error': 'ID de véhicule non fourni'}, status=400)
