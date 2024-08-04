from django.contrib import admin
from .models import Lot, Processus, LotProcessus, Message

admin.site.register(Lot)
admin.site.register(Processus)
admin.site.register(LotProcessus)
admin.site.register(Message)  # Ajout du modèle Message