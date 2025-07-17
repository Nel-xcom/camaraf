"""generic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register_farmacia, name='register_farmacia'),
    path('login/', views.login_view, name='login'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('gestionar-presentaciones/', views.gestionar_presentaciones, name='gestionar_presentaciones'),
    path('cargar-datos/<str:obra_social>/', views.cargar_datos, name='cargar_datos'),
    path('presentacion_exitosa/<int:carga_datos_id>/', views.presentacion_exitosa, name='presentacion_exitosa'),
    path('observaciones/', views.observaciones, name='observaciones'),
    path('actualizar_estado_presentacion/<int:id>/', views.actualizar_estado_presentacion, name='actualizar_estado_presentacion'),

    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('buscar_usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
    path('usuario/actualizar/', views.actualizar_usuario, name='actualizar_usuario'),
    path('usuario/<int:user_id>/detalle_json/', views.usuario_detalle_json, name='usuario_detalle_json'),
    path('usuario/<int:user_id>/actualizar_json/', views.usuario_actualizar_json, name='usuario_actualizar_json'),

    path('calendario/', views.calendario, name="calendario"),
    path('get_presentaciones_listado/', views.get_presentaciones_listado, name='get_presentaciones_listado'),
    path('calendar/', views.calendar_farmacias, name="calendario_farmacias"),
    path('api/get_presentaciones/', views.get_presentaciones, name="get_presentaciones"),
    path('guardar_presentacion/', views.guardar_presentacion, name="guardar_presentacion"),
    path('eliminar_presentacion/<int:presentacion_id>/', views.eliminar_presentacion, name='eliminar_presentacion'),
    path('eliminar_presentacion_calendario/<int:presentacion_id>/', views.eliminar_presentacion_calendario, name='eliminar_presentacion_calendario'),

    path('resumen-cobro/', views.resumen_cobro, name='resumen_cobro'),
    
    path('homeliquidacion/', views.home_liquidacion, name='hliquidacion'),
    path("cargar-liquidacion-galeno/", views.cargar_liquidacion_galeno, name="cargar_liquidacion_galeno"),
    path("eliminar-liquidacion-galeno/", views.eliminar_liquidacion_galeno, name="eliminar_liquidacion_galeno"),
    path("cargar-liquidacion-pami/", views.cargar_liquidacion_pami, name="cargar_liquidacion_pami"),
    path("editar-titulo-liquidacion/", views.editar_titulo_liquidacion, name="editar_titulo_liquidacion"),
    path("eliminar-liquidacion/", views.eliminar_liquidacion_pami, name="eliminar_liquidacion_pami"),
    path("cargar-liquidacion-pami-oncologico/", views.cargar_liquidacion_pami_oncologico, name="cargar_liquidacion_pami_oncologico"),
    path("eliminar-liquidacion-pami-oncologico/", views.eliminar_liquidacion_pami_oncologico, name="eliminar_liquidacion_pami_oncologico"),
    path("cargar-liquidacion-pami-panales/", views.cargar_liquidacion_pami_panales, name="cargar_liquidacion_pami_panales"),
    path("eliminar-liquidacion-pami-panales/", views.eliminar_liquidacion_pami_panales, name="eliminar_liquidacion_pami_panales"),
    path("cargar-liquidacion-pami-vacunas/", views.cargar_liquidacion_pami_vacunas, name="cargar_liquidacion_pami_vacunas"),
    path("eliminar-liquidacion-pami-vacunas/", views.eliminar_liquidacion_pami_vacunas, name="eliminar_liquidacion_pami_vacunas"),
    path("cargar-liquidacion-pami-nutricional/", views.cargar_liquidacion_pami_nutricional, name="cargar_liquidacion_pami_nutricional"),
    path("cargar-liquidacion-jerarquicos/", views.cargar_liquidacion_jerarquicos, name="cargar_liquidacion_jerarquicos"),
    path("eliminar-liquidacion-jerarquicos/", views.eliminar_liquidacion_jerarquicos, name="eliminar_liquidacion_jerarquicos"),
    path('cargar-liquidacion-ospil/', views.cargar_liquidacion_ospil, name='cargar_liquidacion_ospil'),
    path('eliminar-liquidacion-ospil/', views.eliminar_liquidacion_ospil, name='eliminar_liquidacion_ospil'),
    path('cargar-liquidacion-osfatlyf/', views.cargar_liquidacion_osfatlyf, name='cargar_liquidacion_osfatlyf'),
    path('eliminar-liquidacion-osfatlyf/', views.eliminar_liquidacion_osfatlyf, name='eliminar_liquidacion_osfatlyf'),
    path("cargar-liquidacion-andina-art/", views.cargar_liquidacion_andina_art, name="cargar_liquidacion_andina_art"),
    path("eliminar-liquidacion-andina-art/", views.eliminar_liquidacion_andina_art, name="eliminar_liquidacion_andina_art"),
    path("cargar-liquidacion-asociart/", views.cargar_liquidacion_asociart, name="cargar_liquidacion_asociart"),
    path("eliminar-liquidacion-asociart/", views.eliminar_liquidacion_asociart, name="eliminar_liquidacion_asociart"),
    path("cargar-liquidacion-coloniasuiza/", views.cargar_liquidacion_coloniasuiza, name="cargar_liquidacion_coloniasuiza"),
    path("eliminar-liquidacion-coloniasuiza/", views.eliminar_liquidacion_coloniasuiza, name="eliminar_liquidacion_coloniasuiza"),
    path("cargar-liquidacion-experta/", views.cargar_liquidacion_experta, name="cargar_liquidacion_experta"),
    path("eliminar-liquidacion-experta/", views.eliminar_liquidacion_experta, name="eliminar_liquidacion_experta"),
    path("cargar-liquidacion-galenoart/", views.cargar_liquidacion_galenoart, name="cargar_liquidacion_galenoart"),
    path("eliminar-liquidacion-galenoart/", views.eliminar_liquidacion_galenoart, name="eliminar_liquidacion_galenoart"),
    path("cargar-liquidacion-prevencion-art/", views.cargar_liquidacion_prevencion_art, name="cargar_liquidacion_prevencion_art"),
    path("eliminar-liquidacion-prevencion-art/", views.eliminar_liquidacion_prevencion_art, name="eliminar_liquidacion_prevencion_art"),

    path("transferencias/", views.transferencias_tesorera, name="transferencias"),

    path("panel-liquidaciones/", views.panel_liquidaciones, name="panel_liquidaciones"),

    path("foro/", views.foro, name="foro"),
    path("foro/crear-publicacion/", views.crear_publicacion, name="crear_publicacion"),
    path("foro/publicacion/<int:publicacion_id>/like/", views.toggle_like, name="toggle_like"),
    path("foro/publicacion/<int:publicacion_id>/comentar/", views.crear_comentario, name="crear_comentario"),
    path("foro/publicacion/<int:publicacion_id>/eliminar/", views.eliminar_publicacion, name="eliminar_publicacion"),
    path("foro/publicacion/<int:publicacion_id>/comentarios/", views.obtener_comentarios, name="obtener_comentarios"),
    path("foro/comentario/<int:comentario_id>/eliminar/", views.eliminar_comentario, name="eliminar_comentario"),
    path("foro/comentario/<int:comentario_id>/responder/", views.responder_comentario, name="responder_comentario"),
    path("foro/reclamos/crear/", views.crear_reclamo, name="crear_reclamo"),
    path("foro/reclamos/listar/", views.listar_reclamos, name="listar_reclamos"),
    path("foro/reclamos/resueltos/", views.listar_reclamos_resueltos, name="listar_reclamos_resueltos"),
    path("foro/reclamos/<int:reclamo_id>/cambiar-estado/", views.cambiar_estado_reclamo, name="cambiar_estado_reclamo"),
    path("foro/reclamos/<int:reclamo_id>/eliminar/", views.eliminar_reclamo, name="eliminar_reclamo"),
    path("foro/reclamos/<int:reclamo_id>/toggle-notificaciones/", views.toggle_notificaciones_reclamo, name="toggle_notificaciones_reclamo"),
    path("foro/reclamos/<int:reclamo_id>/detalle/", views.detalle_reclamo, name="detalle_reclamo"),
    path("foro/reclamos/<int:reclamo_id>/comentarios/", views.comentarios_reclamo, name="comentarios_reclamo"),
    path("foro/reclamos/<int:reclamo_id>/comentar/", views.comentar_reclamo, name="comentar_reclamo"),
    path("foro/reclamos/<int:reclamo_id>/asignar/", views.asignar_reclamo, name="asignar_reclamo"),
    path("foro/reclamos/usuarios-asignables/", views.usuarios_asignables_reclamo, name="usuarios_asignables_reclamo"),
    path("foro/reclamos/estados/", views.estados_reclamo, name="estados_reclamo"),
    path("foro/reclamos/comentario/<int:comentario_id>/responder/", views.responder_comentario_reclamo, name="responder_comentario_reclamo"),
    path("foro/reclamos/comentario/<int:comentario_id>/eliminar/", views.eliminar_comentario_reclamo, name="eliminar_comentario_reclamo"),
    path("guias-uso/", views.guias_uso, name="guias_uso"),
    path("guias-uso/subir-video/", views.subir_video, name="subir_video"),
    path("guias-uso/subir-archivo/", views.subir_archivo, name="subir_archivo"),
    path("guias-uso/video/<int:video_id>/reproducir/", views.reproducir_video, name="reproducir_video"),
    path("guias-uso/archivo/<int:archivo_id>/descargar/", views.descargar_archivo, name="descargar_archivo"),
    path("guias-uso/video/<int:video_id>/descargar/", views.descargar_video, name="descargar_video"),
    path("guias-uso/regenerar-thumbnails/", views.regenerar_thumbnails, name="regenerar_thumbnails"),
    path("notificaciones/", views.notificaciones_usuario, name="notificaciones_usuario"),
    path("notificaciones/<int:notificacion_id>/leer/", views.marcar_notificacion_leida, name="marcar_notificacion_leida"),
    path("notificaciones/marcar-todas-leidas/", views.marcar_todas_notificaciones_leidas, name="marcar_todas_notificaciones_leidas"),
    path("guias-uso/video/<int:video_id>/eliminar/", views.eliminar_video, name="eliminar_video"),
    path("cargar-liquidacion-lasegundaart/", views.cargar_liquidacion_lasegundaart, name="cargar_liquidacion_lasegundaart"),
    path("eliminar-liquidacion-lasegundaart/", views.eliminar_liquidacion_lasegundaart, name="eliminar_liquidacion_lasegundaart"),
    path("cargar-liquidacion-osdipp/", views.cargar_liquidacion_osdipp, name="cargar_liquidacion_osdipp"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)