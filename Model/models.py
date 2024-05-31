# models.py
# import uuid
from datetime import timedelta

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db.models import Sum
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import models
from django.utils.timesince import timesince


class MyUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError("Vous devez entrer un nom d'utilisateur")

        user = self.model(
            username=username
            # username = self.get_by_natural_key(username)
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class Roles(models.Model):
    ADMIN = 'ADMIN'
    GESTIONNAIRE = 'GESTIONNAIRE'
    CONDUCTEUR = 'CONDUCTEUR'
    CLIENT = 'CLIENT'

    ROLE_CHOICES = [
        (ADMIN, 'ADMIN'),
        (GESTIONNAIRE, 'GESTIONNAIRE'),
        (CONDUCTEUR, 'CONDUCTEUR'),
        (CLIENT, 'CLIENT'),

    ]
    role = models.CharField(max_length=200, choices=ROLE_CHOICES)

    def __str__(self):
        return self.get_role_display()


class type_entretien(models.Model):
    nom = models.CharField(max_length=200)

    def __str__(self):
        return self.nom


class type_carburant(models.Model):
    date_mise_a_jour = models.DateTimeField(verbose_name="Date de mise a jour", auto_now=True)
    nom = models.CharField(max_length=20)
    prix = models.IntegerField()

    def __str__(self):
        return f"{self.nom}"


class periode_carburant(models.Model):
    date_debut = models.DateTimeField(verbose_name="Date de debut", blank=True, null=True)
    date_fin = models.DateTimeField(verbose_name="Date de fin", blank=True, null=True)
    prix = models.IntegerField()
    carburant = models.ForeignKey(type_carburant, on_delete=models.SET_NULL, blank=False, null=True)


class Conducteur(models.Model):
    date_mise_a_jour = models.DateTimeField(verbose_name="Date de mise a jour", auto_now=True)
    numero_permis_conduire = models.CharField(max_length=20, unique=True, )
    date_embauche = models.DateField(blank=True, null=True)
    date_de_naissance = models.DateField(blank=True, null=True)
    numero_telephone = models.CharField(max_length=15, unique=True)
    adresse = models.CharField(blank=True, max_length=20)
    disponibilite = models.BooleanField(default=True)
    num_cni = models.CharField(max_length=250, unique=True)
    image = models.ImageField(upload_to='ImagesConducteur/', null=True, blank=True)
    supprimer = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.utilisateur.nom} {self.utilisateur.prenom} "


class Utilisateur(AbstractBaseUser):
    # mon_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_mise_a_jour = models.DateTimeField(verbose_name="Date de mise a jour", auto_now=True)
    username = models.CharField(
        unique=True,
        max_length=255,
        blank=False
    )
    email = models.EmailField(
        unique=True,
        max_length=255,
        blank=False
    )
    nom = models.CharField(max_length=250, verbose_name='nom')
    prenom = models.CharField(max_length=250)
    conducteur = models.OneToOneField(Conducteur, on_delete=models.SET_NULL, null=True, blank=True)
    roles = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    image = models.ImageField(upload_to='ImagesGestionnaire/', null=True, blank=True)
    USERNAME_FIELD = 'username'
    objects = MyUserManager()

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class Marque(models.Model):
    marque = models.CharField(unique=True, max_length=250)

    def __str__(self):
        return self.marque


