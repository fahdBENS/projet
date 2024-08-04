from django.db import models
from django.utils import timezone

class Lot(models.Model):
    ref = models.CharField(max_length=20, primary_key=True)
    quantite = models.IntegerField()

    def __str__(self):
        return self.ref

class Processus(models.Model):
    id = models.AutoField(primary_key=True)
    nom_proc = models.CharField(max_length=100)
    responsable = models.CharField(max_length=100)
    duree = models.IntegerField(default=0)  # Durée en minutes

    def __str__(self):
        return self.nom_proc

class LotProcessus(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    processus = models.ForeignKey(Processus, on_delete=models.CASCADE)
    temps_debut = models.DateTimeField(null=True, blank=True)  # Permet les valeurs nulles
    temps_fin = models.DateTimeField(null=True, blank=True)  # Permet les valeurs nulles

    class Meta:
        unique_together = (('lot', 'processus'),)

class Message(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    processus = models.ForeignKey(Processus, on_delete=models.CASCADE)
    temps_reclamation = models.DateTimeField()
    le_message = models.TextField()
    responsable = models.CharField(max_length=255)

    class Meta:
        unique_together = (('lot', 'processus', 'temps_reclamation'),)
