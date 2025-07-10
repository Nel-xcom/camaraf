from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Publication, PublicationLike, PublicationComment
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea publicaciones de ejemplo para el foro'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Número de publicaciones a crear (default: 10)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Obtener usuarios existentes
        users = User.objects.all()
        if not users.exists():
            self.stdout.write(
                self.style.ERROR('No hay usuarios en el sistema. Crea usuarios primero.')
            )
            return
        
        # Contenido de ejemplo
        sample_content = [
            "Excelente iniciativa la nueva funcionalidad de liquidaciones. Ha simplificado mucho nuestro trabajo diario.",
            "¿Alguien puede ayudarme con el proceso de carga de datos? Tengo algunas dudas sobre el formato de los archivos CSV.",
            "Recomendación: Para optimizar el rendimiento, asegúrense de cerrar las pestañas del navegador que no estén usando.",
            "¿Hay alguna actualización programada para este fin de semana? Necesito planificar el mantenimiento de mi farmacia.",
            "El sistema de notificaciones está funcionando perfectamente. ¡Muy útil!",
            "¿Alguien más ha notado la mejora en los tiempos de carga?",
            "Importante recordatorio: Revisen sus datos antes de enviar las presentaciones.",
            "La nueva interfaz es mucho más intuitiva. ¡Felicitaciones al equipo de desarrollo!",
            "¿Tienen alguna sugerencia para mejorar el proceso de liquidaciones?",
            "El soporte técnico ha sido muy eficiente últimamente. ¡Gracias!",
            "¿Alguien sabe cuándo estará disponible la nueva funcionalidad de reportes?",
            "Excelente trabajo con las actualizaciones de seguridad.",
            "La documentación está muy completa. ¡Muy útil para nuevos usuarios!",
            "¿Hay algún tutorial disponible para las nuevas funciones?",
            "El sistema está funcionando de manera óptima. ¡Excelente trabajo!"
        ]
        
        categories = ['obra-social', 'anuncio', 'recordatorio']
        
        # Crear publicaciones
        publications_created = 0
        for i in range(count):
            # Seleccionar usuario aleatorio
            user = random.choice(users)
            
            # Seleccionar contenido y categoría aleatorios
            content = random.choice(sample_content)
            category = random.choice(categories)
            
            # Crear publicación con fecha aleatoria (últimos 30 días)
            days_ago = random.randint(0, 30)
            created_date = timezone.now() - timedelta(days=days_ago)
            
            publication = Publication.objects.create(
                descripcion=content,
                categoria=category,
                usuario_creacion=user,
                usuario_modificacion=user,
                fecha_creacion=created_date,
                fecha_modificacion=created_date
            )
            
            # Agregar algunos likes aleatorios
            like_users = random.sample(list(users), min(random.randint(0, 5), len(users)))
            for like_user in like_users:
                PublicationLike.objects.create(
                    publicacion=publication,
                    usuario=like_user,
                    fecha_like=created_date + timedelta(minutes=random.randint(1, 60))
                )
            
            # Agregar algunos comentarios aleatorios
            comment_users = random.sample(list(users), min(random.randint(0, 3), len(users)))
            comment_content = [
                "¡Muy buena observación!",
                "Estoy de acuerdo contigo.",
                "Gracias por compartir esta información.",
                "Interesante punto de vista.",
                "Esto es muy útil, gracias.",
                "¿Podrías dar más detalles?",
                "Excelente sugerencia.",
                "Esto me ayudó mucho.",
                "¿Alguien más ha experimentado esto?",
                "¡Perfecto! Justo lo que necesitaba."
            ]
            
            for j, comment_user in enumerate(comment_users):
                PublicationComment.objects.create(
                    publicacion=publication,
                    usuario=comment_user,
                    contenido=random.choice(comment_content),
                    fecha_comentario=created_date + timedelta(hours=j+1)
                )
            
            publications_created += 1
            self.stdout.write(f'Publicación {i+1} creada: {content[:50]}...')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Se crearon {publications_created} publicaciones de ejemplo exitosamente.'
            )
        ) 