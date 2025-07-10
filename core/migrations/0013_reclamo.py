from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0012_alter_cargadatos_periodo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reclamo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('descripcion', models.TextField()),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('en_progreso', 'En progreso'), ('resuelto', 'Resuelto'), ('cerrado', 'Cerrado')], default='pendiente', max_length=20)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('fecha_resolucion', models.DateTimeField(blank=True, null=True)),
                ('notificaciones_activas', models.BooleanField(default=True)),
                ('es_publico', models.BooleanField(default=True)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='reclamos/imagenes/')),
                ('archivo', models.FileField(blank=True, null=True, upload_to='reclamos/archivos/')),
                ('is_deleted', models.BooleanField(default=False)),
                ('usuario_asignado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reclamos_asignados', to='core.user')),
                ('usuario_creador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reclamos_creados', to='core.user')),
                ('ultima_actualizacion_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reclamos_actualizados', to='core.user')),
            ],
            options={
                'verbose_name': 'Reclamo',
                'verbose_name_plural': 'Reclamos',
                'ordering': ['-fecha_creacion'],
            },
        ),
    ] 