from django.db.models import Q
from django.db import transaction
from dev_sistema_escolar_api.serializers import EventoAcademicoSerializer, UserSerializer
from dev_sistema_escolar_api.models import EventoAcademico
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404

class EventosAll(generics.CreateAPIView):
    """
    GET: Obtener todos los eventos académicos filtrados por rol del usuario
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        # Obtener el grupo/rol del usuario autenticado
        user_groups = request.user.groups.values_list('name', flat=True)
        
        # Filtrado según el rol del usuario
        if 'administrador' in user_groups:
            # Administradores ven todos los eventos
            eventos = EventoAcademico.objects.all().order_by('-fecha', '-hora_inicio')
        elif 'maestro' in user_groups:
            # Maestros ven eventos para profesores y público general
            eventos = EventoAcademico.objects.filter(
                Q(publico_objetivo='profesores') | Q(publico_objetivo='publico_general')
            ).order_by('-fecha', '-hora_inicio')
        elif 'alumno' in user_groups:
            # Alumnos ven eventos para estudiantes y público general
            eventos = EventoAcademico.objects.filter(
                Q(publico_objetivo='estudiantes') | Q(publico_objetivo='publico_general')
            ).order_by('-fecha', '-hora_inicio')
        else:
            # Si no tiene rol, no ve nada
            eventos = EventoAcademico.objects.none()
        
        lista = EventoAcademicoSerializer(eventos, many=True).data
        return Response(lista, 200)

class EventosView(generics.CreateAPIView):
    """
    GET: Obtener evento por ID
    POST: Registrar nuevo evento (solo admin)
    PUT: Actualizar evento (solo admin)
    DELETE: Eliminar evento (solo admin)
    """
    
    def get_permissions(self):
        # GET requiere autenticación
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        # POST, PUT, DELETE requieren ser administrador
        return [permissions.IsAuthenticated()]
    
    def get(self, request, *args, **kwargs):
        """Obtener evento por ID"""
        evento = get_object_or_404(EventoAcademico, id=request.GET.get("id"))
        evento_data = EventoAcademicoSerializer(evento, many=False).data
        return Response(evento_data, 200)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Registrar nuevo evento académico (solo admin)"""
        # Verificar que el usuario sea administrador
        user_groups = request.user.groups.values_list('name', flat=True)
        if 'administrador' not in user_groups:
            return Response(
                {"error": "Solo los administradores pueden registrar eventos académicos"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validar datos del evento
        evento_serializer = EventoAcademicoSerializer(data=request.data)
        if evento_serializer.is_valid():
            # Obtener el responsable si se proporcionó
            responsable = None
            if 'responsable_id' in request.data and request.data['responsable_id']:
                responsable = get_object_or_404(User, id=request.data['responsable_id'])
            
            # Crear el evento
            evento = EventoAcademico.objects.create(
                nombre=request.data['nombre'],
                tipo=request.data['tipo'],
                fecha=request.data['fecha'],
                hora_inicio=request.data['hora_inicio'],
                hora_fin=request.data['hora_fin'],
                lugar=request.data['lugar'],
                publico_objetivo=request.data['publico_objetivo'],
                programa_educativo=request.data.get('programa_educativo', None),
                responsable=responsable,
                descripcion=request.data['descripcion'],
                cupo_maximo=request.data['cupo_maximo']
            )
            evento.save()
            
            return Response(
                {"evento_created_id": evento.id, "message": "Evento creado exitosamente"}, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(evento_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        """Actualizar evento académico (solo admin)"""
        # Verificar que el usuario sea administrador
        user_groups = request.user.groups.values_list('name', flat=True)
        if 'administrador' not in user_groups:
            return Response(
                {"error": "Solo los administradores pueden actualizar eventos académicos"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener el evento
        evento = get_object_or_404(EventoAcademico, id=request.data["id"])
        
        # Actualizar campos
        evento.nombre = request.data['nombre']
        evento.tipo = request.data['tipo']
        evento.fecha = request.data['fecha']
        evento.hora_inicio = request.data['hora_inicio']
        evento.hora_fin = request.data['hora_fin']
        evento.lugar = request.data['lugar']
        evento.publico_objetivo = request.data['publico_objetivo']
        evento.programa_educativo = request.data.get('programa_educativo', None)
        evento.descripcion = request.data['descripcion']
        evento.cupo_maximo = request.data['cupo_maximo']
        
        # Actualizar responsable si se proporcionó
        if 'responsable_id' in request.data:
            if request.data['responsable_id']:
                evento.responsable = get_object_or_404(User, id=request.data['responsable_id'])
            else:
                evento.responsable = None
        
        evento.save()
        
        return Response(EventoAcademicoSerializer(evento).data, 200)
    
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        """Eliminar evento académico (solo admin)"""
        # Verificar que el usuario sea administrador
        user_groups = request.user.groups.values_list('name', flat=True)
        if 'administrador' not in user_groups:
            return Response(
                {"error": "Solo los administradores pueden eliminar eventos académicos"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener el ID del evento
        evento_id = request.GET.get("id")
        if not evento_id:
            return Response(
                {"error": "Se requiere el parámetro 'id'"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener y eliminar el evento
        evento = get_object_or_404(EventoAcademico, id=evento_id)
        evento.delete()
        
        return Response(
            {"message": "Evento eliminado correctamente"}, 
            status=status.HTTP_200_OK
        )

class ResponsablesView(generics.ListAPIView):
    """
    GET: Obtener lista de maestros y administradores para seleccionar como responsables
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        # Obtener usuarios que son maestros o administradores
        maestros_group = Group.objects.filter(name='maestro').first()
        admin_group = Group.objects.filter(name='administrador').first()
        
        responsables = User.objects.filter(
            Q(groups=maestros_group) | Q(groups=admin_group),
            is_active=True
        ).distinct().order_by('first_name', 'last_name')
        
        # Serializar y agregar rol
        lista = []
        for user in responsables:
            user_data = UserSerializer(user).data
            
            # Determinar el rol
            user_groups = user.groups.values_list('name', flat=True)
            if 'administrador' in user_groups:
                user_data['rol'] = 'Administrador'
            elif 'maestro' in user_groups:
                user_data['rol'] = 'Maestro'
            else:
                user_data['rol'] = 'Desconocido'
            
            lista.append(user_data)
        
        return Response(lista, 200)

class TotalEventos(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        # Contar eventos por público objetivo
        estudiantes = EventoAcademico.objects.filter(publico_objetivo='estudiantes').count()
        profesores = EventoAcademico.objects.filter(publico_objetivo='profesores').count()
        publico_general = EventoAcademico.objects.filter(publico_objetivo='publico_general').count()
        
        return Response(
            {
                "estudiantes": estudiantes,
                "profesores": profesores,
                "publico_general": publico_general
            },
            status=200
        )
