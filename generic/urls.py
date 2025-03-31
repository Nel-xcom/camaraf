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

    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('buscar_usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
    path('usuario/actualizar/', views.actualizar_usuario, name='actualizar_usuario'),

    path('calendario/', views.calendario, name="calendario"),
    path('calendar/', views.calendar_farmacias, name="calendario_farmacias"),
    path('api/get_presentaciones/', views.get_presentaciones, name="get_presentaciones"),
    path('guardar_presentacion/', views.guardar_presentacion, name="guardar_presentacion"),
    path('eliminar_presentacion/<int:presentacion_id>/', views.eliminar_presentacion, name='eliminar_presentacion'),

    path('resumen-cobro/', views.resumen_cobro, name='resumen_cobro'),
    
    path('homeliquidacion/', views.home_liquidacion, name='hliquidacion'),
    path("cargar-liquidacion-galeno/", views.cargar_liquidacion_galeno, name="cargar_liquidacion_galeno"),
    path("eliminar-liquidacion-galeno/", views.eliminar_liquidacion_galeno, name="eliminar_liquidacion_galeno"),
    path("cargar-liquidacion-pami/", views.cargar_liquidacion_pami, name="cargar_liquidacion_pami"),
    path("eliminar-liquidacion/", views.eliminar_liquidacion_pami, name="eliminar_liquidacion_pami"),
    path("cargar-liquidacion-pami-oncologico/", views.cargar_liquidacion_pami_oncologico, name="cargar_liquidacion_pami_oncologico"),
    path("eliminar-liquidacion-pami-oncologico/", views.eliminar_liquidacion_pami_oncologico, name="eliminar_liquidacion_pami_oncologico"),
    path("cargar-liquidacion-pami-panales/", views.cargar_liquidacion_pami_panales, name="cargar_liquidacion_pami_panales"),
    path("eliminar-liquidacion-pami-panales/", views.eliminar_liquidacion_pami_panales, name="eliminar_liquidacion_pami_panales"),
    path("cargar-liquidacion-pami-vacunas/", views.cargar_liquidacion_pami_vacunas, name="cargar_liquidacion_pami_vacunas"),
    path("eliminar-liquidacion-pami-vacunas/", views.eliminar_liquidacion_pami_vacunas, name="eliminar_liquidacion_pami_vacunas"),
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
]