from django.core.management.base import BaseCommand
from core.utils import regenerar_thumbnails_pendientes
from core.models import GuiaVideo


class Command(BaseCommand):
    help = 'Regenera thumbnails para videos que no los tienen'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar regeneración de todos los thumbnails (incluso los que ya existen)',
        )

    def handle(self, *args, **options):
        self.stdout.write('Iniciando proceso de regeneración de thumbnails...')
        
        if options['force']:
            # Regenerar todos los thumbnails
            videos = GuiaVideo.objects.all()
            self.stdout.write(f'Regenerando thumbnails para {videos.count()} videos...')
        else:
            # Solo videos sin thumbnail
            videos = GuiaVideo.objects.filter(thumbnail__isnull=True)
            self.stdout.write(f'Encontrados {videos.count()} videos sin thumbnail.')
        
        if not videos.exists():
            self.stdout.write(
                self.style.SUCCESS('No hay videos que requieran regeneración de thumbnails.')
            )
            return
        
        exitosos = 0
        fallidos = 0
        
        for video in videos:
            try:
                from core.utils import generar_thumbnail_para_guia_video
                if generar_thumbnail_para_guia_video(video):
                    exitosos += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Thumbnail regenerado para: {video.titulo}')
                    )
                else:
                    fallidos += 1
                    self.stdout.write(
                        self.style.WARNING(f'✗ No se pudo regenerar thumbnail para: {video.titulo}')
                    )
            except Exception as e:
                fallidos += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error regenerando thumbnail para {video.titulo}: {e}')
                )
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'Proceso completado: {exitosos} exitosos, {fallidos} fallidos')
        ) 