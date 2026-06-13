from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('veterinario', 'Veterinario'),
        ('dueno', 'Dueño'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    numero_colegiado = models.CharField(max_length=50, blank=True, null=True)

class Animal(models.Model):
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    dueno = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'dueno'}
    )

    def __str__(self):
        return f'{self.nombre} ({self.especie})'

class Tratamiento(models.Model):
    nombre = models.CharField(max_length=100)
    apto_para_intervenciones = models.BooleanField()

    def __str__(self):
        return self.nombre

class Intervencion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE)
    animales = models.ManyToManyField('Animal')
    nivel_riesgo = models.IntegerField()
    fecha_programada = models.DateField()
    fecha_fin_recuperacion = models.DateField()
    completada = models.BooleanField(default=False)
    veterinario_responsable = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='intervenciones',
        limit_choices_to={'rol': 'veterinario'}
    )

    def __str__(self):
        return self.nombre