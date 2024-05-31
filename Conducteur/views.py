from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, ExpressionWrapper, F, fields
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from Model.forms import UserRegistrationForme, UserRegistrationFormee
from Model.models import Conducteur, Roles, Utilisateur
from .forms import ConducteurForm, ConducteurSearchForm


@login_required(login_url='Connexion')
def ajouter_conducteur(request):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        conducteur_form = ConducteurForm(request.POST, request.FILES)
        utilisateur_form = UserRegistrationForme(request.POST)
        if conducteur_form.is_valid() and utilisateur_form.is_valid():
            conducteur_instance = conducteur_form.save()
            utilisateur_instance = utilisateur_form.save(commit=False)
            utilisateur_role = Roles.objects.get(role=Roles.CONDUCTEUR)
            utilisateur_instance.roles = utilisateur_role
            utilisateur_instance.conducteur = conducteur_instance
            utilisateur_instance.save()
            messages.success(request, 'Le conducteur a été ajouté avec succès.')
            return redirect('conducteur:ajouter_conducteur')
        else:
            print(conducteur_form.errors)
            print(utilisateur_form.errors)
    else:
        conducteur_form = ConducteurForm()
        utilisateur_form = UserRegistrationForme()

    return render(request, 'ajouter_conducteur.html',
                  {'conducteur_form': conducteur_form, 'utilisateur_form': utilisateur_form})


@login_required(login_url='Connexion')
def tous_les_conducteurs(request):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    conducteurs = Conducteur.objects.all().order_by('date_mise_a_jour')
    utilisateurs = (
        Utilisateur.objects.exclude(conducteur_id__isnull=True).filter(is_active=True).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())).order_by('-hour')
        )

    paginator = Paginator(utilisateurs, 15)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        utilisateurs = paginator.page(page)
    except EmptyPage:
        utilisateurs = paginator.page(paginator.num_pages())

    return render(request, 'tous_les_conducteurs.html', {'conducteurs': conducteurs, 'utilisateurs': utilisateurs})


@login_required(login_url='Connexion')
def supprimer_conducteur(request, conducteur_id):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    utilisateurs = get_object_or_404(Utilisateur, conducteur=conducteur_id)
    conducteur = get_object_or_404(Conducteur, pk=conducteur_id)
    conducteur.supprimer = True
    conducteur.save()
    utilisateurs.is_active = False
    utilisateurs.save()
    return redirect('conducteur:tous_les_conducteurs')


@login_required(login_url='Connexion')
def modifier_conducteur(request, conducteur_id):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    global form
    conducteur = get_object_or_404(Conducteur, pk=conducteur_id)
    utilisateur = get_object_or_404(Utilisateur, conducteur=conducteur_id)
    if request.method == 'POST':
        form_conducteur = ConducteurForm(request.POST, request.FILES, instance=conducteur)
        form_utilisateur = UserRegistrationFormee(request.POST, instance=utilisateur)
        if form_conducteur.is_valid() and form_utilisateur.is_valid():
            conducteur = form_conducteur.save(commit=False)
            nouveau_fichier = request.FILES.get('image', None)
            if nouveau_fichier:
                conducteur.image = nouveau_fichier
            conducteur.save()
            form_utilisateur.save()
            return redirect('conducteur:tous_les_conducteurs')
    else:
        form = ConducteurForm(instance=conducteur, initial={
            'date_de_naissance': conducteur.date_de_naissance,
            'date_embauche': conducteur.date_embauche,
        })
    return render(request, 'modifier_conducteur.html',
                  {'form': form, 'conducteur': conducteur, 'utilisateur': utilisateur})


@login_required(login_url='Connexion')
def conducteur_search(request):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    form = ConducteurSearchForm(request.GET)
    utilisateurs = (
        Utilisateur.objects.exclude(conducteur_id__isnull=True).filter(is_active=True).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())).order_by('-hour')
        )

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            utilisateurs = utilisateurs.filter(
                Q(nom__icontains=query) |
                Q(prenom__icontains=query) |
                Q(conducteur__numero_permis_conduire__icontains=query)
            )
        else:
            utilisateurs = utilisateurs

        paginator = Paginator(utilisateurs, 15)
        page = request.GET.get('page')

        try:
            utilisateurs = paginator.page(page)
        except PageNotAnInteger:
            utilisateurs = paginator.page(1)
        except EmptyPage:
            utilisateurs = paginator.page(paginator.num_pages)

        context = {'utilisateurs': utilisateurs, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not utilisateurs and form.is_valid():
            context['no_results'] = True

    return render(request, 'tous_les_conducteurs.html', context)


@login_required(login_url='Connexion')
def details_conducteur(request, conducteur_id):
    if not request.user.roles or request.user.roles.role != 'GESTIONNAIRE':
        return redirect('utilisateur:erreur')
    conducteur = get_object_or_404(Conducteur, id=conducteur_id)
    utilisateur = get_object_or_404(Utilisateur, conducteur=conducteur_id)
    return render(request, 'conducteur_details.html', {'conducteur': conducteur, 'utilisateur': utilisateur})
