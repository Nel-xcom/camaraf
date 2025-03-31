# core/tasks.py
from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Notificacion, CustomUser

User = get_user_model()

def enviar_notificacion_a_usuario(notificacion):
    usuarios = CustomUser.objects.filter(sector=notificacion.tarea.sector)
    for usuario in usuarios:
        print(f"Enviando notificación a {usuario.username}: {notificacion.titulo}")
    # Esta función podría registrar el envío en un modelo de "Historial" si se requiere seguimiento de envíos


@shared_task
def enviar_notificaciones_programadas():
    now = timezone.now()
    dia_hoy = now.strftime("%A").lower()
    hora_actual = now.time()

    # Filtra solo las notificaciones activas, no leídas y programadas para el día y hora actuales
    notificaciones = Notificacion.objects.filter(
        dia__in=[dia_hoy, 'todos'],
        hora_envio__hour=hora_actual.hour,
        hora_envio__minute=hora_actual.minute,
        activo=True,
        enviar_ahora=False,
        leida=False
    )

    for notificacion in notificaciones:
        enviar_notificacion_a_usuario(notificacion)
        # Marcar como leída para evitar reenvío
        notificacion.leida = True
        notificacion.save()


@shared_task
def enviar_notificacion_tarea(solicitante, destinatario_id, descripcion):
    try:
        destinatario = CustomUser.objects.get(id=destinatario_id)
        mensaje = f"Tienes una nueva solicitud de tarea de {solicitante}: {descripcion}"
        # Crear la notificación
        Notificacion.objects.create(
            usuario=destinatario,
            mensaje=mensaje,
            leida=False
        )
        return f"Notificación enviada a {destinatario.username}"
    except CustomUser.DoesNotExist:
        return f"Usuario con ID {destinatario_id} no encontrado."