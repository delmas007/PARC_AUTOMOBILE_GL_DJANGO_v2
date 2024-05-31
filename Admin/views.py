
from django.contrib.auth import update_session_auth_hash

from django.contrib import messages
from django.views.decorators.csrf import csrf_protect

from Admin.forms import typeCarburantForm, CarburantSearchForm, UserRegistrationForm
from Model.models import Roles, Utilisateur, type_carburant, periode_carburant
from deplacement.forms import DeplacementSearchForm
from utilisateurs.forms import ChangerMotDePasse
from vehicule.forms import VehiculSearchForm
from django.utils import formats
from django.utils.translation import gettext as _
from django.http import HttpResponse
from xhtml2pdf import pisa


import calendar
from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, ExpressionWrapper, fields, F, Sum, Subquery
from django.utils.translation import gettext as french
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from Model.models import Vehicule, Carburant, Entretien, Incident, Conducteur, EtatArrive, Photo, Deplacement
from incident.forms import IncidentSearchForm

@login_required(login_url='Connexion')
@csrf_protect
def inscription(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    context = {}
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            client_role = Roles.objects.get(role=Roles.GESTIONNAIRE)
            user.roles = client_role
            user.save()
            # Récupérez l'URL de l'image téléchargée
            image_url = user.image.url if user.image else None
            # Ajoutez l'URL de l'image au contexte
            context['user_image_url'] = image_url
            return redirect('admins:Compte_gestionnaire')
        else:
            context['form'] = form
            return render(request, 'ajouter_gestionnaire.html', context=context)

    form = UserRegistrationForm()
    context['form'] = form
    return render(request, 'ajouter_gestionnaire.html', context=context)


@login_required(login_url='Connexion')
def employer_compte(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    gestionnaires = Utilisateur.objects.filter(roles__role__in=[Roles.GESTIONNAIRE], is_active=True)

    return render(request, 'tous_les_gestionnaires.html', {'gestionnaires': gestionnaires})


def gestionnaire_inactifs(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    gestionnaires2 = Utilisateur.objects.filter(roles__role__in=[Roles.GESTIONNAIRE], is_active=False)
    return render(request, 'tous_les_gestionnairess.html', {'gestionnaires2': gestionnaires2})


@login_required(login_url='Connexion')
def active_emp(request, employer_id):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    employer = get_object_or_404(Utilisateur, id=employer_id)
    employer.is_active = True
    employer.save()
    return redirect('admins:gestionnaire_inactifs')


@login_required(login_url='Connexion')
def desactive_amp(request, employer_id):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    employer = get_object_or_404(Utilisateur, id=employer_id)
    employer.is_active = False
    employer.save()

    return redirect('admins:Compte_gestionnaire')


@login_required(login_url='Connexion')
def gestionnaire_a_search(request):
    form = VehiculSearchForm(request.GET)
    gestionnaire = Utilisateur.objects.filter(roles__role='GESTIONNAIRE').exclude(is_active=False)

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            gestionnaire = gestionnaire.filter(Q(nom__icontains=query) |
                                               Q(email__icontains=query) |
                                               Q(prenom__icontains=query))

        context = {'gestionnaires': gestionnaire, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not gestionnaire.exists() and form.is_valid():
            context['no_results'] = True

    return render(request, 'tous_les_gestionnaires.html', context)


@login_required(login_url='Connexion')
def gestionnaire_a_search_i(request):
    form = VehiculSearchForm(request.GET)
    gestionnaire = Utilisateur.objects.filter(roles__role='GESTIONNAIRE').exclude(is_active=True)

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            gestionnaire = gestionnaire.filter(Q(nom__icontains=query) |
                                               Q(email__icontains=query) |
                                               Q(prenom__icontains=query))

        context = {'gestionnaires2': gestionnaire, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not gestionnaire.exists() and form.is_valid():
            context['no_results'] = True

    return render(request, 'tous_les_gestionnairess.html', context)


@login_required(login_url='Connexion')
def Ajouter_Carburant(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        form = typeCarburantForm(request.POST)
        print(request.POST.get("nom"))
        carburant_id = request.POST.get("nom")
        carburant_prix = request.POST.get("prix")
        aujourdhui = date.today()
        if form.is_valid():

            carburant = type_carburant.objects.get(id=carburant_id)
            carburant.prix = carburant_prix
            carburant.save()
            dernier_periode = periode_carburant.objects.filter(carburant=carburant).order_by('-date_debut').first()
            if dernier_periode:

                periode = periode_carburant.objects.create(carburant=carburant, date_debut=carburant.date_mise_a_jour,
                                                           prix=carburant.prix)
                date_fin = carburant.date_mise_a_jour
                dernier_periode.date_fin = date_fin
                dernier_periode.save()
                periode.save()
            else:
                periode = periode_carburant.objects.create(carburant=carburant, date_debut=carburant.date_mise_a_jour,
                                                           prix=carburant.prix)
                periode.save()
            messages.success(request, "Carburant ajouté avec succès.")
            return redirect('admins:Ajouter_Carburant')
        else:
            print(form.errors)
    else:
        form = typeCarburantForm()
    return render(request, 'enregistrer_carburant.html', {'form': form})


@login_required(login_url='Connexion')
def liste_Carburant(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    carburant_list = (
        type_carburant.objects.all()
        .annotate(hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField()))
        .order_by('-hour')
    )

    paginator = Paginator(carburant_list, 5)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        carburants = paginator.page(page)
    except EmptyPage:

        carburants = paginator.page(paginator.num_pages())

    return render(request, 'afficher_carburant.html', {'carburants': carburants})


@login_required(login_url='Connexion')
def Carburant_search(request):
    form = CarburantSearchForm(request.GET)
    carburant = type_carburant.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            carburant = carburant.filter(Q(nom__icontains=query))

        context = {'carburants': carburant, 'form': form}
        paginator = Paginator(carburant.order_by('-date_mise_a_jour'), 5)
        try:
            page = request.GET.get("page")
            if not page:
                page = 1
            carburants = paginator.page(page)
        except EmptyPage:
            carburants = paginator.page(paginator.num_pages())
        context = {'carburants': carburants, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not carburant.exists() and form.is_valid():
            context['no_results'] = True

    return render(request, 'afficher_carburant.html', context)


@login_required(login_url='Connexion')
def dashboard_admins(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)
    aujourd_hui = date.today()
    nombre_deplacements_en_cours = Deplacement.objects.filter(Q(date_depart__lte=aujourd_hui)).exclude(
        Q(id__in=deplacements_etat_arrive_ids)).count()

    nombre_vehicules = Vehicule.objects.filter(supprimer=False).count()
    incidents_externe = Incident.objects.filter(conducteur_id__isnull=False).count()
    incidents_interne = Incident.objects.filter(conducteur_id__isnull=True).count()
    nombre_incidents = incidents_interne + incidents_externe
    vehicules_ids_with_carburant = Carburant.objects.values('vehicule_id').distinct()
    vehicles = Vehicule.objects.filter(id__in=Subquery(vehicules_ids_with_carburant))
    vehicules = Vehicule.objects.all()
    labels = [f"{vehicle.marque} {vehicle.type_commercial}" for vehicle in vehicles]
    mois = date.today().month
    mois_ = _(calendar.month_name[int(mois)])
    mois_lettre = mois_.upper()
    annee = date.today().year
    fuel_data = [vehicle.total_carburant(mois, annee) for vehicle in vehicles]
    quantites = [data['quantite'] for data in fuel_data]
    prix = [data['prix'] for data in fuel_data]

    types_carburant = type_carburant.objects.all()

    totals_carburant = []
    label = [carburant.nom for carburant in types_carburant]
    for carburant in types_carburant:
        total_quantite = Carburant.objects.filter(type=carburant).aggregate(Sum('quantite'))['quantite__sum'] or 0
        totals_carburant.append(total_quantite)
    deplacements_par_vehicule = []
    for vehicle in vehicules:
        total_deplacements_mois = vehicle.deplacement_set.filter(
            date_depart__month=mois,
            date_depart__year=annee,
            id__in=deplacements_etat_arrive_ids
        ).count()
        if total_deplacements_mois:
            deplacements_par_vehicule.append({'vehicle': vehicle, 'total_deplacements_mois': total_deplacements_mois})

    context = {
        'labels_circ': label,
        'labels': labels,
        'data': totals_carburant,
        'quantites': quantites,
        'prix': prix,
        'mois': mois_lettre,
        'nombre_vehicules': nombre_vehicules,
        'nombre_incidents': nombre_incidents,
        'nombre_deplacements_en_cours': nombre_deplacements_en_cours,
        'labels_entr': labels,
        'deplacements_par_vehicule': deplacements_par_vehicule,
    }

    return render(request, 'dashoard_admins.html', context)


@login_required(login_url='Connexion')
def rapport_depense_admins(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        return courbe_depense_global(request)
    vehicule = Vehicule.objects.all()
    context = {'vehicule': vehicule}
    return render(request, 'rapport_depense.html', context)


@login_required(login_url='Connexion')
def rapport_depense_mensuel_admins(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        return courbe_depense_mensuel(request)
    vehicule = Vehicule.objects.all()
    context = {'vehicule': vehicule}
    return render(request, 'rapport_depense_mensuel.html', context)


@login_required(login_url='Connexion')
def rapport_carburant_mensuel_admins(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        return rapport_carburant_mensuel(request)
    else:
        vehicules = Vehicule.objects.all()
        context = {'vehicules': vehicules}
        return render(request, 'rapport_carburant_mensuel.html', context)


@login_required(login_url='Connexion')
def rapport_incident_conducteur_mensuel_admins(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        return courbe_incident_conducteur_mensuel(request)
    conducteurs = Conducteur.objects.all()
    context = {'conducteurs': conducteurs}
    return render(request, 'rapport_incident_conducteur_mensuel.html', context)


def rapport_depense_mensuel_pdf(request):
    if request.method == 'POST':
        # Récupérez les données soumises du formulaire
        vehicule_id = request.POST.get('vehicule')
        mois = request.POST.get('mois')
        annee = request.POST.get('annee')
        mois_lettre = _(calendar.month_name[int(mois)])
        voitures = Vehicule.objects.all()
        variations = periode_carburant.objects.all()
        types = type_carburant.objects.all()
        if vehicule_id:
            vehicule = Vehicule.objects.get(id=vehicule_id)
            # Récupérer les données de carburant et d'entretien
            carburant = Carburant.objects.filter(vehicule=vehicule_id, date_premiere__month=mois,
                                                 date_premiere__year=annee)
            entretien = Entretien.objects.filter(vehicule=vehicule_id, date_entretien__month=mois,
                                                 date_entretien__year=annee)

            # Calculer les totaux de carburant et d'entretien
            total_carburant = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
            total_entretien = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            total_quantite = carburant.aggregate(Sum('quantite'))['quantite__sum'] or 0
            nbre_entretien = entretien.count()
            html_content = f"""
                       <html>
                       <head>
                       <title>Rapport</title>
                       <style>
                               table {{
                                   width: 100%;
                                   border-collapse: collapse;
                                   page-break-inside: avoid;
                               }}
                               th, td {{
                                   border: 1px solid black;
                                   padding: 8px;
                                   text-align: center;
                               }}
                               th {{
                                   background-color: #f2f2f2;
                               }}
                               h1, h2 {{
                                   text-align: center;
                               }}
                               .center {{
                                   text-align: center;
                               }}
                       </style>
                       </head>
                       <body class="center">
                       <h1>Rapport Dépenses de {mois_lettre} {annee}  de {vehicule}</h1>
                   """

            if carburant:
                html_content += "<h2>Carburant</h2>"
                html_content += """
                    <table border="1">
                    <tr><th>Date</th><th>Litre</th><th>Prix</th><th>Gestionnaire</th></tr>
                    """
                for essence in carburant:
                    date1 = essence.date_premiere
                    essence_date = formats.date_format(date1, format("l d F Y"))
                    html_content += f"""
                       <tr><td>{essence_date}</td><td>{essence.quantite}</td><td>{essence.prix_total}</td><td>{essence.utilisateur}</td></tr>
                   """
                html_content += f"""

                   <tr><td>Total</td><td>{total_quantite}</td><td>{total_carburant}</td></tr>
                    </table>
                   """
                variation_first = variations.filter(carburant_id=vehicule.energie.id, date_debut__month__lte=mois,
                                                    date_debut__year__lte=annee).order_by('date_debut')

                html_content += f"""
                   <br>
                   <br>
                   <br>
                   <h1>Variation des prix du {vehicule.energie.nom.upper()}</h1>
                   <table border="1">
                   <tr><th>Nom</th><th>Prix</th><th>Période</th></tr>
                   """
                for variation in variation_first:
                    date1 = variation.date_debut.date()
                    variation_date = formats.date_format(date1, format("l d F Y"))
                    date_fin_info = ""
                    if variation.date_fin:
                        date2 = variation.date_fin.date()
                        variation_fin = formats.date_format(date2, format("l d F Y"))
                        date_fin_info = f" au {variation_fin}"
                    if variation.date_fin:
                        if variation.date_fin.month == int(mois) and variation.date_fin.year == int(
                                annee) or not variation.date_fin:
                            html_content += f"""
                                          <tr><td>{variation.carburant.nom}</td><td>{variation.prix}</td><td>{variation_date} {date_fin_info}</td></tr>
                                                          """
                    else:
                        html_content += f"""
                                          <tr>
                                              <td>{variation.carburant.nom}</td>
                                              <td>{variation.prix}</td>
                                              <td>{variation_date} {date_fin_info}</td>
                                          </tr>
                                      """
                html_content += """
                              </table>"""

            else:
                html_content += "<p>Aucune donnée de carburant disponible.</p>"

            if entretien:
                html_content += "<h2>Entretien</h2>"
                html_content += """
                    <table border="1">
                    <tr><th>Date</th><th>Type</th><th>Prix</th><th>Gestionnaire</th></tr>
                    """
                for reparation in entretien:
                    date2 = reparation.date_entretien
                    reparation_date = formats.date_format(date2, format("l d F Y"))
                    html_content += f"""
                       <tr><td>{reparation_date}</td><td>{reparation.type}</td><td>{reparation.prix_entretient}</td><td>{reparation.utilisateur}</td></tr>
                   """
                html_content += f"""

                   <tr><td>Total</td><td>{nbre_entretien}</td><td>{total_entretien}</td></tr>
                    </table>
                   """
            else:
                html_content += "<p>Aucune donnée d'entretien disponible.</p>"

            if carburant and entretien:
                html_content += f"""
                   <table border="1" style="margin-top:20px">
                   <tr colspan="3"><td>TOTAL DÉPENSE</td><td>{total_entretien + total_carburant}</td></tr>
                    </table>
                              """

        else:
            carburant = Carburant.objects.filter(date_premiere__month=mois,
                                                 date_premiere__year=annee)
            entretien = Entretien.objects.filter(date_entretien__month=mois,
                                                 date_entretien__year=annee)
            nbre_deplacements = 0
            # Calculer les totaux de carburant et d'entretien
            total_carburant = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
            total_entretien = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            total_quantite = carburant.aggregate(Sum('quantite'))['quantite__sum'] or 0
            # Générer le contenu HTML du PDF
            html_content = f"""
               <html>
               <head>
               <title>Rapport PDF</title>
               <style>
                               table {{
                                   width: 100%;
                                   border-collapse: collapse;
                               }}
                               th, td {{
                                   border: 1px solid black;
                                   padding: 8px;
                                   text-align: center;
                               }}
                               th {{
                                   background-color: #f2f2f2;
                               }}
                               h1, h2 {{
                                   text-align: center;
                               }}
                               .center {{
                                   text-align: center;
                               }}
                </style>
               </head>
               <body class="center">
               <h1>Rapport Dépenses de {mois_lettre} {annee}</h1>
               <table border="1">
                <tr><th>Voitures</th><th>Nombre de déplacements</th><th>Quantitié Carburant</th><th>Montant Carburant</th><th>Nombre Entretien</th><th>Montant Entretien</th><th>Total</th></tr>
    
                   """
            # Vérifie si les listes de carburant ou d'entretien ne sont pas vides

            # Créer une liste pour stocker les lignes HTML
            rows = []

            # Boucler sur les voitures pour construire les lignes HTML
            for voiture in voitures:
                carburant = Carburant.objects.filter(vehicule=voiture, date_premiere__month=mois,
                                                     date_premiere__year=annee)
                carburant_vehicule = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
                carburant_quantite = carburant.aggregate(Sum('quantite'))['quantite__sum'] or 0
                entretien = Entretien.objects.filter(vehicule=voiture, date_entretien__month=mois,
                                                     date_entretien__year=annee)
                entretien_vehicule = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0

                deplacement = Deplacement.objects.filter(vehicule=voiture, date_depart__month=mois,
                                                         date_depart__year=annee).count()
                nbre_deplacements += deplacement
                nbre_entretien = entretien.count()
                nbres_entretien = nbre_entretien

                total = carburant_vehicule + entretien_vehicule
                html_row = f"<tr><td>{voiture}</td><td>{deplacement}</td><td>{carburant_quantite}</td><td>{carburant_vehicule}</td><td>{nbre_entretien}</td><td>{entretien_vehicule}</td><td>{total}</td></tr>"
                rows.append((total, html_row))  # Ajouter un tuple contenant le total et la ligne HTML

            # Trier les lignes par la somme des coûts de carburant et d'entretien (total) du plus grand au plus petit
            sorted_rows = sorted(rows, key=lambda x: x[0], reverse=True)

            # Construire le contenu HTML en utilisant les lignes triées
            html_content += "<table>"
            for total, html_row in sorted_rows:
                html_content += html_row

            # Fermer la table
            html_content += f"""
                <tr><td>Total</td><td>{nbre_deplacements}</td><td>{total_quantite}</td><td>{total_carburant}</td><td>{nbres_entretien}</td><td>{total_entretien}</td><td>{total_carburant + total_entretien}</td></tr>
                </table>
                </body>
                </html>
            """

            if carburant:
                for type in types:
                    variation_first = variations.filter(carburant=type, date_debut__month__lte=mois,
                                                        date_debut__year__lte=annee).order_by('date_debut')

                    html_content += f"""
                           <br>
                           <br>
                           <br>
                           <h1>VARIATION DES PRIX DU {type.nom.upper()}</h1>
                           <br>
                                                                                   <table border="1">
                                                                                   <tr><th>NOM</th><th>PRIX</th><th>PERIODE</th></tr>
                                                                                   """
                    for variation in variation_first:
                        date1 = variation.date_debut.date()
                        variation_date = formats.date_format(date1, format("l d F Y"))
                        date_fin_info = ""
                        if variation.date_fin:
                            date2 = variation.date_fin.date()
                            variation_fin = formats.date_format(date2, format("l d F Y"))
                            date_fin_info = f" au {variation_fin}"
                        if variation.date_fin:
                            if variation.date_fin.month == int(mois) and variation.date_fin.year == int(
                                    annee) or not variation.date_fin:
                                html_content += f"""
                                                                                    <tr><td>{variation.carburant.nom}</td><td>{variation.prix}</td><td>{variation_date} {date_fin_info}</td></tr>
                                                                                                    """
                        else:
                            html_content += f"""
                                                                                    <tr>
                                                                                        <td>{variation.carburant.nom}</td>
                                                                                        <td>{variation.prix}</td>
                                                                                        <td>{variation_date} {date_fin_info}</td>
                                                                                    </tr>
                                                                                """
                    html_content += f"""
                                                                        </table>"""

        # Créer un objet HttpResponse avec le contenu du PDF
        response = HttpResponse(content_type='application/pdf')
        if vehicule_id:
            vehicule = Vehicule.objects.get(id=vehicule_id)
            response[
                'Content-Disposition'] = f'inline; filename="Rapport Depense de {mois_lettre} {annee}  de {vehicule}.pdf"'
        else:
            response['Content-Disposition'] = f'inline; filename="Rapport Depenses de {mois_lettre} {annee}.pdf"'
        # Générer le PDF à partir du contenu HTML
        pisa_status = pisa.CreatePDF(html_content, dest=response)
        if pisa_status.err:
            return HttpResponse('Une erreur est survenue lors de la génération du PDF')

        return response


def rapport_depense_pdf(request):
    if request.method == 'POST':
        # Récupérez les données soumises du formulaire
        vehicule_id = request.POST.get('vehicule')
        debut = request.POST.get('date_debut_periode')
        fin = request.POST.get('date_fin_periode')
        voitures = Vehicule.objects.all()
        debut_date = datetime.strptime(debut, '%Y-%m-%d').date()
        date_debut = formats.date_format(debut_date, format("l d F Y"))
        variations = periode_carburant.objects.all()
        types = type_carburant.objects.all()

        if fin:
            fin_date = datetime.strptime(fin, '%Y-%m-%d').date()
            date_fin = formats.date_format(fin_date, format("l d F Y"))
        else:
            fin_date = date.today()
            date_fin = formats.date_format(fin_date, format("l d F Y"))
        if vehicule_id:

            vehicule = Vehicule.objects.get(id=vehicule_id)
            carburants = Carburant.objects.filter(vehicule=vehicule,
                                                  date_premiere__range=(debut_date, fin_date))
            entretiens = Entretien.objects.filter(vehicule=vehicule, date_entretien__range=(debut_date, fin_date))
            total_carburant = carburants.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
            total_entretien = entretiens.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            total_quantite = carburants.aggregate(Sum('quantite'))['quantite__sum'] or 0
            nbre_entretien = entretiens.count()
            html_content = f"""
                               <html>
                               <head>
                               <title>Rapport</title>
                               <style>
                                    table {{
                                       width: 100%;
                                       border-collapse: collapse;
                                       page-break-inside: avoid;
                                    }}
                                    th, td {{
                                        border: 1px solid black;
                                        padding: 8px;
                                        text-align: center;
                                    }}
                                    th {{
                                        background-color: #f2f2f2;
                                    }}
                                    h1, h2 {{
                                    text-align: center;
                                    }}
                                    .center {{
                                        text-align: center;
                                    }}
                               </style>
                               </head>
                               <body class="center">
                               <h1>Rapport Depense du {date_debut} au {date_fin}  de {vehicule}</h1>
                           """

            if carburants:
                html_content += "<h2>Carburant</h2>"
                html_content += """
                            <table border="1">
                            <tr><th>Date</th><th>Litre</th><th>Prix</th><th>Gestionnaire</th></tr>
                            """
                for essence in carburants:
                    date_essence = essence.date_premiere
                    essence_date = formats.date_format(date_essence, format("l d F Y"))
                    html_content += f"""
                               <tr><td>{essence_date}</td><td>{essence.quantite}</td><td>{essence.prix_total}</td><td>{essence.utilisateur}</td></tr>
                           """
                html_content += f"""

                           <tr><td>Total</td><td>{total_quantite}</td><td>{total_carburant}</td></tr>
                            </table>
                           """
                variation_first = variations.filter(carburant_id=vehicule.energie.id,
                                                    date_debut__lte=fin_date).order_by('date_debut')

                html_content += f"""
                               <br>
                               <br>
                               <br>
                               <h1> VARIATION DES PRIX DU {vehicule.energie.nom.upper()}</h1>
                                                                                <table border="1">
                                                                                <tr><th>NOM</th><th>PRIX</th><th>PERIODE</th></tr>
                                                                                """
                for variation in variation_first:
                    date1 = variation.date_debut.date()
                    variation_date = formats.date_format(date1, format("l d F Y"))
                    date_fin_info = ""
                    if variation.date_fin:
                        date2 = variation.date_fin.date()
                        variation_fin = formats.date_format(date2, format("l d F Y"))
                        date_fin_info = f" au {variation_fin}"
                    if variation.date_fin:
                        if debut_date <= variation.date_fin.date() <= fin_date or not variation.date_fin:
                            html_content += f"""
                                                      <tr><td>{variation.carburant.nom}</td><td>{variation.prix}</td><td>{variation_date} {date_fin_info}</td></tr>
                                                                      """
                    else:
                        html_content += f"""
                                                      <tr>
                                                          <td>{variation.carburant.nom}</td>
                                                          <td>{variation.prix}</td>
                                                          <td>{variation_date} {date_fin_info}</td>
                                                      </tr>
                                                  """
                html_content += f"""
                                          </table>"""
            else:
                html_content += "<p>Aucune donnée de carburant disponible.</p>"

            if entretiens:
                html_content += "<h2>Entretien</h2>"
                html_content += """
                            <table border="1">
                            <tr><th>Date</th><th>Type</th><th>Prix</th><th>Gestionnaire</th></tr>
                            """
                for reparation in entretiens:
                    date1 = reparation.date_entretien
                    reparation_date = formats.date_format(date1, format("l d F Y"))

                    html_content += f"""
                               <tr><td>{reparation_date}</td><td>{reparation.type}</td><td>{reparation.prix_entretient}</td><td>{reparation.utilisateur}</td></tr>
                           """
                html_content += f"""

                           <tr><td>Total</td><td>{nbre_entretien}</td><td>{total_entretien}</td></tr>
                            </table>
                           """
            if carburants and entretiens:
                html_content += f"""
                <table border="1" style="margin-top:20px">
                <tr colspan="3"><td>TOTAL DEPENSE</td><td>{total_entretien + total_carburant}</td></tr>
                 </table>
                           """
            else:
                html_content += "<p>Aucune donnée d'entretien disponible.</p>"
        else:
            carburant = Carburant.objects.filter(date_premiere__range=(debut_date, fin_date))
            entretien = Entretien.objects.filter(date_entretien__range=(debut_date, fin_date))
            nbre_deplacements = 0
            nbres_entretien = 0
            # Calculer les totaux de carburant et d'entretien
            total_carburant = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
            total_entretien = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            total_quantite = carburant.aggregate(Sum('quantite'))['quantite__sum'] or 0
            # Générer le contenu HTML du PDF
            html_content = f"""
                   <html>
                   <head>
                   <title>Rapport PDF</title>
                   <style>
                            table {{
                                width: 100%;
                                border-collapse: collapse;
                            }}
                            th, td {{
                                border: 1px solid black;
                                padding: 8px;
                                text-align: center;
                            }}
                            th {{
                                background-color: #f2f2f2;
                            }}
                            h1, h2 {{
                                text-align: center;
                            }}
                            .center {{
                                text-align: center;
                            }}
                   </style>
                   </head>
                   <body class="center">
                  <h1>Rapport Depense du {date_debut} à {date_fin}</h1> <table border="1"> 
                  <tr><th>Voitures</th><th>Nombre de deplacements</th><th>Quantitié de carburant</th><th>Montant Carburant</th><th>Nombre 
                  entretien</th><th>Montant Entretien</th><th>Total</th></tr>

                   """
            # Créer une liste pour stocker les lignes HTML
            rows = []

            # Boucle sur les voitures pour construire les lignes HTML
            for voiture in voitures:
                carburant = Carburant.objects.filter(vehicule=voiture, date_premiere__range=(debut_date, fin_date))
                carburant_vehicule = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
                entretien = Entretien.objects.filter(vehicule=voiture, date_entretien__range=(debut_date, fin_date))
                entretien_vehicule = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
                total = carburant_vehicule + entretien_vehicule
                nbre_entretien = entretien.count()
                deplacement = Deplacement.objects.filter(vehicule=voiture,
                                                         date_depart__range=(debut_date, fin_date)).count()
                carburant_quantite = carburant.aggregate(Sum('quantite'))['quantite__sum'] or 0
                html_row = f"""<tr> <td> {voiture} </td><td> {deplacement} </td><td> {carburant_quantite} </td><td>{carburant_vehicule}</td><td>{nbre_entretien}</td><td>{entretien_vehicule}</td><td>{total}</td></tr>"""
                rows.append((total, html_row))  # Ajouter un tuple contenant le total et la ligne HTML

            # Trier les lignes par la somme des coûts de carburant et d'entretien (total) du plus grand au plus petit
            sorted_rows = sorted(rows, key=lambda x: x[0], reverse=True)

            # Construire le contenu HTML en utilisant les lignes triées
            html_content += "<table>"
            for total, html_row in sorted_rows:
                html_content += html_row

            # Fermer la table
            html_content += f"""
                <tr><td>Total</td><td>{nbre_deplacements}</td><td>{total_quantite}</td><td>{total_carburant}</td><td>{nbres_entretien}</td><td>{total_entretien}</td><td>{total_carburant + total_entretien}</td></tr>
                </table>
                </body>
                </html>
            """
            if carburant:
                for type in types:
                    variation_first = variations.filter(carburant=type, date_debut__lte=fin_date).order_by('date_debut')

                    html_content += f"""
                    <br>
                    <br>
                    <br>
                    <h1>VARIATION DES PRIX DU {type.nom.upper()}</h1>
                    <br>
                                                                                        <table border="1">
                                                                                        <tr><th>NOM</th><th>PRIX</th><th>PRERIODE</th></tr>
                                                                                        """
                    for variation in variation_first:
                        date1 = variation.date_debut.date()
                        variation_date = formats.date_format(date1, format("l d F Y"))
                        date_fin_info = ""
                        if variation.date_fin:
                            date2 = variation.date_fin.date()
                            variation_fin = formats.date_format(date2, format("l d F Y"))
                            date_fin_info = f" au {variation_fin}"
                        if variation.date_fin:
                            if debut_date <= variation.date_fin.date() <= fin_date or not variation.date_fin:
                                html_content += f"""
                                                                             <tr><td>{variation.carburant.nom}</td><td>{variation.prix}</td><td>{variation_date} {date_fin_info}</td></tr>
                                                                                             """
                        else:
                            html_content += f"""
                                                                             <tr>
                                                                                 <td>{variation.carburant.nom}</td>
                                                                                 <td>{variation.prix}</td>
                                                                                 <td>{variation_date} {date_fin_info}</td>
                                                                             </tr>
                                                                         """
                    html_content += f"""
                                                                 </table>"""

        response = HttpResponse(content_type='application/pdf')
        if vehicule_id:
            vehicule = Vehicule.objects.get(id=vehicule_id)
            response[
                'Content-Disposition'] = f'inline; filename="Rapport Depense de {debut_date} à {fin_date}  de {vehicule}.pdf"'
        else:
            response['Content-Disposition'] = f'inline; filename="Rapport Depense de {debut_date} à {fin_date}.pdf"'
        # Générer le PDF à partir du contenu HTML
        pisa_status = pisa.CreatePDF(html_content, dest=response)
        if pisa_status.err:
            return HttpResponse('Une erreur est survenue lors de la génération du PDF')

        return response


@login_required(login_url='Connexion')
def CustomPasswordResetConfirmView(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        username = request.POST.get('username')
        passe = request.POST.get('new_password')
        passe2 = request.POST.get('new_password2')

        try:
            # Rechercher l'utilisateur par nom d'utilisateur
            user = Utilisateur.objects.get(username=username)
        except Utilisateur.DoesNotExist:
            user = None
        if not user:
            messages.error(request, "L'utilisateur n'existe pas")
            return redirect('admins:password_reset_confirms')
        if passe == passe2:
            new_password = passe
            user.set_password(new_password)
            user.save()
            messages.success(request, "Mot de passe réinitialisé avec succès.")
        else:
            messages.error(request, "Les mots de passe ne correspondent pas.")
        update_session_auth_hash(request, user)

        return redirect('admins:password_reset_confirms')
    else:
        return render(request, 'reinitialiser.html')


@login_required(login_url='Connexion')
def ChangerMotDePasse_admin(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        form = ChangerMotDePasse(request.user, request.POST)
        if request.user.check_password(request.POST.get('passe')):
            if form.is_valid():
                form.save()
                messages.success(request, "Votre mot de passe a été changer.")
                return redirect('Connexion')
            else:
                messages.error(request, "Les deux mots de passe ne correspondent pas")
        else:
            messages.error(request, "Le mot de passe actuel est incorrect.")
    form = ChangerMotDePasse(request.user)
    return render(request, 'changerMotDePasse_admin.html', {'form': form})


def rapport_carburant_mensuel_pdf(request):
    if request.method == 'POST':
        # Récupérez les données soumises du formulaire
        vehicule_id = request.POST.get('vehicule')
        mois = request.POST.get('mois')
        annee = request.POST.get('annee')
        mois_lettre = _(calendar.month_name[int(mois)])
        voitures = Vehicule.objects.all()
        variations = periode_carburant.objects.all()
        types = type_carburant.objects.all()
        if vehicule_id:

            carburant = Carburant.objects.filter(vehicule=vehicule_id, date_premiere__month=mois,
                                                 date_premiere__year=annee)

            vehicule = Vehicule.objects.get(id=vehicule_id)

            deplacement = Deplacement.objects.filter(vehicule=vehicule, date_depart__month=mois,
                                                     date_depart__year=annee).order_by('date_depart')
            if deplacement:
                deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)

                deplacement_first = deplacement.first()

                deplacement_last = deplacement.filter(id__in=deplacements_etat_arrive_ids).last()
                if deplacement_last:
                    arrive = EtatArrive.objects.filter(deplacement=deplacement_last.id, date_arrive__month=mois,
                                                       date_arrive__year=annee).last()

                    total_kilometrage = arrive.kilometrage_arrive - deplacement_first.kilometrage_depart

            # Calculer les totaux de carburant et d'entretien
            total_carburant = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
            total_quantite = carburant.aggregate(Sum('quantite'))['quantite__sum'] or 0

            html_content = f"""
                       <html>
                       <head>
                       <title>Rapport</title>
                       <style>
                               table {{
                                   width: 100%;
                                   border-collapse: collapse;

                               }}
                               th, td {{
                                   border: 1px solid black;
                                   padding: 8px;
                                   text-align: center;
                               }}
                               th {{
                                   background-color: #f2f2f2;
                               }}
                               h1, h2 {{
                                   text-align: center;
                               }}
                               .center {{
                                   text-align: center;
                               }}
                       </style>
                       </head>
                       <body class="center">
                       <h1>Rapport Carburant de {mois_lettre} {annee}  de {vehicule}</h1>
                   """

            if carburant:
                html_content += """
                    <table border="1">
                    <tr><th>Date</th><th>Litre</th><th>Prix</th><th>Gestionnaire</th></tr>
                    """
                for essence in carburant:
                    date = essence.date_premiere
                    essence_date = formats.date_format(date, format="l d F Y")
                    html_content += f"""
                       <tr><td>{essence_date}</td><td>{essence.quantite} LITRES</td><td>{essence.prix_total} FCFA</td><td>{essence.utilisateur}</td></tr>
                   """
                if deplacement:
                    if deplacement_last:
                        html_content += f"""

                           <tr><td>Total</td><td>{total_quantite} LITRES</td><td>{total_carburant} FCFA</td></tr>
                            <tr> <td colspan="4"><h2>KILOMETRAGE DU VEHICULE:{total_kilometrage}</h2></tr>
                            </table>
                           """
                    else:
                        html_content += f"""
                           <tr><td>Total</td><td>{total_quantite} LITRES</td><td>{total_carburant} FCFA</td></tr>
                            <tr> <td colspan="4"><h2>Deplacement en cours</h2></tr>
                            </table>
                            <br>
                            <br>
                            <br>
                           """
                else:
                    html_content += f"""
                           <tr><td>Total</td><td>{total_quantite} LITRES</td><td>{total_carburant} FCFA</td></tr>
                            <tr> <td colspan="4"><h2>Aucun déplacement effectué</h2></tr>
                            </table>
                            <br>
                            <br>
                            <br>
                           """
                variation_first = variations.filter(carburant_id=vehicule.energie.id, date_debut__month__lte=mois,
                                                    date_debut__year__lte=annee).order_by('date_debut')

                html_content += f"""
                   <h1>VARIATION DES PRIX DU {vehicule.energie.nom.upper()}</h1>
                                                     <table border="1">
                                                     <tr><th>NOM</th><th>PRIX</th><th>PERIODE</th></tr>
                                                     """
                for variation in variation_first:
                    date = variation.date_debut.date()
                    variation_date = formats.date_format(date, format="l d F Y")
                    date_fin_info = ""
                    if variation.date_fin:
                        date2 = variation.date_fin.date()
                        variation_fin = formats.date_format(date2, format="l d F Y")
                        date_fin_info = f" au {variation_fin}"
                    if variation.date_fin:
                        if variation.date_fin.month == int(mois) and variation.date_fin.year == int(
                                annee) or not variation.date_fin:
                            html_content += f"""
                                          <tr><td>{variation.carburant.nom}</td><td>{variation.prix} FCFA</td><td>{variation_date} {date_fin_info}</td></tr>
                                                          """
                    else:
                        html_content += f"""
                                          <tr>
                                              <td>{variation.carburant.nom}</td>
                                              <td>{variation.prix} FCFA</td>
                                              <td>{variation_date} {date_fin_info}</td>
                                          </tr>
                                      """
                html_content += f"""
                              </table>"""
            else:
                html_content += "<p>Aucune donnée de carburant disponible.</p>"
        else:
            # Générer le contenu HTML du PDF
            html_content = f"""
               <html>
               <head>
               <title>Rapport PDF</title>
               <style>
                               table {{
                                   width: 100%;
                                   border-collapse: collapse;
                                    page-break-inside: avoid;
                               }}
                               th, td {{
                                   border: 1px solid black;
                                   padding: 8px;
                                   text-align: center;
                               }}
                               th {{
                                   background-color: #f2f2f2;
                               }}
                               h1, h2 {{
                                   text-align: center;
                               }}
                               .center {{
                                   text-align: center;
                               }}
               </style>
               </head>
               <body class="center">
               <h1>Rapport Carburant de {mois_lettre} {annee}</h1>

               """
            carburant = Carburant.objects.filter(date_premiere__month=mois,
                                                 date_premiere__year=annee)

            # Calculer les totaux de carburant et d'entretien

            for voiture in voitures:
                carburant_voiture = carburant.filter(vehicule=voiture, date_premiere__month=mois,
                                                     date_premiere__year=annee)

                html_content += f"""
                                              <h1>Rapport  de {voiture}</h1>
                                            """

                # Vérifier s'il y a des données de carburant pour ce véhicule
                if carburant_voiture:
                    html_content += f"""
                                <table border="1">
                                <tr><th>Date</th><th>Litre</th><th>Prix</th><th>Gestionnaire</th></tr>
                            """

                    for essence in carburant_voiture:
                        if voiture == essence.vehicule:
                            deplacement = Deplacement.objects.filter(vehicule=voiture, date_depart__month=mois,
                                                                     date_depart__year=annee).order_by('date_depart')
                            if deplacement:
                                deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id',
                                                                                              flat=True)

                                deplacement_first = deplacement.first()

                                deplacement_last = deplacement.filter(id__in=deplacements_etat_arrive_ids).last()
                                if deplacement_last:
                                    arrive = EtatArrive.objects.filter(deplacement=deplacement_last.id,
                                                                       date_arrive__month=mois,
                                                                       date_arrive__year=annee).last()

                                    total_kilometrage = arrive.kilometrage_arrive - deplacement_first.kilometrage_depart
                            total_carburant = carburant_voiture.filter(vehicule=voiture).aggregate(Sum('prix_total'))[
                                                  'prix_total__sum'] or 0
                            total_quantite = carburant_voiture.filter(vehicule=voiture).aggregate(Sum('quantite'))[
                                                 'quantite__sum'] or 0
                            date = essence.date_premiere
                            essence_date = formats.date_format(date, format="l d F Y")
                            html_content += f"""
                                           <tr><td>{essence_date}</td><td>{essence.quantite} LITRES</td><td>{essence.prix_total} FCFA</td><td>{essence.utilisateur}</td></tr>
                                       """

                    if deplacement:
                        if deplacement_last:
                            html_content += f"""
                               <tr><td>Total</td><td>{total_quantite} LITRES</td><td>{total_carburant} FCFA</td></tr>
                            <tr> <td colspan="4"><h2>KILOMETRAGE DU VEHICULE:{total_kilometrage}</h2></tr>
                            </table>
                           """

                        else:
                            html_content += f"""
                                           <tr><td>Total</td><td>{total_quantite} LITRES</td><td>{total_carburant} FCFA</td></tr>
                                            <tr> <td colspan="4"><h2>Deplacement en cours</h2></tr>
                                            </table>
                                           """
                    else:
                        html_content += f"""
                               <tr><td>Total</td><td>{total_quantite} LITRES</td><td>{total_carburant} FCFA</td></tr>
                            <tr> <td colspan="4"><h2>Aucun deplacement effectué.</h2></tr>
                            </table>
                           """


                else:
                    html_content += f""" \
                                       <table border="1" >
                                       <tr> <td colspan="4"><h2>Aucune donnée de carburant disponible.</h2></tr>
                            </table>"""

            html_content += f"""
            <br><br><br>
            <h1> RECAPITULATIF:</h1>
            <table border="1">
            <tr><th>Voiture</th><th>Quantite de carburant</th><th>Montant de carburant</th></tr>
            """
            # Calculer le prix total pour chaque voiture
            voitures_annotated_prix = voitures.annotate(
                total_prix=Sum('carburant__prix_total')
            )

            # Filtrer les voitures sans données de carburant
            voitures_annotated_prix = voitures_annotated_prix.exclude(total_prix=None)

            # Ranger les voitures par rapport au prix total
            voitures_ranger_par_prix = voitures_annotated_prix.order_by('-total_prix')
            for voiture in voitures_ranger_par_prix:
                carburant_voiture = carburant.filter(vehicule=voiture, date_premiere__month=mois,
                                                     date_premiere__year=annee)
                if carburant_voiture:
                    total_carburant = carburant_voiture.filter(vehicule=voiture).aggregate(Sum('prix_total'))[
                                          'prix_total__sum'] or 0
                    total_quantite = carburant_voiture.filter(vehicule=voiture).aggregate(Sum('quantite'))[
                                         'quantite__sum'] or 0
                    html_content += f"""
                                    <tr><td>{voiture}</td><td>{total_quantite} Litres</td><td>{total_carburant} FCFA</td></tr>
                                    """

            # Fermer la table précédente
            html_content += "</table>"



            if carburant:
                for type in types:
                    variation_first = variations.filter(carburant=type, date_debut__month__lte=mois,
                                                        date_debut__year__lte=annee).order_by('date_debut')

                    html_content += f"""
                       <br>
                       <br>
                       <br>
                       <h1>VARIATION DES PRIX DU {type.nom.upper()}</h1>
                       <br>
                                                                                           <table border="1">
                                                                                           <tr><th>NOM</th><th>PRIX</th><th>PERIOD</th></tr>
                                                                                           """
                    for variation in variation_first:
                        date = variation.date_debut.date()
                        variation_date = formats.date_format(date, format="l d F Y")
                        date_fin_info = ""
                        if variation.date_fin:
                            date2 = variation.date_fin.date()
                            variation_fin = formats.date_format(date2, format="l d F Y")
                            date_fin_info = f" au {variation_fin}"
                        if variation.date_fin:
                            if variation.date_fin.month == int(mois) and variation.date_fin.year == int(
                                    annee) or not variation.date_fin:
                                html_content += f"""
                                                                                <tr><td>{variation.carburant.nom}</td><td>{variation.prix} FCFA</td><td>{variation_date} {date_fin_info}</td></tr>
                                                                                                """
                        else:
                            html_content += f"""
                                                                                <tr>
                                                                                    <td>{variation.carburant.nom}</td>
                                                                                    <td>{variation.prix} FCFA</td>
                                                                                    <td>{variation_date} {date_fin_info}</td>
                                                                                </tr>
                                                                            """
                    html_content += f"""
                                                                    </table>"""

        # Créer un objet HttpResponse avec le contenu du PDF
        response = HttpResponse(content_type='application/pdf')
        if vehicule_id:
            vehicule = Vehicule.objects.get(id=vehicule_id)
            response[
                'Content-Disposition'] = f'inline; filename="Rapport Carburant de {mois_lettre} {annee}  de {vehicule}.pdf"'
        else:
            response['Content-Disposition'] = f'inline; filename="Rapport Carburant de {mois_lettre} {annee}.pdf"'
        # Générer le PDF à partir du contenu HTML
        pisa_status = pisa.CreatePDF(html_content, dest=response)
        if pisa_status.err:
            return HttpResponse('Une erreur est survenue lors de la génération du PDF')

        return response


@login_required(login_url='Connexion')
def rapport_carburant_mensuel(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        mois = request.POST.get('mois')
        mois_lettre = _(calendar.month_name[int(mois)])
        annee = request.POST.get('annee')
        vehicules_ids_with_carburant = Carburant.objects.values('vehicule_id').distinct()
        vehicule = Vehicule.objects.filter(id__in=Subquery(vehicules_ids_with_carburant))
        voiture = Vehicule.objects.all()
        labels = [f"{vehicle}" for vehicle in vehicule]
        fuel_data = [vehicle.total_carburant(mois, annee) for vehicle in vehicule]
        quantites = [data['quantite'] for data in fuel_data]
        prix = [data['prix'] for data in fuel_data]

        context = {
            'labels': labels,
            'quantites': quantites,
            'prix': prix,
            'vehicules': voiture,
            'mois': mois_lettre,
            'annee': annee
        }

        return render(request, 'rapport_carburant_mensuel.html', context)

    return render(request, 'rapport_carburant_mensuel.html')


def rapport_incident_conducteur_mensuel_pdf(request):
    if request.method == 'POST':
        # Récupérez les données soumises du formulaire
        conducteur_id = request.POST.get('conducteur')
        mois = request.POST.get('mois')
        annee = request.POST.get('annee')
        mois_lettre = _(calendar.month_name[int(mois)])
        conducteurs = Conducteur.objects.all()
        if conducteur_id:

            conducteur = Conducteur.objects.get(id=conducteur_id)
            # Récupérer les données de carburant et d'entretien
            incidents = Incident.objects.filter(conducteur=conducteur_id, date_premiere__month=mois,
                                                date_premiere__year=annee)

            html_content = f"""
                        <html>
                        <head>
                        <title>Rapport</title>
                        <style>
                                table {{
                                    width: 100%;
                                    border-collapse: collapse;
                                }}
                                th, td {{
                                    border: 1px solid black;
                                    padding: 8px;
                                    text-align: center;
                                }}
                                th {{
                                    background-color: #f2f2f2;
                                }}
                                h1, h2 {{
                                    text-align: center;
                                }}
                                .center {{
                                    text-align: center;
                                }}
                        </style>
                        </head>
                        <body class="center">
                        <h1>Rapport Incident de {mois_lettre} {annee}  de {conducteur}</h1>
                    """

            if incidents:
                html_content += """
                     <table border="1">
                     <tr><th>Date</th><th>Vehicule</th><th>Description</th></tr>
                     """
                for incident in incidents:
                    date = incident.date_premiere
                    incident_date = formats.date_format(date, format="l d F Y")
                    html_content += f"""
                        <tr><td>{incident_date}</td><td>{incident.vehicule}</td><td>{incident.description_incident}</td></tr>
                    """

            else:
                html_content += "<p>Aucune donnée de incident disponible.</p>"
        else:
            # Générer le contenu HTML du PDF
            html_content = f"""
                <html>
                <head>
                <title>Rapport PDF</title>
                <style>
                                table {{
                                    width: 100%;
                                    border-collapse: collapse;
                                }}
                                th, td {{
                                    border: 1px solid black;
                                    padding: 8px;
                                    text-align: center;
                                }}
                                th {{
                                    background-color: #f2f2f2;
                                }}
                                h1, h2 {{
                                    text-align: center;
                                }}
                                .center {{
                                    text-align: center;
                                }}
                </style>
                </head>
                <body class="center">
                <h1>Rapport Incidents de {mois_lettre} {annee}</h1>
                """

            # Filtrer les incidents pour le mois et l'année spécifiés
            incidents = Incident.objects.filter(date_premiere__month=mois, date_premiere__year=annee)

            # Vérifier s'il y a des incidents pour ce mois et cette année
            if incidents:

                # Boucle sur chaque conducteur pour générer le rapport
                for conducteur in conducteurs:

                    # Filtrer les incidents pour ce conducteur
                    incidents_conducteur = incidents.filter(conducteur=conducteur)
                    html_content += f"""
                                                                      <h2>Rapport de {conducteur}</h2>

                                                                  """

                    # Vérifier s'il y a des incidents pour ce conducteur
                    if incidents_conducteur:
                        html_content += f"""
                                            <table border="1">
                                            <tr><th>Date</th><th>Véhicule</th><th>Description</th></tr>
                                            """

                        # Boucle sur chaque incident pour ce conducteur
                        for incident in incidents_conducteur:
                            date = incident.date_premiere
                            incident_date = formats.date_format(date, format="l d F Y")
                            html_content += f"""
                                                    <tr><td>{incident_date}</td><td>{incident.vehicule}</td><td>{incident.description_incident}</td></tr>
                                                """

                            # Calculer le nombre total d'incidents pour ce conducteur
                        total_incident = incidents_conducteur.count()
                        # Calculer les totaux pour ce conducteur
                        total_vehicule = incidents_conducteur.values('vehicule').distinct().count()
                        html_content += f"""
                                <tr><td>Total</td><td>{total_vehicule}</td><td>{total_incident}</td></tr>
                            """
                    else:
                        html_content += "<tr><td colspan='3'>Aucun incident trouvé pour ce conducteur.</td></tr>"

                    html_content += "</table>"

            else:
                html_content += "<p>Aucun incident trouvé pour ce mois et cette année.</p>"

            # Fermer les balises HTML
            html_content += f"""
                </body>
                </html>
                """

        # Créer un objet HttpResponse avec le contenu du PDF
        response = HttpResponse(content_type='application/pdf')
        if conducteur_id:
            conducteur = Conducteur.objects.get(id=conducteur_id)
            response[
                'Content-Disposition'] = f'inline; filename="Rapport Incident Conducteur de {mois_lettre} {annee}  de {conducteur}.pdf"'
        else:
            response[
                'Content-Disposition'] = f'inline; filename="Rapport Incident Conducteur de {mois_lettre} {annee}.pdf"'
        # Générer le PDF à partir du contenu HTML
        pisa_status = pisa.CreatePDF(html_content, dest=response)
        if pisa_status.err:
            return HttpResponse('Une erreur est survenue lors de la génération du PDF')

        return response



@login_required(login_url='Connexion')
def courbe_depense_mensuel(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        mois = request.POST.get('mois')
        mois_lettre = french(calendar.month_name[int(mois)])
        annee = request.POST.get('annee')
        voiture = Vehicule.objects.all()
        # Filtrer les données de consommation de carburant pour le mois et l'année sélectionnés
        prix_carburant = Carburant.objects.filter(date_premiere__month=mois, date_premiere__year=annee)
        prix_entretien = Entretien.objects.filter(date_entretien__month=mois, date_entretien__year=annee)
        # Calculer la consommation de carburant pour chaque véhicule
        prix_par_vehicule = {}
        for prix in prix_carburant:
            if prix.vehicule not in prix_par_vehicule:
                prix_par_vehicule[prix.vehicule] = 0
            prix_par_vehicule[prix.vehicule] += prix.prix_total

        # Parcourir la liste des prix d'entretien
        for prix in prix_entretien:
            if prix.vehicule not in prix_par_vehicule:
                prix_par_vehicule[prix.vehicule] = 0
            prix_par_vehicule[prix.vehicule] += prix.prix_entretient
        labels = []
        data = []
        for vehicule, prix in prix_par_vehicule.items():
            labels.append(f"{vehicule}")
            data.append(prix)

        return render(request, 'rapport_depense_mensuel.html',
                      {'labels': labels, 'data': data, 'vehicule': voiture, 'mois': mois_lettre, 'annee': annee})

    return render(request, 'rapport_depense_mensuel.html')


@login_required(login_url='Connexion')
def courbe_depense_global(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        debut = request.POST.get('date_debut_periode')
        fin = request.POST.get('date_fin_periode')
        debut_date = datetime.strptime(debut, '%Y-%m-%d').date()

        if fin:
            fin_date = datetime.strptime(fin, '%Y-%m-%d').date()
        else:
            fin_date = date.today()

        vehicules = Vehicule.objects.all()
        # Filtrer les données de consommation de carburant pour le mois et l'année sélectionnés
        prix_carburant = Carburant.objects.filter(date_premiere__range=(debut_date, fin_date))
        prix_entretien = Entretien.objects.filter(date_entretien__range=(debut_date, fin_date))
        # Calculer la consommation de carburant pour chaque véhicule
        prix_par_vehicule = {}
        for prix in prix_carburant:
            if prix.vehicule not in prix_par_vehicule:
                prix_par_vehicule[prix.vehicule] = 0
            prix_par_vehicule[prix.vehicule] += prix.prix_total

        # Parcourir la liste des prix d'entretien
        for prix in prix_entretien:
            if prix.vehicule not in prix_par_vehicule:
                prix_par_vehicule[prix.vehicule] = 0
            prix_par_vehicule[prix.vehicule] += prix.prix_entretient
        labels = []
        data = []
        for vehicule, prix in prix_par_vehicule.items():
            labels.append(f"{vehicule}")
            data.append(prix)

        return render(request, 'rapport_depense.html',
                      {'labels': labels, 'data': data, 'vehicule': vehicules, 'debut': debut_date, 'fin': fin_date})

    return render(request, 'rapport_depense.html')


@login_required(login_url='Connexion')
def courbe_entretien_mensuel(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        mois = request.POST.get('mois')
        mois_lettre = french(calendar.month_name[int(mois)])
        annee = request.POST.get('annee')
        vehicules_ids_with_carburant = Entretien.objects.values(
            'vehicule_id').distinct()
        vehicles = Vehicule.objects.filter(id__in=Subquery(vehicules_ids_with_carburant))
        voiture = Vehicule.objects.all()
        labels = [f"{vehicle}" for vehicle in vehicles]
        fuel_data = [vehicle.total_entretien(mois, annee) for vehicle in vehicles]
        quantites = [data['quantite'] for data in fuel_data]
        prix = [data['prix'] for data in fuel_data]

        context = {
            'labels': labels,
            'quantites': quantites,
            'prix': prix,
            'mois': mois_lettre,
            'annee': annee,
            'vehicules': voiture,
        }

        return render(request, 'rapport_entretien_mensuel.html', context)

    return render(request, 'rapport_entretien_mensuel.html')


@login_required(login_url='Connexion')
def courbe_incident_vehicule_mensuel(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        mois = request.POST.get('mois')
        mois_lettre = french(calendar.month_name[int(mois)])
        annee = request.POST.get('annee')
        voiture = Vehicule.objects.all()
        # Filtrer les données de consommation de carburant pour le mois et l'année sélectionnés
        nbre_incident = Incident.objects.filter(date_premiere__month=mois, date_premiere__year=annee)

        # Calculer la consommation de carburant pour chaque véhicule
        incident_par_vehicule = {}
        for incident in nbre_incident:
            if incident.vehicule not in incident_par_vehicule:
                incident_par_vehicule[incident.vehicule] = 0
            incident_par_vehicule[incident.vehicule] += 1
        labels = []
        data = []
        for vehicule, incident in incident_par_vehicule.items():
            labels.append(f"{vehicule}")
            data.append(incident)

        return render(request, 'rapport_incident_vehicule_mensuel.html',
                      {'labels': labels, 'data': data, 'vehicules': voiture, 'mois': mois_lettre, 'annee': annee})

    return render(request, 'rapport_incident_vehicule_mensuel.html')


@login_required(login_url='Connexion')
def courbe_incident_conducteur_mensuel(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        mois = request.POST.get('mois')
        mois_lettre = french(calendar.month_name[int(mois)])
        annee = request.POST.get('annee')
        conducteurs = Conducteur.objects.all()
        # Filtrer les données de consommation de carburant pour le mois et l'année sélectionnés
        nbre_incident = Incident.objects.filter(conducteur__isnull=False, date_premiere__month=mois,
                                                date_premiere__year=annee)

        # Calculer la consommation de carburant pour chaque véhicule
        incident_par_conducteur = {}
        for incident in nbre_incident:
            if incident.conducteur not in incident_par_conducteur:
                incident_par_conducteur[incident.conducteur] = 0
            incident_par_conducteur[incident.conducteur] += 1
        labels = []
        data = []
        for conducteur, incident in incident_par_conducteur.items():
            labels.append(f"{conducteur}")
            data.append(incident)

        return render(request, 'rapport_incident_conducteur_mensuel.html',
                      {'labels': labels, 'data': data, 'conducteurs': conducteurs, 'mois': mois_lettre, 'annee': annee})

    return render(request, 'rapport_incident_conducteur_mensuel.html')


@login_required(login_url='Connexion')
def liste_deplacement_arrive_admin(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    etatarrive = (
        EtatArrive.objects.all().annotate(
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
    return render(request, 'afficher_deplacement_arrive_admin.html', {'etatarrives': etatarrive})


@login_required(login_url='Connexion')
def details_arriver_admin(request, etatarrive_id):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    etat_arrive = get_object_or_404(EtatArrive, id=etatarrive_id)
    deplacement_id = etat_arrive.deplacement.id
    deplacement = get_object_or_404(Deplacement, id=deplacement_id)
    image = Photo.objects.filter(etat_arrive=etatarrive_id)
    images = Photo.objects.filter(deplacement=deplacement_id)
    return render(request, 'arriver_details_admin.html',
                  {'etat_arrive': etat_arrive, 'deplacement': deplacement, 'image': image, 'images': images})


@login_required(login_url='Connexion')
def liste_incidents_externe_admin(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    aujourd_hui = date.today()
    incidents_list = (
        Incident.objects.filter(conducteur_id__isnull=False).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )
    incidents = {}
    for item_incident in incidents_list:
        latest_photo = get_latest_photo(item_incident)
        incidents[item_incident.id] = {'incident': item_incident, 'latest_photo': latest_photo}
    paginator = Paginator(list(incidents.values()), 15)
    page = request.GET.get('page')
    try:
        incidents_page = paginator.page(page)
    except PageNotAnInteger:
        incidents_page = paginator.page(1)
    return render(request, 'Liste_incidents_externe_admin.html', {'incidents': incidents_page, 'paginator': paginator})


@login_required(login_url='Connexion')
def liste_incidents_interne_admin(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    incidents_list = (
        Incident.objects.filter(conducteur_id__isnull=True).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )
    incidents = {}
    for item_incident in incidents_list:
        latest_photo = get_latest_photo(item_incident)
        incidents[item_incident.id] = {'incident': item_incident, 'latest_photo': latest_photo}

    paginator = Paginator(list(incidents.values()), 15)

    page = request.GET.get('page')
    try:
        incidents_page = paginator.page(page)
    except PageNotAnInteger:
        incidents_page = paginator.page(1)
    except EmptyPage:
        incidents_page = paginator.page(paginator.num_pages)

    return render(request, 'Liste_incidents_interne_admin.html', {'incidents': incidents_page, 'paginator': paginator})


@login_required(login_url='Connexion')
def incident_interne_detail_admin(request, pk):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    incident = get_object_or_404(Incident, id=pk)
    image = Photo.objects.filter(incident=incident)
    return render(request, 'incident_interne_details_admin.html', {'incident': incident, 'image': image})


@login_required(login_url='Connexion')
def incident_externe_detail_admin(request, pk):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    incident = get_object_or_404(Incident, id=pk)
    image = Photo.objects.filter(incident=incident)
    return render(request, 'incident_externe_details_admin.html', {'incident': incident, 'image': image})


def get_latest_photo(incident):
    return Photo.objects.filter(incident=incident).order_by('-id').first()


@login_required(login_url='Connexion')
def incidents_search(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    form = IncidentSearchForm(request.GET)
    incidents_list = (
        Incident.objects.filter(conducteur_id__isnull=True).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )
    incidents = {}

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            incidents_list = incidents_list.filter(Q(vehicule__numero_immatriculation__icontains=query) |
                                                   Q(description_incident__icontains=query) |
                                                   Q(vehicule__marque__marque__icontains=query))
    for incident in incidents_list:
        latest_photo = get_latest_photo(incident)
        incidents[incident.id] = {'incident': incident, 'latest_photo': latest_photo}

    paginator = Paginator(list(incidents.values()), 15)

    page = request.GET.get('page')
    try:
        incidents_page = paginator.page(page)
    except PageNotAnInteger:
        incidents_page = paginator.page(1)
    except EmptyPage:
        incidents_page = paginator.page(paginator.num_pages)

    context = {'incidents': incidents_page, 'form': form, 'paginator': paginator}
    if not incidents and form.is_valid():
        context['no_results'] = True
    return render(request, 'Liste_incidents_interne_admin.html', context)


@login_required(login_url='Connexion')
def incidents_externe_search(request):
    form = IncidentSearchForm(request.GET)
    incidents_list = (
        Incident.objects.filter(conducteur_id__isnull=False).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )
    incidents = {}

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            query_parts = query.split()
            if len(query_parts) > 1:
                nom = query_parts[0]  # First part is considered the last name (nom)
                prenoms = query_parts[1:]  # All parts except the first one are considered first names (prenoms)
                incidents_list = incidents_list.filter(
                    Q(vehicule__marque__marque__icontains=query) |
                    Q(vehicule__numero_immatriculation__icontains=query) |
                    Q(vehicule__type_commercial__modele__icontains=query) |
                    Q(description_incident__icontains=query) |
                    Q(conducteur__utilisateur__nom__icontains=nom)
                )
                for prenom in prenoms:
                    incidents_list = incidents_list.filter(conducteur__utilisateur__prenom__icontains=prenom)
            else:

                incidents_list = incidents_list.filter(Q(vehicule__numero_immatriculation__icontains=query) |
                                                       Q(description_incident__icontains=query) |
                                                       Q(vehicule__marque__marque__icontains=query) |
                                                       Q(conducteur__utilisateur__nom__icontains=query) |
                                                       Q(conducteur__utilisateur__prenom__icontains=query))
    for incident in incidents_list:
        latest_photo = get_latest_photo(incident)
        incidents[incident.id] = {'incident': incident, 'latest_photo': latest_photo}

    paginator = Paginator(list(incidents.values()), 15)

    page = request.GET.get('page')
    try:
        incidents_page = paginator.page(page)
    except PageNotAnInteger:
        incidents_page = paginator.page(1)
    except EmptyPage:
        incidents_page = paginator.page(paginator.num_pages)

    context = {'incidents': incidents_page, 'form': form, 'paginator': paginator}
    # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
    if not incidents and form.is_valid():
        context['no_results'] = True
    return render(request, 'Liste_incidents_externe_admin.html', context)


def arrive_search(request):
    form = DeplacementSearchForm(request.GET)
    arrivee = (
        EtatArrive.objects.annotate(
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

    return render(request, 'afficher_deplacement_arrive_admin.html', context)

def rapport_entretien_mensuel_admins(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        return courbe_entretien_mensuel(request)
    else:
        vehicule = Vehicule.objects.all()
        context = {'vehicules': vehicule}
        return render(request, 'rapport_entretien_mensuel.html', context)


@login_required(login_url='Connexion')
def rapport_incident_vehicule_mensuel_admins(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        return courbe_incident_vehicule_mensuel(request)
    vehicules = Vehicule.objects.all()
    context = {'vehicules': vehicules}
    return render(request, 'rapport_incident_vehicule_mensuel.html', context)


def rapport_entretien_mensuel_pdf(request):
    if request.method == 'POST':
        # Récupérez les données soumises du formulaire
        vehicule_id = request.POST.get('vehicule')
        mois = request.POST.get('mois')
        annee = request.POST.get('annee')
        mois_lettre = _(calendar.month_name[int(mois)])
        voitures = Vehicule.objects.all()
        if vehicule_id:

            vehicule = Vehicule.objects.get(id=vehicule_id)
            entretien = Entretien.objects.filter(vehicule=vehicule_id, date_entretien__month=mois,
                                                 date_entretien__year=annee)

            total_entretien = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            vidange = Entretien.objects.filter(vehicule=vehicule_id, date_entretien__month=mois,
                                               date_entretien__year=annee, type__nom="VIDANGE")
            total_vidange = vidange.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            nbre_vidange = vidange.count() or 0
            visite = Entretien.objects.filter(vehicule=vehicule_id, date_entretien__month=mois,
                                              date_entretien__year=annee, type__nom="VISITE")
            total_visite = visite.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            nbre_visite = visite.count() or 0
            autre = Entretien.objects.filter(vehicule=vehicule_id, date_entretien__month=mois,
                                             date_entretien__year=annee, type__nom="AUTRE")
            total_autre = autre.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            nbre_autre = autre.count() or 0
            nbre_entretien = entretien.count()

            html_content = f"""
                        <html>
                        <head>
                        <title>Rapport</title>
                        <style>
                                table {{
                                    width: 100%;
                                    border-collapse: collapse;
                                }}
                                th, td {{
                                    border: 1px solid black;
                                    padding: 8px;
                                    text-align: center;
                                }}
                                th {{
                                    background-color: #f2f2f2;
                                }}
                                h1, h2 {{
                                    text-align: center;
                                }}
                                .center {{
                                    text-align: center;
                                }}
                        </style>
                        </head>
                        <body class="center">
                        <h1>Rapport Entretien de {mois_lettre} {annee}  de {vehicule}</h1>
                    """

            if entretien:
                html_content += """
                     <table border="1">
                     <tr><th>Date</th><th>Type</th><th>Prix</th><th>Gestionnaire</th></tr>
                     """
                for reparation in entretien:
                    date = reparation.date_entretien
                    reparation_date = formats.date_format(date, format="l d F Y")
                    html_content += f"""
                        <tr><td>{reparation_date}</td><td>{reparation.type}</td><td>{reparation.prix_entretient}</td><td>{reparation.utilisateur}</td></tr>
                    """
                html_content += f"""

                    <tr><td>Total</td><td>{nbre_entretien}</td><td>{total_entretien}</td></tr>
                     </table>
                    """
                html_content += f"""

                <br>
                <br>
                <br>
                    <table border=1>
                    <tr><th>Type</th><th>Nombre</th><th>Prix Total</th></tr>
                    <tr><th>Vidange</th><td>{nbre_vidange}</td><td>{total_vidange}</td></tr>
                    <tr><th>Visite</th><td>{nbre_visite}</td><td>{total_visite}</td></tr>
                    <tr><th>Autre</th><td>{nbre_autre}</td><td>{total_autre}</td></tr>
                     </table>
                    """
            else:
                html_content += "<p>Aucune donnée d'entretien disponible.</p>"
        else:
            # Initialiser entretiens_vehicule en dehors de la boucle
            entretiens_vehicule = None

            # Générer le contenu HTML du PDF
            html_content = f"""
                <html>
                <head>
                <title>Rapport PDF</title>
                <style>
                                table {{
                                    width: 100%;
                                    border-collapse: collapse;
                                }}
                                th, td {{
                                    border: 1px solid black;
                                    padding: 8px;
                                    text-align: center;
                                }}
                                th {{
                                    background-color: #f2f2f2;
                                }}
                                h1, h2 {{
                                    text-align: center;
                                }}
                                .center {{
                                    text-align: center;
                                }}
                </style>
                </head>
                <body class="center">
                <h1>Rapport Entretien de {mois_lettre} {annee}</h1>
            """

            # Filtrer les incidents pour le mois et l'année spécifiés
            entretiens = Entretien.objects.filter(date_entretien__month=mois, date_entretien__year=annee)

            # Vérifier s'il y a des incidents pour ce mois et cette année
            if entretiens:

                # Boucle sur chaque conducteur pour générer le rapport
                for voiture in voitures:

                    # Filtrer les incidents pour ce conducteur
                    entretiens_vehicule = entretiens.filter(vehicule=voiture)

                    vidange = Entretien.objects.filter(date_entretien__month=mois,
                                                       date_entretien__year=annee, type__nom="VIDANGE")
                    total_vidange = vidange.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
                    nbre_vidange = vidange.count() or 0
                    visite = Entretien.objects.filter(date_entretien__month=mois,
                                                      date_entretien__year=annee, type__nom="VISITE")
                    total_visite = visite.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
                    nbre_visite = visite.count() or 0
                    autre = Entretien.objects.filter(date_entretien__month=mois,
                                                     date_entretien__year=annee, type__nom="AUTRE")
                    total_autre = autre.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
                    nbre_autre = autre.count() or 0
                    html_content += f"""
                        <h2>Rapport de {voiture}</h2>
                    """

                    # Vérifier s'il y a des incidents pour ce conducteur
                    if entretiens_vehicule:
                        html_content += f"""
                            <table border="1">
                            <tr><th>Date</th><th>Type</th><th>Prix</th><th>Gestionnaire</th></tr>
                        """

                        # Boucle sur chaque incident pour ce conducteur
                        for entretien in entretiens_vehicule:
                            date = entretien.date_entretien
                            entretien_date = formats.date_format(date, format="l d F Y")
                            html_content += f"""
                                <tr><td>{entretien_date}</td><td>{entretien.type}</td><td>{entretien.prix_entretient}</td><td>{entretien.utilisateur}</td></tr>
                            """

                        # Calculer le nombre total d'incidents pour ce conducteur
                        total_entretien = entretiens_vehicule.aggregate(Sum('prix_entretient'))[
                                              'prix_entretient__sum'] or 0
                        # Calculer les totaux pour ce conducteur
                        total_vehicule = entretiens_vehicule.filter(vehicule=entretien.vehicule).count()
                        html_content += f"""
                            <tr><td>Total</td><td>{total_vehicule}</td><td>{total_entretien}</td></tr>
                        """

                    else:
                        html_content += "<tr><td colspan='3'>Aucun entretien trouvé pour ce vehicule.</td></tr>"

                    html_content += "</table>"

            else:
                html_content += "<p>Aucun incident trouvé pour ce mois et cette année.</p>"

            html_content += f"""
                        <br><br><br>
                        <h1> RECAPITULATIF:</h1>
                        <table border="1">
                        <tr><th>Voiture</th><th>Montant entretien</th></tr>
                        """
            # Calculer le prix total pour chaque voiture
            voitures_annotated_prix = voitures.annotate(
                total_prix=Sum('entretien__prix_entretient')
            )

            # Filtrer les voitures sans données de carburant
            voitures_annotated_prix = voitures_annotated_prix.exclude(total_prix=None)

            # Ranger les voitures par rapport au prix total
            voitures_ranger_par_prix = voitures_annotated_prix.order_by('-total_prix')
            for voiture in voitures_ranger_par_prix:
                entretien_voiture = entretiens.filter(vehicule=voiture, date_entretien__month=mois,
                                                      date_entretien__year=annee)
                if entretien_voiture:
                    total_entretien = entretien_voiture.filter(vehicule=voiture).aggregate(Sum('prix_entretient'))[
                                          'prix_entretient__sum'] or 0

                    html_content += f"""
                                                <tr><td>{voiture}</td><td>{total_entretien} FCFA</td></tr>
                                                """

            # Fermer la table précédente
            html_content += "</table>"

            # Utilisez entretiens_vehicule pour vérifier s'il y a eu des entretiens de véhicules
            if entretiens_vehicule:
                html_content_bas = f"""
                    <br>
                    <br>
                    <br>
                    <table border=1>
                    <tr><th>Type</th><th>Nombre</th><th>Prix Total</th></tr>
                    <tr><th>Vidange</th><td>{nbre_vidange}</td><td>{total_vidange}</td></tr>
                    <tr><th>Visite</th><td>{nbre_visite}</td><td>{total_visite}</td></tr>
                    <tr><th>Autre</th><td>{nbre_autre}</td><td>{total_autre}</td></tr>
                    </table>
                """

            # Fermer les balises HTML
            html_content += f"""
                </body>
                </html>
            """

            # Si entretiens_vehicule est défini, ajouter le tableau bas
            if entretiens_vehicule:
                html_content += html_content_bas

        # Créer un objet HttpResponse avec le contenu du PDF
        response = HttpResponse(content_type='application/pdf')
        if vehicule_id:
            vehicule = Vehicule.objects.get(id=vehicule_id)
            response[
                'Content-Disposition'] = f'inline; filename="Rapport Entretien de {mois_lettre} {annee}  de {vehicule}.pdf"'
        else:
            response['Content-Disposition'] = f'inline; filename="Rapport Entretien de {mois_lettre} {annee}.pdf"'
        # Générer le PDF à partir du contenu HTML
        pisa_status = pisa.CreatePDF(html_content, dest=response)
        if pisa_status.err:
            return HttpResponse('Une erreur est survenue lors de la génération du PDF')

        return response


def rapport_incident_vehicule_mensuel_pdf(request):
    if request.method == 'POST':
        # Récupérez les données soumises du formulaire
        vehicule_id = request.POST.get('vehicule')
        mois = request.POST.get('mois')
        annee = request.POST.get('annee')
        mois_lettre = _(calendar.month_name[int(mois)])
        vehicules = Vehicule.objects.all()
        if vehicule_id:

            vehicule = Vehicule.objects.get(id=vehicule_id)
            # Récupérer les données de carburant et d'entretien
            incidents = Incident.objects.filter(vehicule=vehicule_id, date_premiere__month=mois,
                                                date_premiere__year=annee)
            incidents_externe = Incident.objects.filter(vehicule=vehicule_id, date_premiere__month=mois,
                                                        date_premiere__year=annee, utilisateurs__isnull=True)
            nbre_incidents_externe = incidents_externe.count()
            incidents_interne = Incident.objects.filter(vehicule=vehicule_id, date_premiere__month=mois,
                                                        date_premiere__year=annee, conducteur__isnull=True)
            nbre_incidents_interne = incidents_interne.count()

            html_content = f"""
                           <html>
                           <head>
                           <title>Rapport</title>
                           <style>
                                   table {{
                                       width: 100%;
                                       border-collapse: collapse;
                                   }}
                                   th, td {{
                                       border: 1px solid black;
                                       padding: 8px;
                                       text-align: center;
                                   }}
                                   th {{
                                       background-color: #f2f2f2;
                                   }}
                                   h1, h2 {{
                                       text-align: center;
                                   }}
                                   .center {{
                                       text-align: center;
                                   }}
                           </style>
                           </head>
                           <body class="center">
                           <h1>Rapport Carburant de {mois_lettre} {annee}  de {vehicule}</h1>
                       """

            if incidents:
                html_content += """
                        <table border="1">
                        <tr><th>Date</th><th>Conducteur</th><th>Gestionnaire</th><th>Description</th></tr>
                        """

                for incident in incidents:

                    date = incident.date_premiere
                    incident_date = formats.date_format(date, format='l d F Y')
                    incident_conducteur = incident.conducteur
                    if not incident.conducteur:
                        incident_conducteur = " "
                    incident_gestionnaire = incident.utilisateurs
                    if not incident.utilisateurs:
                        incident_gestionnaire = " "
                    html_content += f"""
                           <tr><td>{incident_date}</td><td>{incident_conducteur}</td><td>{incident_gestionnaire}</td><td>{incident.description_incident}</td></tr>
                       """
                html_content += f"""<tr><td>Total</td><td>{nbre_incidents_externe} incidents externes</td><td>{nbre_incidents_interne} incidents internes</td></tr>
                                </table>
                                   """
                if incidents_externe:
                    html_content += f"""
                                            <br>
                                            <br>
                                            <br>
                                            <table border =1>
                                            <tr><th>Conducteur</th><th>Nombre d'incidents</th></tr>
                                            """
                    conducteurs_traites = set()  # Ensemble pour garder une trace des conducteurs déjà traités

                    for incident in incidents:
                        if incident.conducteur and incident.conducteur not in conducteurs_traites:
                            incident_par_conducteur = incidents_externe.filter(conducteur=incident.conducteur).count()
                            html_content += f"""

                                <tr><td>{incident.conducteur}</td><td>{incident_par_conducteur}</td></tr>
                            """
                            conducteurs_traites.add(incident.conducteur)  # Ajouter le conducteur traité à l'ensemble

                        # Créer un dictionnaire pour compter les incidents par conducteur
                    html_content += "</table>"
            else:
                html_content += "<p>Aucune donnée de incident disponible.</p>"


        else:
            # Générer le contenu HTML du PDF
            html_content = f"""
                   <html>
                   <head>
                   <title>Rapport PDF</title>
                   <style>
                                   table {{
                                       width: 100%;
                                       border-collapse: collapse;
                                   }}
                                   th, td {{
                                       border: 1px solid black;
                                       padding: 8px;
                                       text-align: center;
                                   }}
                                   th {{
                                       background-color: #f2f2f2;
                                   }}
                                   h1, h2 {{
                                       text-align: center;
                                   }}
                                   .center {{
                                       text-align: center;
                                   }}
                   </style>
                   </head>
                   <body class="center">
                   <h1>Rapport Incidents de {mois_lettre} {annee}</h1>
                   """

            # Filtrer les incidents pour le mois et l'année spécifiés
            incidents = Incident.objects.filter(date_premiere__month=mois, date_premiere__year=annee)

            # Vérifier s'il y a des incidents pour ce mois et cette année
            if incidents:
                # Créer un ensemble pour garder une trace des conducteurs déjà traités
                conducteurs_traites = set()

                # Créer un dictionnaire pour garder une trace du nombre total d'incidents par conducteur
                total_incidents_par_conducteur = {}

                # Boucle sur chaque véhicule pour générer le rapport
                for vehicule in vehicules:

                    # Filtrer les incidents pour ce véhicule
                    incidents_vehicule = incidents.filter(vehicule=vehicule)

                    html_content += f"""
                                           <h2>Rapport de {vehicule}</h2>
                                           """

                    # Vérifier s'il y a des incidents pour ce véhicule
                    if incidents_vehicule:
                        html_content += f"""
                                               <table border="1">
                                               <tr><th>Date</th><th>Conducteur</th><th>Gestionnaire</th><th>Description</th></tr>
                                                """

                        # Créer un dictionnaire pour garder une trace du nombre d'incidents par conducteur pour ce véhicule
                        incidents_par_conducteur = {}

                        # Boucle sur chaque incident pour ce véhicule
                        for incident in incidents_vehicule:
                            date = incident.date_premiere
                            incident_date = formats.date_format(date, format='l d F Y')
                            incident_conducteur = incident.conducteur if incident.conducteur else " "
                            incident_gestionnaire = incident.utilisateurs if incident.utilisateurs else " "
                            description_incident = incident.description_incident

                            # Ajouter le conducteur à la liste des conducteurs traités
                            conducteurs_traites.add(incident_conducteur)

                            # Ajouter l'incident au dictionnaire incidents_par_conducteur
                            if incident_conducteur in incidents_par_conducteur:
                                incidents_par_conducteur[incident_conducteur] += 1
                            else:
                                incidents_par_conducteur[incident_conducteur] = 1

                            html_content += f"""
                                                       <tr><td>{incident_date}</td><td>{incident_conducteur}</td><td>{incident_gestionnaire}</td><td>{description_incident}</td></tr>
                                                   """

                        # Ajouter le nombre d'incidents par conducteur au dictionnaire total_incidents_par_conducteur
                        for conducteur, nb_incidents in incidents_par_conducteur.items():
                            if conducteur in total_incidents_par_conducteur:
                                total_incidents_par_conducteur[conducteur] += nb_incidents
                            else:
                                total_incidents_par_conducteur[conducteur] = nb_incidents

                                # Calculer le nombre total d'incidents pour ce conducteur
                        incidents_interne_vehicule = incidents.filter(vehicule=vehicule, conducteur__isnull=True)
                        incidents_externe_vehicule = incidents.filter(vehicule=vehicule, utilisateurs__isnull=True)
                        total_incident = incidents_interne_vehicule.count()

                        # Calculer les totaux pour ce conducteur
                        total_vehicule = incidents_externe_vehicule.count()
                        html_content += f"""
                                                       <tr><td>Total</td><td>{total_vehicule}</td><td>{total_incident}</td></tr>
                                                   """

                    else:
                        html_content += "<tr><td>Aucun incident trouvé pour ce véhicule.</td></tr>"

                    html_content += "</table>"

                incidents_interne = incidents.filter(conducteur__isnull=True)
                incidents_externe = incidents.filter(utilisateurs__isnull=True)
                total_incidents_interne = incidents_interne.count()

                # Calculer les totaux pour ce conducteur
                total_incidents_externe = incidents_externe.count()
                html_content += f"""<br><br><br>
                <table border="1">
                <tr><th>Total incidents internes</th><th>Total incidents externe</th></tr>
                <tr><td>{total_incidents_interne}<td>{total_incidents_externe}</td></tr>
                </table>
                <br>
                <br>
                <br>
                                                                   """

                # Afficher le tableau avec le nombre total d'incidents par conducteur sur la période
                html_content += "<h2>Nombres d'incidents par conducteur sur la période :</h2>"
                html_content += "<table border='1'><tr><th>Conducteur</th><th>Nombre total d'incidents</th></tr>"

                for conducteur, nb_incidents in total_incidents_par_conducteur.items():
                    if conducteur != " ":
                        html_content += f"<tr><td>{conducteur}</td><td>{nb_incidents}</td></tr>"
                html_content += "</table>"

            else:
                html_content += "<p>Aucun incident trouvé pour ce mois et cette année.</p>"

            # Fermer les balises HTML
            html_content += f"""
                   </body>
                   </html>
                   """

        # Créer un objet HttpResponse avec le contenu du PDF
        response = HttpResponse(content_type='application/pdf')
        if vehicule_id:
            conducteur = Vehicule.objects.get(id=vehicule_id)
            response[
                'Content-Disposition'] = f'inline; filename="Rapport Incident Véhicule de {mois_lettre} {annee}  de {conducteur}.pdf"'
        else:
            response[
                'Content-Disposition'] = f'inline; filename="Rapport Incident Véhicule de {mois_lettre} {annee}.pdf"'
        # Générer le PDF à partir du contenu HTML
        pisa_status = pisa.CreatePDF(html_content, dest=response)
        if pisa_status.err:
            return HttpResponse('Une erreur est survenue lors de la génération du PDF')

        return response


@login_required(login_url='Connexion')
def ProfilAdmin(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    return render(request, 'Profil_admin.html')
