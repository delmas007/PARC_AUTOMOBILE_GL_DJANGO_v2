from urllib import request

from django.core.paginator import EmptyPage, Paginator
from django.db.models import Q, ExpressionWrapper, F, fields
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from Model.models import Carburant, Vehicule
from carburant.forms import ModifierCarburantForm, AjouterCarburantForm, CarburantSearchForm


# Create your views here.
def Ajouter_carburant(request):
    if request.method == 'POST':
        form = AjouterCarburantForm(request.POST)

        if form.is_valid():
            carburant = form.save(commit=False)
            carburant.utilisateur = request.user

            # Récupérer l'objet Véhicule associé au formulaire
            vehicule = form.cleaned_data.get('vehicule')


            if isinstance(vehicule, Vehicule):
                vehicule_id = vehicule.id
            else:
                return HttpResponseBadRequest("Véhicule non valide.")

            carburant.vehicule_id = vehicule_id

            type_carburant = vehicule.energie

            prix_carburant = type_carburant.prix
            carburant.type = type_carburant
            carburant.prix_total = carburant.quantite * prix_carburant
            carburant.save()

            messages.success(request, 'Enregistrement des coûts liés au carburant !')
            return redirect('carburant:Ajouter_carburant')
    else:
        form = AjouterCarburantForm()

    context = {'form': form}

    return render(request, 'Ajouter_carburant.html', context)


def liste_carburant(request):
    carburant_list = (
        Carburant.objects.all().annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )

    paginator = Paginator(carburant_list, 15)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        carburant_list = paginator.page(page)
    except EmptyPage:

        carburant_list = paginator.page(paginator.num_pages())

    return render(request, 'Liste_carburant.html', {'carburants': carburant_list})


def Modifier_carburant(request, pk):
    carburant = get_object_or_404(Carburant, pk=pk)

    if request.method == 'POST':
        form = ModifierCarburantForm(request.POST, instance=carburant)
        if form.is_valid():
            carburant = form.save(commit=False)
            carburant.prix_total = carburant.quantite * carburant.type.prix
            carburant.save()

            return redirect('carburant:Liste_carburant')
    else:
        form = ModifierCarburantForm(instance=carburant)

    context = {
        'form': form,
        'carburant': carburant,
    }

    return render(request, 'Modifier_carburant.html', context)


def carburant_search(request):
    form = CarburantSearchForm(request.GET)
    carburant = Carburant.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            entretien = carburant.filter(Q(type__nom__icontains=query) |
                                         Q(vehicule__marque__marque__icontains=query) |
                                         Q(vehicule__numero_immatriculation__icontains=query) |
                                         Q(vehicule__type_commercial__modele__icontains=query))

        context = {'entretiens': entretien, 'form': form}
        paginator = Paginator(entretien.order_by('date_mise_a_jour'), 5)
        try:
            page = request.GET.get("page")
            if not page:
                page = 1
            entretienss = paginator.page(page)
        except EmptyPage:
            entretienss = paginator.page(paginator.num_pages())
        context = {'entretiens': entretienss, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not entretien.exists() and form.is_valid():
            context['no_results'] = True

    return render(request, 'afficher_entretien.html', context)


def carburant_search(request):
    form = CarburantSearchForm(request.GET)
    carburant = (
        Carburant.objects.all().annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )
    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            carburant = carburant.filter(
                Q(vehicule__marque__marque__icontains=query) |
                Q(type__nom__icontains=query) |
                Q(vehicule__numero_immatriculation__icontains=query) |
                Q(vehicule__type_commercial__modele__icontains=query)

            )
    paginator = Paginator(carburant, 15)
    page = request.GET.get("page", 1)
    try:
        carburants = paginator.page(page)
    except EmptyPage:
        carburants = paginator.page(paginator.num_pages)

    context = {'carburants': carburants, 'form': form}

    # Ajouter la logique pour gérer les cas où aucun résultat n'est trouvé
    if carburant.count() == 0 and form.is_valid():
        context['no_results'] = True

    return render(request, 'Liste_carburant.html', context)


def details_carburant(request, pk):
    carburant = get_object_or_404(Carburant, id=pk)
    return render(request, 'carburant_details.html', {'carburant': carburant})


def get_TypeCarburant(request):
    vehicule_id = request.GET.get('vehicule_id')
    if vehicule_id:
        try:
            vehicule = Vehicule.objects.get(pk=vehicule_id)
            Type_de_carburant = vehicule.energie.nom
            return JsonResponse({'Type_de_carburant': Type_de_carburant})
        except Vehicule.DoesNotExist:
            return JsonResponse({'error': 'Véhicule non trouvé'}, status=404)
    else:
        return JsonResponse({'error': 'ID de véhicule non fourni'}, status=400)

