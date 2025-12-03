from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings

from django.db import models
from django.contrib.auth.models import User

from rest_framework.authentication import TokenAuthentication

class BearerTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"


class Administradores(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    clave_admin = models.CharField(max_length=255,null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    rfc = models.CharField(max_length=255,null=True, blank=True)
    fecha_nacimiento = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    ocupacion = models.CharField(max_length=255,null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del admin "+self.first_name+" "+self.last_name
    
class Alumnos(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    matricula = models.CharField(max_length=255,null=True, blank=True)
    curp = models.CharField(max_length=255,null=True, blank=True)
    rfc = models.CharField(max_length=255,null=True, blank=True)
    fecha_nacimiento = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    ocupacion = models.CharField(max_length=255,null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del alumno "+self.first_name+" "+self.last_name
    
class Maestros(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    id_trabajador = models.CharField(max_length=255,null=True, blank=True)
    fecha_nacimiento = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    rfc = models.CharField(max_length=255,null=True, blank=True)
    cubiculo = models.CharField(max_length=255,null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    area_investigacion = models.CharField(max_length=255,null=True, blank=True)
    materias_json = models.TextField(null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del maestro "+self.first_name+" "+self.last_name

class EventoAcademico(models.Model):
    TIPO_CHOICES = [
        ('conferencia', 'Conferencia'),
        ('taller', 'Taller'),
        ('seminario', 'Seminario'),
        ('concurso', 'Concurso'),
    ]
    
    PUBLICO_CHOICES = [
        ('estudiantes', 'Estudiantes'),
        ('profesores', 'Profesores'),
        ('publico_general', 'Público General'),
    ]
    
    PROGRAMA_CHOICES = [
        ('ingenieria_ciencias_computacion', 'Ingeniería en Ciencias de la Computación'),
        ('licenciatura_ciencias_computacion', 'Licenciatura en Ciencias de la Computación'),
        ('ingenieria_tecnologias_informacion', 'Ingeniería en Tecnologías de la Información'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=False, blank=False)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, null=False, blank=False)
    fecha = models.DateField(null=False, blank=False)
    hora_inicio = models.TimeField(null=False, blank=False)
    hora_fin = models.TimeField(null=False, blank=False)
    lugar = models.CharField(max_length=200, null=False, blank=False)
    publico_objetivo = models.CharField(max_length=20, choices=PUBLICO_CHOICES, null=False, blank=False)
    programa_educativo = models.CharField(max_length=50, choices=PROGRAMA_CHOICES, null=True, blank=True)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos_responsable')
    descripcion = models.TextField(max_length=300, null=False, blank=False)
    cupo_maximo = models.IntegerField(null=False, blank=False)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Evento: {self.nombre} - {self.fecha}"
    
    class Meta:
        verbose_name = "Evento Académico"
        verbose_name_plural = "Eventos Académicos"
        ordering = ['-fecha', '-hora_inicio']
