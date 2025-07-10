from django.contrib import admin
from .models import (
    Farmacia, User, CargaDatos, Presentacion, Liquidacion,
    LiquidacionGaleno, LiquidacionPAMI, LiquidacionJerarquicos,
    LiquidacionOspil, LiquidacionOsfatlyf, LiquidacionPAMIOncologico,
    LiquidacionPAMIPanales, LiquidacionPAMIVacunas, LiquidacionAndinaART,
    LiquidacionAsociart, LiquidacionColoniaSuiza, LiquidacionExperta,
    LiquidacionGalenoART, LiquidacionPrevencionART,
    Publication, PublicationLike, PublicationComment, Reclamo,
)

# Register your models here.

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('usuario_creacion', 'categoria', 'fecha_creacion', 'likes_count', 'comentarios_count')
    list_filter = ('categoria', 'fecha_creacion', 'usuario_creacion')
    search_fields = ('descripcion', 'usuario_creacion__username', 'usuario_creacion__first_name', 'usuario_creacion__last_name')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'likes_count', 'comentarios_count')
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = (
        ('Información básica', {
            'fields': ('descripcion', 'categoria')
        }),
        ('Archivos adjuntos', {
            'fields': ('imagen', 'archivo'),
            'classes': ('collapse',)
        }),
        ('Usuarios', {
            'fields': ('usuario_creacion', 'usuario_modificacion')
        }),
        ('Fechas y contadores', {
            'fields': ('fecha_creacion', 'fecha_modificacion', 'likes_count', 'comentarios_count'),
            'classes': ('collapse',)
        })
    )


@admin.register(PublicationLike)
class PublicationLikeAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'publicacion', 'fecha_like')
    list_filter = ('fecha_like', 'usuario')
    search_fields = ('usuario__username', 'publicacion__descripcion')
    readonly_fields = ('fecha_like',)
    date_hierarchy = 'fecha_like'


@admin.register(PublicationComment)
class PublicationCommentAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'publicacion', 'fecha_comentario', 'contenido_preview')
    list_filter = ('fecha_comentario', 'usuario')
    search_fields = ('contenido', 'usuario__username', 'publicacion__descripcion')
    readonly_fields = ('fecha_comentario',)
    date_hierarchy = 'fecha_comentario'
    
    def contenido_preview(self, obj):
        return obj.contenido[:50] + '...' if len(obj.contenido) > 50 else obj.contenido
    contenido_preview.short_description = 'Contenido'


@admin.register(Reclamo)
class ReclamoAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'usuario_creador', 'estado', 'fecha_creacion', 'notificaciones_activas', 'es_publico', 'is_deleted')
    list_filter = ('estado', 'notificaciones_activas', 'es_publico', 'is_deleted')
    search_fields = ('titulo', 'descripcion', 'usuario_creador__username')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'fecha_resolucion')
