from django.core.management.base import BaseCommand
from core.utils import regenerar_duracion_videos

class Command(BaseCommand):
    help = 'Regenera la duración de todos los videos que tengan duración vacía o 00:00.'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando regeneración de duración de videos...')
        success = regenerar_duracion_videos()
        if success:
            self.stdout.write(self.style.SUCCESS('Duración de videos actualizada correctamente.'))
        else:
            self.stdout.write(self.style.WARNING('No se actualizó la duración de ningún video.')) 