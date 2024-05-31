from django.contrib.auth.decorators import login_required
from django.db.models import Q, ExpressionWrapper, F, fields
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy

from Model.models import Vehicule, Photo, Marque, Type_Commerciale
from vehicule.forms import VehiculeForm, VehiculSearchForm, marqueForm, VehiculeModifierForm, typeForm
from django.views.decorators.http import require_GET
from django.core.serializers import serialize


# Create your views here.

@login_required(login_url=reverse_lazy('Connexion'))
def Ajouter_vehicule(request):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        form = VehiculeForm(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('images')
            if len(images) <= 6:
                vehicule = form.save(commit=False)
                vehicule.utilisateur = request.user
                vehicule.save()
                for uploaded_file in images:
                    photo = Photo.objects.create(vehicule=vehicule, images=uploaded_file)

                messages.success(request, 'Le véhicule a été ajouté avec succès.')
                return redirect('vehicule:Ajouter_vehicule')
            else:
                form.add_error('images', 'Vous ne pouvez sélectionner que 6 images.')
        else:
            print(form.errors)

    else:
        form = VehiculeForm()

    marques = Marque.objects.all()
    return render(request, 'ajouter_vehicule.html', {'form': form, 'marques': marques})


@login_required(login_url=reverse_lazy('Connexion'))
def liste_vehicules(request):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    vehicules_list = (
        Vehicule.objects.filter(supprimer=False)
        .annotate(hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField()))
        .order_by('-hour')
    )

    paginator = Paginator(vehicules_list, 15)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        vehicules_list = paginator.page(page)
    except EmptyPage:

        vehicules_list = paginator.page(paginator.num_pages())

    return render(request, 'afficher_vehicule.html', {'vehicules': vehicules_list})


@login_required(login_url=reverse_lazy('Connexion'))
def vehicul_search(request):
    form = VehiculSearchForm(request.GET)
    vehicules = (
        Vehicule.objects.filter(supprimer=False).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            vehicules = vehicules.filter(Q(marque__marque__icontains=query) |
                                              Q(numero_immatriculation__icontains=query))
        else:
            vehicules = vehicules

        paginator = Paginator(vehicules, 15)
        try:
            page = request.GET.get("page")
            if not page:
                page = 1
            vehicules = paginator.page(page)
        except (EmptyPage, PageNotAnInteger):

            vehicules = paginator.page(paginator.num_pages())

        context = {'vehicules': vehicules, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not vehicules and form.is_valid():
            context['no_results'] = True

    return render(request, 'afficher_vehicule.html', context)


@login_required(login_url=reverse_lazy('Connexion'))
def supprimer_vehicule(request, pk):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    vehicule = get_object_or_404(Vehicule, pk=pk)
    vehicule.supprimer = True
    vehicule.save()
    return redirect('vehicule:liste_vehicules')


@login_required(login_url=reverse_lazy('Connexion'))
def modifier_vehicule(request, pk):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    vehicule = get_object_or_404(Vehicule, pk=pk)
    photos = Photo.objects.filter(vehicule=pk)

    if request.method == 'POST':
        form = VehiculeModifierForm(request.POST, request.FILES, instance=vehicule)
        if form.is_valid():
            if request.FILES.getlist('images'):
                # Supprimez les anciennes images du véhicule
                Photo.objects.filter(vehicule=vehicule).delete()
                # Ajoutez les nouvelles images au véhicule
                for image in request.FILES.getlist('images'):
                    Photo.objects.create(vehicule=vehicule, images=image)

            # Enregistrez le formulaire du véhicule mis à jour
            if 'energie' not in form.cleaned_data:
                form.cleaned_data['energie'] = vehicule.energie
            form.instance.utilisateur = request.user
            form.save()

            return redirect('vehicule:liste_vehicules')
    else:
        form = VehiculeModifierForm(instance=vehicule, initial={
            'date_mise_circulation': vehicule.date_mise_circulation.strftime('%Y-%m-%d') if vehicule.date_mise_circulation else None,
            'date_expiration_assurance': vehicule.date_expiration_assurance.strftime('%Y-%m-%d') if vehicule.date_expiration_assurance else None,
            'date_visite_technique': vehicule.date_visite_technique.strftime('%Y-%m-%d') if vehicule.date_visite_technique else None,
            'energie': vehicule.energie if vehicule.energie else None
        })

    return render(request, 'modifier_vehicule.html', {'form': form, 'vehicule': vehicule, 'photos': photos})


@login_required(login_url='Connexion')
def ajouter_marque(request):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        form = marqueForm(request.POST)
        if form.is_valid():
            marque = form.cleaned_data['marque']
            if Marque.objects.filter(marque=marque).exists():
                return JsonResponse({'error': 'Cette marque existe déjà.'}, status=400)
            form.save()
            return JsonResponse({'success': True})
        else:
            errors = dict(form.errors.items())
            print(form.errors)
            return JsonResponse({'errors': errors}, status=400)
    else:
        form = marqueForm()
    return render(request, 'ajouter_vehicule.html', {'form': form})


@login_required(login_url='Connexion')
def ajouter_type(request):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        form = typeForm(request.POST)
        if form.is_valid():
            marque_id = request.POST.get('marque_id')

            modele = form.cleaned_data['modele']
            if Type_Commerciale.objects.filter(modele=modele, marque_id=marque_id).exists():
                return JsonResponse({'error': 'Ce type commercial existe déjà.'}, status=400)
            form.save()
            return JsonResponse({'success': True})
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'errors': errors}, status=400)
    else:
        form = typeForm()
    return render(request, 'ajouter_vehicule.html', {'form': form})


@login_required(login_url=reverse_lazy('Connexion'))
def details_vehicule(request, vehicule_id):
    vehicule = get_object_or_404(Vehicule, id=vehicule_id)
    image = Photo.objects.filter(vehicule=vehicule_id)
    return render(request, 'vehicule_details.html', {'vehicule': vehicule, 'image': image})


@require_GET
def get_modeles(request):
    marque_id = request.GET.get('marque_id')
    modeles = Type_Commerciale.objects.filter(marque_id=marque_id)
    serialized_modeles = serialize('json', modeles)
    return JsonResponse({'modeles': serialized_modeles})
