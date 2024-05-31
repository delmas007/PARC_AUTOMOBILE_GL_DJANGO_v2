import threading

from django.apps import AppConfig


class VehiculeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vehicule'

    def ready(self):
        import vehicule.startup  # Importez le script de démarrage
        threading.Thread(target=vehicule.startup.start_scheduler, daemon=True).start()