class Type_Commerciale(models.Model):
    modele = models.CharField(max_length=250)
    marque = models.ForeignKey(Marque, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.modele


class Vehicule(models.Model):
    date_mise_a_jour = models.DateTimeField(verbose_name="Date de mise a jour", auto_now=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    marque = models.ForeignKey(Marque, on_delete=models.CASCADE)
    numero_immatriculation = models.CharField(max_length=25, unique=True)
    type_commercial = models.ForeignKey(Type_Commerciale, on_delete=models.CASCADE)
    numero_chassis = models.CharField(max_length=25, unique=True)
    couleur = models.CharField(max_length=20, blank=True, null=True)
    carte_grise = models.CharField(max_length=25, unique=True)
    date_mise_circulation = models.DateField(blank=True, null=True)
    carrosserie = models.CharField(max_length=100, blank=True, null=True)
    place_assises = models.IntegerField(blank=True, null=True)
    date_expiration_assurance = models.DateField()
    kilometrage = models.IntegerField()
    image_recto = models.ImageField(upload_to='carteGrise/')
    image_verso = models.ImageField(upload_to='carteGrise/')
    date_visite_technique = models.DateField()
    taille_reservoir = models.IntegerField()
    videnge = models.IntegerField()
    energie = models.ForeignKey(type_carburant, on_delete=models.SET_NULL, null=True)
    disponibilite = models.BooleanField(default=True)
    supprimer = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.marque} {self.type_commercial} {self.numero_immatriculation}"

    def total_carburant(self, mois, annee):
        total_quantite = Carburant.objects.filter(vehicule=self, date_premiere__month=mois,
                                                  date_premiere__year=annee).aggregate(total=Sum('quantite')) \
                             .get('total') or 0
        total_prix = Carburant.objects.filter(vehicule=self, date_premiere__month=mois,
                                              date_premiere__year=annee).aggregate(total=Sum('prix_total')) \
                         .get('total') or 0

        return {'quantite': total_quantite, 'prix': total_prix}

    def total_entretien(self, mois, annee):
        total_prix = Entretien.objects.filter(vehicule=self, date_entretien__month=mois, date_entretien__year=annee) \
                         .aggregate(total=Sum('prix_entretient')).get('total') or 0
        total_quantite = Entretien.objects.filter(vehicule=self, date_entretien__month=mois,
                                                  date_entretien__year=annee).count() or 0
        return {'quantite': total_quantite, 'prix': total_prix}


class Deplacement(models.Model):
    date_mise_a_jour = models.DateTimeField(verbose_name="Date de mise a jour", auto_now=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    conducteur = models.ForeignKey(Conducteur, on_delete=models.SET_NULL, blank=True, null=True)
    date_depart = models.DateField(blank=True, null=True)
    kilometrage_depart = models.IntegerField(null=True, blank=True)
    duree_deplacement = models.IntegerField()
    photo_jauge_depart = models.ImageField(upload_to='photo_jauge/', blank=False)
    description = models.CharField(max_length=100, null=True)

    def date_fin(self):
        if self.date_depart:
            return self.date_depart + timedelta(days=self.duree_deplacement)
        else:
            return None

    def __str__(self):
        return f"{self.vehicule} - {self.conducteur.numero_permis_conduire}"


class Motif(models.Model):
    deplacement = models.ForeignKey(Deplacement, on_delete=models.SET_NULL, null=True)
    descritption_modtif = models.CharField(max_length=100, null=True)


class Demande_location(models.Model):
    date_mise_a_jour = models.DateTimeField(verbose_name="Date de mise a jour", auto_now=True)
    conducteur = models.ForeignKey(Conducteur, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    en_cours = models.BooleanField(default=True)
    accepter = models.BooleanField(default=False)
    refuser = models.BooleanField(default=False)
    paniers = models.ManyToManyField(Vehicule)


class Location(models.Model):
    date_mise_a_jour = models.DateTimeField(verbose_name="Date de mise a jour", auto_now=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    demande_location = models.ForeignKey(Demande_location, on_delete=models.SET_NULL, null=True)
    date_depart = models.DateTimeField()
    niveau_carburant = models.IntegerField()
    duree_deplacement = models.CharField(max_length=250, )
    depart = models.BooleanField(default=False)
    arrivee = models.BooleanField(default=False)
    kilometrage_depart = models.IntegerField()
    statut = models.CharField(
        max_length=50,
        choices=[
            ('en cours', 'En cours...'),
            ('arrivée', 'Arrivée')
        ],
        default='en cours'
    )


class Demande_prolongement(models.Model):
    date_mise_a_jour = models.DateTimeField(verbose_name="Date de mise a jour", auto_now=True)
    date_reponse = models.DateTimeField(blank=True, null=True)
    conducteur = models.ForeignKey(Conducteur, on_delete=models.SET_NULL, null=True)
    duree = models.IntegerField()
    motif = models.CharField(max_length=250)
    en_cours = models.BooleanField(default=True)
    accepter = models.BooleanField(default=False)
    refuser = models.BooleanField(default=False)
    deplacement = models.ForeignKey(Deplacement, on_delete=models.SET_NULL, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    kilometrage = models.IntegerField()
    lu = models.BooleanField(default=False)
    photo_jauge_demande = models.ImageField(upload_to='jaugeDemandeProlongement/', null=True, blank=True)
    date_premiere = models.DateField(auto_now_add=True, null=True)
    motif_refus = models.CharField(max_length=250, blank=True, null=True)

    @property
    def time_since_reponse(self):
        if self.date_reponse:
            time_since_reponse = timesince(self.date_reponse)
            return f"il y a {time_since_reponse}"

    def __str__(self):
        return f"{self.conducteur.numero_permis_conduire} {self.conducteur.numero_permis_conduire}"


class Carburant(models.Model):
    date_mise_a_jour = models.DateTimeField(verbose_name="Date de mise a jour", auto_now=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    type = models.ForeignKey(type_carburant, on_delete=models.SET_NULL, blank=False, null=True)
    prix_total = models.IntegerField()
    quantite = models.FloatField()
    date_premiere = models.DateField(auto_now_add=True, null=True)

    def prix_total_format(self):
        return "{:,.2f}".format(self.prix_total)


class Entretien(models.Model):
    date_mise_a_jour = models.DateTimeField(verbose_name="Date de mise a jour", auto_now=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, blank=True, null=True)
    date_entretien = models.DateField()
    prix_entretient = models.IntegerField()
    description = models.TextField(blank=True)
    type = models.ForeignKey(type_entretien, on_delete=models.SET_NULL, null=True)
    recu = models.ImageField(upload_to='recu/', blank=False)


class EtatArrive(models.Model):
    date_mise_a_jour = models.DateTimeField(verbose_name="Date de mise a jour", auto_now=True)
    deplacement = models.ForeignKey(Deplacement, on_delete=models.SET_NULL, blank=True, null=True,
                                    related_name='deplacement_etat')
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='utilisateur_etat')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True)
    kilometrage_arrive = models.IntegerField()
    date_arrive = models.DateField(auto_now=True)
    photo_jauge_arrive = models.ImageField(upload_to='jaugeArrive/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.date_arrive:
            self.date_arrive = timezone.now()
        super().save(*args, **kwargs)


class Incident(models.Model):
    date_mise_a_jour = models.DateTimeField(verbose_name="Date de mise a jour", auto_now=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    conducteur = models.ForeignKey(Conducteur, on_delete=models.SET_NULL, null=True)
    deplacement = models.ForeignKey(Deplacement, on_delete=models.SET_NULL, null=True)
    description_incident = models.TextField()
    utilisateurs = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='gestionnaire',
                                     blank=True)
    date_premiere = models.DateField(auto_now_add=True, null=True, )


class Photo(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    images = models.ImageField(upload_to='Images/', null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True)
    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, blank=True, null=True)
    demande_prolongement = models.ForeignKey(Demande_prolongement, on_delete=models.SET_NULL, blank=True, null=True)
    etat_arrive = models.ForeignKey(EtatArrive, on_delete=models.SET_NULL, blank=True, null=True)
    deplacement = models.ForeignKey(Deplacement, on_delete=models.SET_NULL, blank=True, null=True)
