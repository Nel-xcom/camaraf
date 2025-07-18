# Generated by Django 5.1.6 on 2025-07-10 05:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_alter_cargadatos_periodo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField(help_text='Contenido de la publicación')),
                ('categoria', models.CharField(choices=[('obra-social', 'Obra social'), ('anuncio', 'Anuncio'), ('recordatorio', 'Recordatorio')], help_text='Categoría de la publicación', max_length=20)),
                ('imagen', models.ImageField(blank=True, help_text='Imagen adjunta a la publicación', null=True, upload_to='publicaciones/imagenes/')),
                ('archivo', models.FileField(blank=True, help_text='Archivo adjunto a la publicación', null=True, upload_to='publicaciones/archivos/')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, help_text='Fecha y hora de creación')),
                ('fecha_modificacion', models.DateTimeField(auto_now=True, help_text='Fecha y hora de la última modificación')),
                ('likes_count', models.PositiveIntegerField(default=0, help_text='Número total de likes')),
                ('comentarios_count', models.PositiveIntegerField(default=0, help_text='Número total de comentarios')),
                ('usuario_creacion', models.ForeignKey(help_text='Usuario que creó la publicación', on_delete=django.db.models.deletion.CASCADE, related_name='publicaciones_creadas', to=settings.AUTH_USER_MODEL)),
                ('usuario_modificacion', models.ForeignKey(blank=True, help_text='Usuario que modificó la publicación por última vez', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='publicaciones_modificadas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Publicación',
                'verbose_name_plural': 'Publicaciones',
                'ordering': ['-fecha_creacion'],
            },
        ),
        migrations.CreateModel(
            name='PublicationComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField(help_text='Contenido del comentario')),
                ('fecha_comentario', models.DateTimeField(auto_now_add=True, help_text='Fecha y hora del comentario')),
                ('publicacion', models.ForeignKey(help_text='Publicación a la que pertenece el comentario', on_delete=django.db.models.deletion.CASCADE, related_name='comentarios', to='core.publication')),
                ('usuario', models.ForeignKey(help_text='Usuario que realizó el comentario', on_delete=django.db.models.deletion.CASCADE, related_name='comentarios_realizados', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Comentario de Publicación',
                'verbose_name_plural': 'Comentarios de Publicaciones',
                'ordering': ['fecha_comentario'],
            },
        ),
        migrations.CreateModel(
            name='PublicationLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_like', models.DateTimeField(auto_now_add=True, help_text='Fecha y hora del like')),
                ('publicacion', models.ForeignKey(help_text='Publicación que recibió el like', on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='core.publication')),
                ('usuario', models.ForeignKey(help_text='Usuario que dio el like', on_delete=django.db.models.deletion.CASCADE, related_name='likes_dados', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Like de Publicación',
                'verbose_name_plural': 'Likes de Publicaciones',
                'ordering': ['-fecha_like'],
                'unique_together': {('publicacion', 'usuario')},
            },
        ),
    ]
