# Generated by Django 5.1.6 on 2025-07-10 09:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_reclamo_asignados_alter_reclamo_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReclamoComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField(help_text='Contenido del comentario')),
                ('fecha_comentario', models.DateTimeField(auto_now_add=True, help_text='Fecha y hora del comentario')),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='reclamos/comentarios/imagenes/')),
                ('archivo', models.FileField(blank=True, null=True, upload_to='reclamos/comentarios/archivos/')),
                ('is_deleted', models.BooleanField(default=False, help_text='Indica si el comentario fue eliminado (borrado lógico)')),
                ('parent', models.ForeignKey(blank=True, help_text='Comentario padre si es una respuesta', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='core.reclamocomment')),
                ('reclamo', models.ForeignKey(help_text='Reclamo al que pertenece el comentario', on_delete=django.db.models.deletion.CASCADE, related_name='comentarios', to='core.reclamo')),
                ('usuario', models.ForeignKey(help_text='Usuario que realizó el comentario', on_delete=django.db.models.deletion.CASCADE, related_name='reclamo_comentarios_realizados', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Comentario de Reclamo',
                'verbose_name_plural': 'Comentarios de Reclamos',
                'ordering': ['fecha_comentario'],
            },
        ),
    ]
