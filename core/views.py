# ────────────────────────────────
# 🧩 Standard Library
# ────────────────────────────────
import calendar
import openpyxl
import pandas as pd
from collections import Counter, defaultdict
from datetime import datetime, date, timedelta
import json
from functools import wraps
from django.http import HttpResponseForbidden

# ────────────────────────────────
# 🔧 Django Core & Utilities
# ────────────────────────────────
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.views import PasswordResetView
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import models
from django.db.models import (
    Q, Count, F, Value, CharField,
    ExpressionWrapper, DurationField, FloatField
)
from django.db.models.functions import Concat
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST, require_GET

# ────────────────────────────────
# 📦 Local Imports
# ────────────────────────────────
from .forms import (
    CargaDatosForm, CargaDatosFormAvalian, CargaDatosFormOSDIPP, CargaDatosFormPAMI,
    CustomLoginForm, CustomPasswordResetForm,
    FarmaciaRegisterForm, LiquidacionPAMIForm, LiquidacionJerarquicosForm,
    LiquidacionGalenoForm, LiquidacionOsfatlyfForm, LiquidacionAsociartForm,
    LiquidacionPrevencionARTForm, GuiaVideoForm, GuiaArchivoForm
)
from .models import (
    CargaDatos, Presentacion, User, Farmacia,
    Liquidacion, LiquidacionGaleno, LiquidacionPAMI, LiquidacionJerarquicos,
    LiquidacionOspil, LiquidacionOsfatlyf, LiquidacionPAMIOncologico,
    LiquidacionPAMIPanales, LiquidacionPAMIVacunas, LiquidacionAndinaART,
    LiquidacionAsociart, LiquidacionColoniaSuiza, LiquidacionExperta,
    LiquidacionGalenoART, LiquidacionPrevencionART, Publication, PublicationLike, PublicationComment,
    Reclamo, ReclamoComment, Notification, GuiaVideo, GuiaArchivo, LiquidacionLaSegundaART,
    LiquidacionOSDIPP
)
from .utils import (
    obtener_datos_panel,
    procesar_liquidacion_pami, procesar_liquidacion_jerarquicos,
    procesar_liquidacion_galeno, procesar_liquidacion_ospil,
    procesar_liquidacion_osfatlyf, procesar_liquidacion_pami_oncologico,
    procesar_liquidacion_pami_panales, procesar_liquidacion_pami_vacunas,
    procesar_liquidacion_andina_art, procesar_liquidacion_asociart,
    procesar_liquidacion_coloniasuiza, procesar_liquidacion_experta,
    procesar_liquidacion_galenoart, procesar_liquidacion_prevencion_art,
    #obtener_transferencias_pami_por_sociedad
    obtener_transferencias_por_sociedad,
    generar_thumbnail_para_guia_video,
    regenerar_thumbnails_pendientes,
    get_video_info,
    procesar_liquidacion_lasegundaart,
    procesar_liquidacion_osdipp_pdf
)

#----
def camara_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name='Camara').exists():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("No tienes permiso para acceder a esta sección.")
    return _wrapped_view

def register_farmacia(request):
    if request.method == 'POST':
        form = FarmaciaRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            farmacia = Farmacia.objects.create(
                nombre=form.cleaned_data['nombre'],
                direccion=form.cleaned_data['direccion'],
                ciudad=form.cleaned_data['ciudad'],
                provincia=form.cleaned_data['provincia'],
                contacto_principal=form.cleaned_data['contacto_principal'],
                email_contacto=form.cleaned_data['email_contacto'],
                telefono_contacto=form.cleaned_data['telefono_contacto'],
                cuit=form.cleaned_data['cuit'],
                drogueria=form.cleaned_data['drogueria'],
            )
            user.farmacia = farmacia
            user.save()
            return redirect('login')
    else:
        form = FarmaciaRegisterForm()
    return render(request, 'register_farmacia.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('gestionar_presentaciones')  # Cambiar 'x' por la ruta deseada
        else:
            return render(request, 'login.html', {'form': form, 'error': 'Credenciales incorrectas'})
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('password_reset_done')


def render_header(request):
    return render(request, 'header_template.html')

def gestionar_presentaciones(request):
    obras_sociales = CargaDatos.OBRAS_SOCIALES
    return render(request, 'gestionar_presentaciones.html', {'obras_sociales': obras_sociales})

def cargar_datos(request, obra_social):
    form_classes = {
        'OSDIPP': CargaDatosFormOSDIPP,
        'SWISS_MEDICAL': CargaDatosFormOSDIPP,
        'GALENO': CargaDatosFormOSDIPP,
        'FARMALINK': CargaDatosFormOSDIPP,
        'PAMI': CargaDatosFormPAMI,
        'AVALIAN': CargaDatosFormAvalian,
    }

    form_class = form_classes.get(obra_social, CargaDatosFormOSDIPP)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.farmacia = request.user.farmacia
            instance.obra_social = obra_social  # ✅ Asignar manualmente el valor
            instance.save()
            return redirect('presentacion_exitosa', carga_datos_id=instance.id)
    else:
        form = form_class()

    return render(request, 'cargar_datos.html', {'form': form, 'obra_social': obra_social})

def presentacion_exitosa(request, carga_datos_id):
    carga_datos = get_object_or_404(CargaDatos, id=carga_datos_id)
    return render(request, 'presentacion_exitosa.html', {'carga_datos': carga_datos})


def observaciones(request):
    # Determinar el queryset según el grupo del usuario
    if request.user.is_superuser or request.user.groups.filter(name='Camara').exists():
        presentaciones = CargaDatos.objects.all()
    else:
        presentaciones = CargaDatos.objects.filter(farmacia=request.user.farmacia)

    # Agregar el usuario relacionado con la farmacia
    usuario_asociado = request.user  # El usuario que está viendo la tabla

    # Obtener el valor de búsqueda
    query = request.GET.get('q', '').strip()
    if query:
        presentaciones = presentaciones.filter(
            Q(numero_presentacion__icontains=query) |
            Q(periodo__icontains=query) |
            Q(obra_social__icontains=query)
        )

    return render(request, 'observaciones.html', {
        'presentaciones': presentaciones,
        'usuario_asociado': usuario_asociado  # Pasamos el usuario asociado
    })

@csrf_exempt
@login_required
def actualizar_estado_presentacion(request, id):
    if request.method == "POST":
        data = json.loads(request.body)
        nuevo_estado = data.get("estado")

        try:
            # Permitir que Camara o superuser edite cualquier presentación
            if request.user.is_superuser or request.user.groups.filter(name='Camara').exists():
                presentacion = CargaDatos.objects.get(id=id)
            else:
                presentacion = CargaDatos.objects.get(id=id, farmacia=request.user.farmacia)
            presentacion.estado = nuevo_estado
            presentacion.save()

            # Notificar a la farmacia (usuario) que subió la presentación
            usuario_farmacia = presentacion.farmacia.user
            if usuario_farmacia:
                from .models import Notification
                Notification.objects.create(
                    usuario=usuario_farmacia,
                    mensaje=f"La presentación {presentacion.numero_presentacion} ha cambiado a estado {nuevo_estado}",
                    link="/observaciones/",
                    tipo="foro"
                )
            return JsonResponse({"status": "ok"})
        except CargaDatos.DoesNotExist:
            return JsonResponse({"error": "Presentación no encontrada"}, status=404)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def lista_usuarios(request):
    """Carga la plantilla de usuarios para mostrar todos los usuarios registrados o hacer búsquedas."""
    usuarios = Farmacia.objects.all()
    return render(request, 'usuarios.html', {'usuarios': usuarios})

@login_required
def buscar_usuarios(request):
    """Busca usuarios por varios campos o retorna los más recientes si no hay búsqueda."""
    query = request.GET.get('q', '').strip()
    if query:
        usuarios = User.objects.annotate(
            full_name=Concat('first_name', Value(' '), 'last_name', output_field=CharField())
        ).filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(full_name__icontains=query)
        ).distinct()
    else:
        usuarios = User.objects.all().order_by('-date_joined')[:10]

    results = [
        {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'sector': user.groups.first().name if user.groups.exists() else "Sin asignar",
        }
        for user in usuarios
    ]
    return JsonResponse({'results': results})


@login_required
def actualizar_usuario(request):

    return render(request, 'actualizar_usuario.html')

@login_required
def calendario(request):
    # Obtener presentaciones del mes actual
    today = now()
    presentaciones = Presentacion.objects.filter(
        fecha__year=today.year, fecha__month=today.month
    ).order_by('fecha')

    # --- NOTIFICAR SI FALTAN 3 DÍAS PARA ALGUNA PRESENTACIÓN ---
    User = get_user_model()
    for p in presentaciones:
        dias_restantes = (p.fecha - timezone.now().date()).days
        if dias_restantes == 3:
            mensaje = f"¡Recordatorio! Faltan 3 días para la presentación de {p.obra_social}"
            for usuario in User.objects.all():
                if not Notification.objects.filter(usuario=usuario, mensaje=mensaje, tipo="foro").exists():
                    Notification.objects.create(
                        usuario=usuario,
                        mensaje=mensaje,
                        link=f"/calendario/",
                        tipo="foro"
                    )
    # --- FIN NOTIFICACION ---

    return render(request, 'calendario.html', {"presentaciones": presentaciones})

#--Obtener presentaciónes para sincronizar el calendario con el listado
def get_presentaciones_listado(request):
    year = int(request.GET.get('year'))
    month = int(request.GET.get('month'))
    
    presentaciones = Presentacion.objects.filter(
        fecha__year=year,
        fecha__month=month
    ).order_by('fecha')
    
    # Prepara los datos con el display name de quincena
    data = []
    for p in presentaciones:
        data.append({
            'fecha': p.fecha.strftime('%d/%m/%Y'),
            'obra_social': p.obra_social,
            'quincena': p.get_quincena_display()  # ¡Esto es clave!
        })
    
    return JsonResponse(data, safe=False)

@login_required
def calendar_farmacias(request):
    # Obtener el mes y año de los parámetros GET o usar el actual
    year = int(request.GET.get('year', now().year))
    month = int(request.GET.get('month', now().month))
    
    presentaciones = Presentacion.objects.filter(
        fecha__year=year, 
        fecha__month=month
    ).order_by('fecha')
    
    num_dias = calendar.monthrange(year, month)[1]
    dias_del_mes = [f"{year}-{month:02d}-{dia:02d}" for dia in range(1, num_dias + 1)]

    return render(request, 'calendar_farmacias.html', {
        "dias_del_mes": dias_del_mes,
        "mes_actual": f"{year}-{month:02d}",
        "presentaciones": presentaciones,
    })

@login_required
def get_presentaciones(request):
    year = request.GET.get("year")
    month = request.GET.get("month")

    if not year or not month:
        return JsonResponse([], safe=False)

    try:
        year = int(year)
        month = int(month)
    except ValueError:
        return JsonResponse([], safe=False)

    # Buscar todas las presentaciones del mes y año seleccionados, sin filtrar por farmacia
    presentaciones = Presentacion.objects.filter(
        fecha__year=year,
        fecha__month=month
    ).order_by('fecha')

    data = [
        {
            'fecha': p.fecha.strftime('%Y-%m-%d'),
            'obra_social': p.obra_social
        }
        for p in presentaciones
    ]
    return JsonResponse(data, safe=False)

@login_required
def guardar_presentacion(request):
    if request.method == "POST":
        fecha_raw = request.POST.get("selected_date")
        obra_social = request.POST.get("obra_social")
        quincena = request.POST.get("quincena")

        # ✅ Verificar si todos los datos están presentes
        if not fecha_raw or not obra_social or not quincena:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("calendario")

        # ✅ Convertimos la fecha al formato correcto (YYYY-MM-DD)
        try:
            fecha = datetime.strptime(fecha_raw, "%d/%m/%Y").date()
        except ValueError:
            messages.error(request, "Formato de fecha incorrecto.")
            return redirect("calendario")

        # ✅ Guardar en la base de datos
        presentacion = Presentacion.objects.create(
            usuario=request.user,
            fecha=fecha,
            obra_social=obra_social,
            quincena=quincena
        )

        # --- NOTIFICAR A TODOS LOS USUARIOS ---
        User = get_user_model()
        dias_restantes = (fecha - datetime.now().date()).days
        if dias_restantes > 1:
            tiempo = f"en {dias_restantes} días"
        elif dias_restantes == 1:
            tiempo = "mañana"
        elif dias_restantes == 0:
            tiempo = "hoy"
        else:
            tiempo = f"hace {abs(dias_restantes)} días"
        mensaje = f"Fecha de presentacion para {obra_social}: {tiempo}"
        for usuario in User.objects.all():
            Notification.objects.create(
                usuario=usuario,
                mensaje=mensaje,
                link=f"/calendar/",
                tipo="foro"
            )
        # --- FIN NOTIFICACION ---

        messages.success(request, "Presentación guardada exitosamente.")
        return redirect("calendario")

    return redirect("calendario")

@csrf_exempt
@login_required
def eliminar_presentacion(request, presentacion_id):
    if request.method == 'DELETE':
        try:
            presentacion = CargaDatos.objects.get(id=presentacion_id, farmacia=request.user.farmacia)
            presentacion.delete()
            return JsonResponse({'message': 'Presentación eliminada correctamente'}, status=200)
        except CargaDatos.DoesNotExist:
            return JsonResponse({'error': 'Presentación no encontrada'}, status=404)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def resumen_cobro(request):
    presentaciones = CargaDatos.objects.filter(farmacia=request.user.farmacia)
    chart_data = []

    for p in presentaciones:
        # Usar periodo_desde y periodo_hasta en vez de 'periodo'
        periodo_str = f"{p.periodo_desde.strftime('%Y-%m-%d')} a {p.periodo_hasta.strftime('%Y-%m-%d')}"
        year = p.periodo_desde.year if p.periodo_desde else None
        month = p.periodo_desde.month if p.periodo_desde else None

        liquidacion = None
        importe_liquidado = 0

        if year and month:
            liquidacion = LiquidacionGaleno.objects.filter(
                prestador=p.obra_social, 
                fecha__year=year, 
                fecha__month=month
            ).first()

            if liquidacion:
                importe_liquidado = float(liquidacion.importe_liquidado or 0)

        chart_data.append({
            "importe_100": float(p.total_pvp_pami if p.obra_social.upper() == "PAMI" else (p.importe_100 or 0)),
            "importe_liquidado": importe_liquidado,
            "periodo": periodo_str  # Para debugging
        })

    return render(request, 'resumen_cobro.html', {
        "presentaciones": presentaciones,
        "chart_data": json.dumps(chart_data)
    })


def home_liquidacion(request):
    obras_sociales = CargaDatos.OBRAS_SOCIALES
    return render(request, 'cargar_liquidaciones.html', {'obras_sociales': obras_sociales})

@login_required
def cargar_liquidacion_galeno(request):
    if request.method == "POST":
        form = LiquidacionGalenoForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_xlsx = request.FILES["archivo"]
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')  
            registros_creados = procesar_liquidacion_galeno(archivo_xlsx, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_galeno")
    else:
        form = LiquidacionGalenoForm()

    liquidaciones = LiquidacionGaleno.objects.all().order_by("-fecha")

    archivos_disponibles = list(
        LiquidacionGaleno.objects.values_list('archivo_origen', flat=True).distinct()
    )

    return render(request, "liquidacion.html", {
        "form": form,
        "liquidaciones": liquidaciones,
        "archivos_disponibles": archivos_disponibles
    })

@csrf_exempt
@login_required
def eliminar_liquidacion_galeno(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")

        if archivo_origen:
            LiquidacionGaleno.objects.filter(archivo_origen=archivo_origen).delete()
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)

def cargar_liquidacion_pami(request):
    if request.method == "POST":
        form = LiquidacionPAMIForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_xlsx = request.FILES["archivo"]
            archivo_origen = "LQ: " + date.today().strftime("%d-%m-%Y")
            registros_creados = procesar_liquidacion_pami(archivo_xlsx, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_pami")
    else:
        form = LiquidacionPAMIForm()

    # Obtener todas las liquidaciones de PAMI ordenadas por fecha descendente
    liquidaciones = LiquidacionPAMI.objects.all().order_by("-fecha_liquidacion")

    archivos_disponibles = list(
        LiquidacionPAMI.objects.values_list('archivo_origen', flat=True).distinct()
    )

    return render(request, "liquidacion_pami.html", {"form": form, "liquidaciones": liquidaciones, "archivos_disponibles": archivos_disponibles})

@csrf_exempt
@login_required
def editar_titulo_liquidacion(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")
        nuevo_titulo = data.get("nuevo_titulo")

        if archivo_origen and nuevo_titulo:
            LiquidacionPAMI.objects.filter(archivo_origen=archivo_origen).update(archivo_origen=nuevo_titulo)
            LiquidacionPAMIOncologico.objects.filter(archivo_origen=archivo_origen).update(archivo_origen=nuevo_titulo)
            LiquidacionPAMIPanales.objects.filter(archivo_origen=archivo_origen).update(archivo_origen=nuevo_titulo)
            LiquidacionPAMIVacunas.objects.filter(archivo_origen=archivo_origen).update(archivo_origen=nuevo_titulo)
            LiquidacionJerarquicos.objects.filter(archivo_origen=archivo_origen).update(archivo_origen=nuevo_titulo)
            LiquidacionGaleno.objects.filter(archivo_origen=archivo_origen).update(archivo_origen=nuevo_titulo)
            LiquidacionOspil.objects.filter(archivo_origen=archivo_origen).update(archivo_origen=nuevo_titulo)
            LiquidacionOsfatlyf.objects.filter(archivo_origen=archivo_origen).update(archivo_origen=nuevo_titulo)
            LiquidacionAndinaART.objects.filter(archivo_origen=archivo_origen).update(archivo_origen=nuevo_titulo)  
            LiquidacionAsociart.objects.filter(archivo_origen=archivo_origen).update(archivo_origen=nuevo_titulo)
            LiquidacionColoniaSuiza.objects.filter(archivo_origen=archivo_origen).update(archivo_origen=nuevo_titulo)
            LiquidacionExperta.objects.filter(archivo_origen=archivo_origen).update(archivo_origen=nuevo_titulo)
            LiquidacionGalenoART.objects.filter(archivo_origen=archivo_origen).update(archivo_origen=nuevo_titulo)
            LiquidacionPrevencionART.objects.filter(archivo_origen=archivo_origen).update(archivo_origen=nuevo_titulo)
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)

@csrf_exempt
@login_required
def eliminar_liquidacion_pami(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")

        if archivo_origen:
            LiquidacionPAMI.objects.filter(archivo_origen=archivo_origen).delete()
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)

@login_required
def cargar_liquidacion_jerarquicos(request):
    if request.method == "POST":
        form = LiquidacionJerarquicosForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_xlsx = request.FILES["archivo"]
            archivo_origen = "LQ: " + date.today().strftime("%d-%m-%Y")
            registros_creados = procesar_liquidacion_jerarquicos(archivo_xlsx, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_jerarquicos")
    else:
        form = LiquidacionJerarquicosForm()

    liquidaciones = LiquidacionJerarquicos.objects.all().order_by("-fecha_liquidacion")

    archivos_disponibles = list(
        LiquidacionJerarquicos.objects.values_list('archivo_origen', flat=True).distinct()
    )

    return render(request, "liquidacion_jerarquicos.html", {
        "form": form,
        "liquidaciones": liquidaciones,
        "archivos_disponibles": archivos_disponibles
    })

@csrf_exempt
@login_required
def eliminar_liquidacion_jerarquicos(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")

        if archivo_origen:
            LiquidacionJerarquicos.objects.filter(archivo_origen=archivo_origen).delete()
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)

@login_required
def cargar_liquidacion_ospil(request):
    if request.method == "POST":
        form = LiquidacionPAMIForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_xlsx = request.FILES["archivo"]
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')
            registros_creados = procesar_liquidacion_ospil(archivo_xlsx, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_ospil")
    else:
        form = LiquidacionPAMIForm()

    liquidaciones = LiquidacionOspil.objects.all().order_by("-fecha_liquidacion")

    archivos_disponibles = list(
        LiquidacionOspil.objects.values_list('archivo_origen', flat=True).distinct()
    )

    return render(request, "liquidacion_ospil.html", {
        "form": form,
        "liquidaciones": liquidaciones,
        "archivos_disponibles": archivos_disponibles
    })

@csrf_exempt
@login_required
def eliminar_liquidacion_ospil(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")

        if archivo_origen:
            LiquidacionOspil.objects.filter(archivo_origen=archivo_origen).delete()
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)

@login_required
def cargar_liquidacion_osfatlyf(request):
    if request.method == "POST":
        form = LiquidacionOsfatlyfForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_xlsx = request.FILES["archivo"]
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')
            registros_creados = procesar_liquidacion_osfatlyf(archivo_xlsx, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_osfatlyf")
    else:
        form = LiquidacionOsfatlyfForm()

    liquidaciones = LiquidacionOsfatlyf.objects.all().order_by("-fecha_liquidacion")

    archivos_disponibles = list(
        LiquidacionOsfatlyf.objects.values_list('archivo_origen', flat=True).distinct()
    )

    return render(request, "liquidacion_osfatlyf.html", {
        "form": form,
        "liquidaciones": liquidaciones,
        "archivos_disponibles": archivos_disponibles
    })


@csrf_exempt
@login_required
def eliminar_liquidacion_osfatlyf(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")

        if archivo_origen:
            LiquidacionOsfatlyf.objects.filter(archivo_origen=archivo_origen).delete()
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)

@login_required
def cargar_liquidacion_pami_oncologico(request):
    if request.method == "POST":
        form = LiquidacionPAMIForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_xlsx = request.FILES["archivo"]
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')
            registros_creados = procesar_liquidacion_pami_oncologico(archivo_xlsx, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_pami_oncologico")
    else:
        form = LiquidacionPAMIForm()

    liquidaciones = LiquidacionPAMIOncologico.objects.all().order_by("-fecha_liquidacion")
    archivos_disponibles = list(
        LiquidacionPAMIOncologico.objects.values_list('archivo_origen', flat=True).distinct()
    )

    return render(request, "liquidacion_pamioncologico.html", {
        "form": form,
        "liquidaciones": liquidaciones,
        "archivos_disponibles": archivos_disponibles
    })


@csrf_exempt
@login_required
def eliminar_liquidacion_pami_oncologico(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")
        if archivo_origen:
            LiquidacionPAMIOncologico.objects.filter(archivo_origen=archivo_origen).delete()
            return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)

@login_required
def cargar_liquidacion_pami_panales(request):
    if request.method == "POST":
        form = LiquidacionPAMIForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_xlsx = request.FILES["archivo"]
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')
            registros_creados = procesar_liquidacion_pami_panales(archivo_xlsx, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_pami_panales")
    else:
        form = LiquidacionPAMIForm()

    liquidaciones = LiquidacionPAMIPanales.objects.all().order_by("-fecha_liquidacion")
    archivos_disponibles = list(
        LiquidacionPAMIPanales.objects.values_list('archivo_origen', flat=True).distinct()
    )

    return render(request, "liquidacion_pami_panales.html", {
        "form": form,
        "liquidaciones": liquidaciones,
        "archivos_disponibles": archivos_disponibles
    })


@csrf_exempt
@login_required
def eliminar_liquidacion_pami_panales(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")

        if archivo_origen:
            LiquidacionPAMIPanales.objects.filter(archivo_origen=archivo_origen).delete()
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)

@login_required
def cargar_liquidacion_pami_vacunas(request):
    if request.method == "POST":
        form = LiquidacionPAMIForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_xlsx = request.FILES["archivo"]
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')
            registros_creados = procesar_liquidacion_pami_vacunas(archivo_xlsx, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_pami_vacunas")
    else:
        form = LiquidacionPAMIForm()

    liquidaciones = LiquidacionPAMIVacunas.objects.all().order_by("-fecha_liquidacion")
    archivos_disponibles = list(
        LiquidacionPAMIVacunas.objects.values_list('archivo_origen', flat=True).distinct()
    )

    return render(request, "liquidacion_pami_vacunas.html", {
        "form": form,
        "liquidaciones": liquidaciones,
        "archivos_disponibles": archivos_disponibles
    })


@csrf_exempt
@login_required
def eliminar_liquidacion_pami_vacunas(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")

        if archivo_origen:
            LiquidacionPAMIVacunas.objects.filter(archivo_origen=archivo_origen).delete()
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)

@login_required
def cargar_liquidacion_pami_nutricional(request):

    return render(request, "liquidacion_pami_nutricional.html")

@login_required
def cargar_liquidacion_andina_art(request):
    if request.method == "POST":
        form = LiquidacionPAMIForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_xlsx = request.FILES["archivo"]
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')
            registros_creados = procesar_liquidacion_andina_art(archivo_xlsx, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_andina_art")
    else:
        form = LiquidacionPAMIForm()

    liquidaciones = LiquidacionAndinaART.objects.all().order_by("-fecha_liquidacion")
    archivos_disponibles = list(
        LiquidacionAndinaART.objects.values_list('archivo_origen', flat=True).distinct()
    )

    return render(request, "liquidacion_andina_art.html", {
        "form": form,
        "liquidaciones": liquidaciones,
        "archivos_disponibles": archivos_disponibles
    })


@csrf_exempt
@login_required
def eliminar_liquidacion_andina_art(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")

        if archivo_origen:
            LiquidacionAndinaART.objects.filter(archivo_origen=archivo_origen).delete()
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)

@login_required
def cargar_liquidacion_asociart(request):
    if request.method == "POST":
        form = LiquidacionAsociartForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_xlsx = request.FILES["archivo"]
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')
            registros_creados = procesar_liquidacion_asociart(archivo_xlsx, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_asociart")
    else:
        form = LiquidacionAsociartForm()

    liquidaciones = LiquidacionAsociart.objects.all().order_by("-fecha_liquidacion")

    archivos_disponibles = list(
        LiquidacionAsociart.objects.values_list('archivo_origen', flat=True).distinct()
    )

    return render(request, "liquidacion_asociart.html", {
        "form": form,
        "liquidaciones": liquidaciones,
        "archivos_disponibles": archivos_disponibles
    })


@csrf_exempt
@login_required
def eliminar_liquidacion_asociart(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")

        if archivo_origen:
            LiquidacionAsociart.objects.filter(archivo_origen=archivo_origen).delete()
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)

@login_required
def cargar_liquidacion_coloniasuiza(request):
    if request.method == "POST":
        form = LiquidacionPAMIForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_xlsx = request.FILES["archivo"]
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')
            registros_creados = procesar_liquidacion_coloniasuiza(archivo_xlsx, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_coloniasuiza")
    else:
        form = LiquidacionPAMIForm()

    liquidaciones = LiquidacionColoniaSuiza.objects.all().order_by("-fecha_liquidacion")
    archivos_disponibles = list(
        LiquidacionColoniaSuiza.objects.values_list('archivo_origen', flat=True).distinct()
    )
    return render(request, "liquidacion_coloniasuiza.html", {"form": form, "liquidaciones": liquidaciones, "archivos_disponibles": archivos_disponibles})


@csrf_exempt
@login_required
def eliminar_liquidacion_coloniasuiza(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")
        if archivo_origen:
            LiquidacionColoniaSuiza.objects.filter(archivo_origen=archivo_origen).delete()
            return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)

@login_required
def cargar_liquidacion_experta(request):
    if request.method == "POST":
        form = LiquidacionPAMIForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_xlsx = request.FILES["archivo"]
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')  
            registros_creados = procesar_liquidacion_experta(archivo_xlsx, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_experta")
    else:
        form = LiquidacionPAMIForm()

    liquidaciones = LiquidacionExperta.objects.all().order_by("-fecha_liquidacion")

    archivos_disponibles = list(
        LiquidacionExperta.objects.values_list('archivo_origen', flat=True).distinct()
    )

    return render(request, "liquidacion_experta.html", {"form": form, "liquidaciones": liquidaciones, "archivos_disponibles": archivos_disponibles})


@csrf_exempt
@login_required
def eliminar_liquidacion_experta(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")
        if archivo_origen:
            LiquidacionExperta.objects.filter(archivo_origen=archivo_origen).delete()
            return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)

@login_required
def cargar_liquidacion_galenoart(request):
    if request.method == "POST":
        form = LiquidacionPAMIForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_xlsx = request.FILES["archivo"]
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')
            registros_creados = procesar_liquidacion_galenoart(archivo_xlsx, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_galenoart")
    else:
        form = LiquidacionPAMIForm()

    liquidaciones = LiquidacionGalenoART.objects.all().order_by("-fecha_liquidacion")
    archivos_disponibles = list(
        LiquidacionGalenoART.objects.values_list('archivo_origen', flat=True).distinct()
    )

    return render(request, "liquidacion_galenoart.html", {
        "form": form,
        "liquidaciones": liquidaciones,
        "archivos_disponibles": archivos_disponibles
    })


@csrf_exempt
@login_required
def eliminar_liquidacion_galenoart(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")

        if archivo_origen:
            LiquidacionGalenoART.objects.filter(archivo_origen=archivo_origen).delete()
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)

@login_required
def cargar_liquidacion_prevencion_art(request):
    if request.method == "POST":
        form = LiquidacionPrevencionARTForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_xlsx = request.FILES["archivo"]
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')
            registros_creados = procesar_liquidacion_prevencion_art(archivo_xlsx, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_prevencion_art")
    else:
        form = LiquidacionPrevencionARTForm()

    liquidaciones = LiquidacionPrevencionART.objects.all().order_by("-fecha_liquidacion")
    archivos_disponibles = list(
        LiquidacionPrevencionART.objects.values_list('archivo_origen', flat=True).distinct()
    )

    return render(request, "liquidacion_prevencion_art.html", {"form": form, "liquidaciones": liquidaciones, "archivos_disponibles": archivos_disponibles})


@csrf_exempt
@login_required
def eliminar_liquidacion_prevencion_art(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")

        if archivo_origen:
            LiquidacionPrevencionART.objects.filter(archivo_origen=archivo_origen).delete()
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)


@login_required
def transferencias_tesorera(request):
    resumen_por_obra, sin_relacion = obtener_transferencias_por_sociedad()

    return render(request, "transferencias.html", {
        "resumen_por_obra": resumen_por_obra,
        "sin_relacion": sin_relacion
    })



def panel_liquidaciones(request):
    """
    Vista que muestra el panel de análisis de liquidaciones.
    """
    

    return render(request, "panel_liquidaciones.html")



def foro(request):
    """
    Vista que muestra el foro con publicaciones reales de la base de datos.
    """
    # Obtener todas las publicaciones ordenadas por fecha de creación (más recientes primero)
    publicaciones = Publication.objects.select_related(
        'usuario_creacion', 
        'usuario_modificacion'
    ).prefetch_related(
        'likes__usuario',
        'comentarios__usuario'
    ).all()
    
    # Verificar si el usuario actual ha dado like a cada publicación
    if request.user.is_authenticated:
        for publicacion in publicaciones:
            publicacion.user_has_liked = publicacion.likes.filter(usuario=request.user).exists()
    
    return render(request, "foro.html", {
        'publicaciones': publicaciones
    })


@login_required
@require_POST
def crear_publicacion(request):
    """
    Vista para crear una nueva publicación en el foro.
    """
    try:
        descripcion = request.POST.get('descripcion', '').strip()
        categoria = request.POST.get('categoria', '').strip()
        
        if not descripcion:
            return JsonResponse({
                'success': False,
                'error': 'La descripción es obligatoria'
            }, status=400)
        
        if not categoria:
            return JsonResponse({
                'success': False,
                'error': 'La categoría es obligatoria'
            }, status=400)
        
        # Crear la publicación
        publicacion = Publication.objects.create(
            descripcion=descripcion,
            categoria=categoria,
            usuario_creacion=request.user,
            usuario_modificacion=request.user
        )
        
        # Manejar archivos adjuntos
        if 'imagen' in request.FILES:
            publicacion.imagen = request.FILES['imagen']
        
        if 'archivo' in request.FILES:
            publicacion.archivo = request.FILES['archivo']
        
        publicacion.save()
        
        # --- NOTIFICAR A TODOS LOS USUARIOS (excepto el creador) ---
        User = get_user_model()
        categoria_display = dict(Publication.CATEGORIAS).get(categoria, categoria)
        mensaje = f"{request.user.get_full_name() or request.user.username} publicó un/a {categoria_display}"
        for usuario in User.objects.exclude(id=request.user.id):
            Notification.objects.create(
                usuario=usuario,
                mensaje=mensaje,
                link=f"/foro/",
                tipo="foro"
            )
        # --- FIN NOTIFICACION ---
        
        return JsonResponse({
            'success': True,
            'message': 'Publicación creada exitosamente',
            'publicacion_id': publicacion.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al crear la publicación: {str(e)}'
        }, status=500)


@login_required
@require_POST
def toggle_like(request, publicacion_id):
    """
    Vista para dar/quitar like a una publicación.
    """
    try:
        publicacion = get_object_or_404(Publication, id=publicacion_id)
        
        # Verificar si el usuario ya dio like
        like_existente = PublicationLike.objects.filter(
            publicacion=publicacion,
            usuario=request.user
        ).first()
        
        if like_existente:
            # Quitar like
            like_existente.delete()
            liked = False
        else:
            # Dar like
            PublicationLike.objects.create(
                publicacion=publicacion,
                usuario=request.user
            )
            liked = True
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': publicacion.likes_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al procesar el like: {str(e)}'
        }, status=500)


@login_required
@require_POST
def crear_comentario(request, publicacion_id):
    """
    Vista para crear un comentario en una publicación.
    """
    try:
        publicacion = get_object_or_404(Publication, id=publicacion_id)
        contenido = request.POST.get('contenido', '').strip()
        
        if not contenido:
            return JsonResponse({
                'success': False,
                'error': 'El contenido del comentario es obligatorio'
            }, status=400)
        
        # Crear el comentario
        comentario = PublicationComment.objects.create(
            publicacion=publicacion,
            usuario=request.user,
            contenido=contenido
        )
        
        # --- NOTIFICAR AL CREADOR DE LA PUBLICACION ---
        if publicacion.usuario_creacion != request.user:
            Notification.objects.create(
                usuario=publicacion.usuario_creacion,
                mensaje=f"{request.user.get_full_name() or request.user.username} ha comentado tu publicación '{publicacion.descripcion[:40]}{'...' if len(publicacion.descripcion) > 40 else ''}'",
                link=f"/foro/",
                tipo="foro"
            )
        # --- FIN NOTIFICACION ---
        
        return JsonResponse({
            'success': True,
            'message': 'Comentario creado exitosamente',
            'comentario_id': comentario.id,
            'comentarios_count': publicacion.comentarios_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al crear el comentario: {str(e)}'
        }, status=500)


@login_required
@require_POST
def eliminar_publicacion(request, publicacion_id):
    """
    Vista para eliminar una publicación (solo el autor puede eliminarla).
    """
    try:
        publicacion = get_object_or_404(Publication, id=publicacion_id)
        
        # Verificar que el usuario sea el autor de la publicación
        if publicacion.usuario_creacion != request.user:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para eliminar esta publicación'
            }, status=403)
        
        publicacion.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Publicación eliminada exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al eliminar la publicación: {str(e)}'
        }, status=500)

@login_required
@require_POST
def eliminar_comentario(request, comentario_id):
    """
    Elimina (borrado lógico) un comentario si el usuario es el autor o el autor de la publicación.
    """
    from .models import PublicationComment
    comentario = get_object_or_404(PublicationComment, id=comentario_id)
    if comentario.usuario != request.user and comentario.publicacion.usuario_creacion != request.user:
        return JsonResponse({'success': False, 'error': 'No tienes permisos para eliminar este comentario'}, status=403)
    comentario.delete()
    return JsonResponse({'success': True, 'message': 'Comentario eliminado'})

@login_required
@require_POST
def responder_comentario(request, comentario_id):
    """
    Crea una respuesta a un comentario (comentario hijo).
    """
    from .models import PublicationComment
    comentario_padre = get_object_or_404(PublicationComment, id=comentario_id)
    contenido = request.POST.get('contenido', '').strip()
    if not contenido:
        return JsonResponse({'success': False, 'error': 'El contenido de la respuesta es obligatorio'}, status=400)
    comentario = PublicationComment.objects.create(
        publicacion=comentario_padre.publicacion,
        usuario=request.user,
        contenido=contenido,
        parent=comentario_padre
    )
    # Notificar al autor del comentario padre si no es el mismo usuario
    if comentario_padre.usuario != request.user:
        Notification.objects.create(
            usuario=comentario_padre.usuario,
            mensaje=f"{request.user.get_full_name() or request.user.username} respondió a tu comentario en la publicación '{comentario_padre.publicacion.descripcion[:40]}{'...' if len(comentario_padre.publicacion.descripcion) > 40 else ''}'",
            link=f"/foro/",
            tipo="foro"
        )
    return JsonResponse({'success': True, 'message': 'Respuesta publicada', 'comentario_id': comentario.id})

@require_GET
@login_required
def obtener_comentarios(request, publicacion_id):
    """
    Devuelve los comentarios de una publicación en formato JSON, anidados y con soporte de borrado lógico.
    """
    from .models import PublicationComment
    def serialize_comment(c):
        return {
            'id': c.id,
            'usuario': c.usuario.get_full_name() or c.usuario.username,
            'contenido': '[Comentario eliminado]' if c.is_deleted else c.contenido,
            'fecha': c.fecha_comentario.strftime('%d/%m/%Y %H:%M'),
            'is_deleted': c.is_deleted,
            'puede_eliminar': (c.usuario == request.user or c.publicacion.usuario_creacion == request.user),
            'replies': [serialize_comment(r) for r in c.replies.filter(is_deleted=False).order_by('fecha_comentario')]
        }
    comentarios = PublicationComment.objects.filter(publicacion_id=publicacion_id, parent__isnull=True).select_related('usuario').order_by('fecha_comentario')
    data = [serialize_comment(c) for c in comentarios]
    return JsonResponse({'comentarios': data})

@login_required
@require_POST
def crear_reclamo(request):
    """
    Crea un nuevo reclamo (AJAX).
    """
    titulo = request.POST.get('titulo', '').strip()
    descripcion = request.POST.get('descripcion', '').strip()
    imagen = request.FILES.get('imagen')
    archivo = request.FILES.get('archivo')
    if not titulo or not descripcion:
        return JsonResponse({'success': False, 'error': 'Título y descripción son obligatorios.'}, status=400)
    reclamo = Reclamo.objects.create(
        titulo=titulo,
        descripcion=descripcion,
        usuario_creador=request.user,
        ultima_actualizacion_por=request.user,
        imagen=imagen,
        archivo=archivo
    )
    # Si quieres notificar a alguien, aquí puedes usar:
    # Notification.objects.create(usuario=..., mensaje=..., link=f"/foro/#reclamo-{reclamo.id}", tipo="reclamo_estado")
    return JsonResponse({'success': True, 'message': 'Reclamo creado', 'reclamo_id': reclamo.id})

@login_required
@require_GET
def listar_reclamos(request):
    """
    Devuelve los reclamos para el aside (solo no eliminados, ordenados por fecha).
    """
    from django.utils import timezone
    from datetime import datetime
    
    reclamos = Reclamo.objects.filter(is_deleted=False, estado__in=['pendiente', 'en_progreso']).order_by('-fecha_creacion')[:10]
    data = []
    
    for r in reclamos:
        # Calcular tiempo transcurrido
        ahora = timezone.now()
        diferencia = ahora - r.fecha_creacion
        
        if diferencia.days > 0:
            tiempo_transcurrido = f"hace {diferencia.days} día{'s' if diferencia.days != 1 else ''}"
        elif diferencia.seconds >= 3600:
            horas = diferencia.seconds // 3600
            tiempo_transcurrido = f"hace {horas} hora{'s' if horas != 1 else ''}"
        elif diferencia.seconds >= 60:
            minutos = diferencia.seconds // 60
            tiempo_transcurrido = f"hace {minutos} minuto{'s' if minutos != 1 else ''}"
        else:
            tiempo_transcurrido = "ahora mismo"
        
        # Obtener usuarios asignados
        usuarios_asignados = []
        if r.usuario_asignado:
            usuarios_asignados.append(r.usuario_asignado.get_full_name() or r.usuario_asignado.username)
        
        # También incluir usuarios del campo ManyToMany asignados
        for usuario in r.asignados.all():
            nombre_usuario = usuario.get_full_name() or usuario.username
            if nombre_usuario not in usuarios_asignados:
                usuarios_asignados.append(nombre_usuario)
        
        data.append({
            'id': r.id,
            'titulo': r.titulo,
            'descripcion': r.descripcion[:120] + ('...' if len(r.descripcion) > 120 else ''),
            'usuario_creador': r.usuario_creador.get_full_name() or r.usuario_creador.username,
            'fecha_creacion': r.fecha_creacion.strftime('%d/%m/%Y'),
            'tiempo_transcurrido': tiempo_transcurrido,
            'usuarios_asignados': usuarios_asignados,
            'ultima_actualizacion_por': r.ultima_actualizacion_por.get_full_name() if r.ultima_actualizacion_por else '',
            'estado': r.get_estado_display(),
            'notificaciones_activas': r.notificaciones_activas,
            'es_publico': r.es_publico,
        })
    
    return JsonResponse({'reclamos': data})

@login_required
@require_GET
def listar_reclamos_resueltos(request):
    """
    Devuelve los reclamos resueltos y cerrados para el aside (solo no eliminados, ordenados por fecha).
    """
    from django.utils import timezone
    from datetime import datetime
    
    # Obtener parámetro de búsqueda
    query = request.GET.get('q', '').strip()
    
    # Filtrar reclamos resueltos y cerrados
    reclamos = Reclamo.objects.filter(
        is_deleted=False, 
        estado__in=['resuelto', 'cerrado']
    ).order_by('-fecha_creacion')
    
    # Aplicar búsqueda si hay query
    if query:
        reclamos = reclamos.filter(titulo__icontains=query)
    
    # Limitar a 10 resultados
    reclamos = reclamos[:10]
    
    data = []
    
    for r in reclamos:
        # Calcular tiempo transcurrido
        ahora = timezone.now()
        diferencia = ahora - r.fecha_creacion
        
        if diferencia.days > 0:
            tiempo_transcurrido = f"hace {diferencia.days} día{'s' if diferencia.days != 1 else ''}"
        elif diferencia.seconds >= 3600:
            horas = diferencia.seconds // 3600
            tiempo_transcurrido = f"hace {horas} hora{'s' if horas != 1 else ''}"
        elif diferencia.seconds >= 60:
            minutos = diferencia.seconds // 60
            tiempo_transcurrido = f"hace {minutos} minuto{'s' if minutos != 1 else ''}"
        else:
            tiempo_transcurrido = "ahora mismo"
        
        # Obtener usuarios asignados
        usuarios_asignados = []
        if r.usuario_asignado:
            usuarios_asignados.append(r.usuario_asignado.get_full_name() or r.usuario_asignado.username)
        
        # También incluir usuarios del campo ManyToMany asignados
        for usuario in r.asignados.all():
            nombre_usuario = usuario.get_full_name() or usuario.username
            if nombre_usuario not in usuarios_asignados:
                usuarios_asignados.append(nombre_usuario)
        
        data.append({
            'id': r.id,
            'titulo': r.titulo,
            'descripcion': r.descripcion[:120] + ('...' if len(r.descripcion) > 120 else ''),
            'usuario_creador': r.usuario_creador.get_full_name() or r.usuario_creador.username,
            'fecha_creacion': r.fecha_creacion.strftime('%d/%m/%Y'),
            'tiempo_transcurrido': tiempo_transcurrido,
            'usuarios_asignados': usuarios_asignados,
            'ultima_actualizacion_por': r.ultima_actualizacion_por.get_full_name() if r.ultima_actualizacion_por else '',
            'estado': r.get_estado_display(),
            'notificaciones_activas': r.notificaciones_activas,
            'es_publico': r.es_publico,
        })
    
    return JsonResponse({'reclamos': data})

@login_required
@require_POST
def cambiar_estado_reclamo(request, reclamo_id):
    """
    Cambia el estado de un reclamo (resuelto, cerrado, etc.) y notifica a los usuarios involucrados.
    """
    nuevo_estado = request.POST.get('estado')
    reclamo = get_object_or_404(Reclamo, id=reclamo_id, is_deleted=False)
    if nuevo_estado not in dict(Reclamo.ESTADOS):
        return JsonResponse({'success': False, 'error': 'Estado inválido.'}, status=400)
    reclamo.estado = nuevo_estado
    if nuevo_estado == 'resuelto':
        from django.utils import timezone
        reclamo.fecha_resolucion = timezone.now()
    reclamo.ultima_actualizacion_por = request.user
    reclamo.save()

    # --- NOTIFICACIONES ---
    usuarios_a_notificar = set()
    if reclamo.usuario_creador:
        usuarios_a_notificar.add(reclamo.usuario_creador)
    for u in reclamo.asignados.all():
        usuarios_a_notificar.add(u)
    for usuario in usuarios_a_notificar:
        Notification.objects.create(
            usuario=usuario,
            mensaje=f"El reclamo '{reclamo.titulo}' cambió de estado a '{reclamo.get_estado_display()}'.",
            link=f"/foro/",
            tipo="reclamo_estado"
        )
    # --- FIN NOTIFICACIONES ---

    return JsonResponse({'success': True, 'message': 'Estado actualizado.'})

@login_required
@require_POST
def eliminar_reclamo(request, reclamo_id):
    """
    Borrado lógico de un reclamo (solo autor o admin).
    """
    reclamo = get_object_or_404(Reclamo, id=reclamo_id, is_deleted=False)
    if reclamo.usuario_creador != request.user and not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'No tienes permisos para eliminar este reclamo.'}, status=403)
    reclamo.is_deleted = True
    reclamo.save(update_fields=['is_deleted'])
    return JsonResponse({'success': True, 'message': 'Reclamo eliminado.'})

@login_required
@require_POST
def toggle_notificaciones_reclamo(request, reclamo_id):
    """
    Activa/desactiva notificaciones para un reclamo.
    """
    reclamo = get_object_or_404(Reclamo, id=reclamo_id, is_deleted=False)
    reclamo.notificaciones_activas = not reclamo.notificaciones_activas
    reclamo.ultima_actualizacion_por = request.user
    reclamo.save(update_fields=['notificaciones_activas', 'ultima_actualizacion_por'])
    return JsonResponse({'success': True, 'notificaciones_activas': reclamo.notificaciones_activas})

@login_required
@require_GET
def detalle_reclamo(request, reclamo_id):
    from .models import Reclamo
    reclamo = get_object_or_404(Reclamo, id=reclamo_id, is_deleted=False)
    asignados_ids = list(reclamo.asignados.values_list('id', flat=True)) if hasattr(reclamo, 'asignados') else []
    return JsonResponse({
        'success': True,
        'titulo': reclamo.titulo,
        'descripcion': reclamo.descripcion,
        'usuario_creador': reclamo.usuario_creador.get_full_name() or reclamo.usuario_creador.username,
        'fecha_creacion': reclamo.fecha_creacion.strftime('%d/%m/%Y'),
        'estado': reclamo.estado,
        'estado_display': reclamo.get_estado_display(),
        'imagen_url': reclamo.imagen.url if reclamo.imagen else None,
        'archivo_url': reclamo.archivo.url if reclamo.archivo else None,
        'asignados_ids': asignados_ids,
    })

@login_required
@require_GET
def comentarios_reclamo(request, reclamo_id):
    reclamo = get_object_or_404(Reclamo, id=reclamo_id, is_deleted=False)
    def serialize_comment(c):
        return {
            'id': c.id,
            'usuario': c.usuario.get_full_name() or c.usuario.username,
            'contenido': '[Comentario eliminado]' if c.is_deleted else c.contenido,
            'fecha': c.fecha_comentario.strftime('%d/%m/%Y %H:%M'),
            'is_deleted': c.is_deleted,
            'puede_eliminar': (c.usuario == request.user or reclamo.usuario_creador == request.user),
            'imagen_url': c.imagen.url if c.imagen else None,
            'archivo_url': c.archivo.url if c.archivo else None,
            'replies': [serialize_comment(r) for r in c.replies.filter(is_deleted=False).order_by('fecha_comentario')]
        }
    comentarios = ReclamoComment.objects.filter(reclamo=reclamo, parent__isnull=True).select_related('usuario').order_by('fecha_comentario')
    data = [serialize_comment(c) for c in comentarios]
    return JsonResponse({'comentarios': data})

@login_required
@require_POST
def comentar_reclamo(request, reclamo_id):
    reclamo = get_object_or_404(Reclamo, id=reclamo_id, is_deleted=False)
    contenido = request.POST.get('contenido', '').strip()
    imagen = request.FILES.get('imagen')
    archivo = request.FILES.get('archivo')
    if not contenido:
        return JsonResponse({'success': False, 'error': 'El contenido es obligatorio.'}, status=400)
    comentario = ReclamoComment.objects.create(
        reclamo=reclamo,
        usuario=request.user,
        contenido=contenido,
        imagen=imagen,
        archivo=archivo
    )
    # Notificar al creador del reclamo si no es el mismo usuario
    if reclamo.usuario_creador != request.user:
        Notification.objects.create(
            usuario=reclamo.usuario_creador,
            mensaje=f"{request.user.get_full_name() or request.user.username} ha comentado tu reclamo '{reclamo.titulo[:40]}{'...' if len(reclamo.titulo) > 40 else ''}'",
            link=f"/foro/",
            tipo="reclamo_comentario"
        )
    return JsonResponse({'success': True, 'message': 'Comentario publicado', 'comentario_id': comentario.id})

@login_required
@require_POST
def responder_comentario_reclamo(request, comentario_id):
    comentario_padre = get_object_or_404(ReclamoComment, id=comentario_id)
    contenido = request.POST.get('contenido', '').strip()
    if not contenido:
        return JsonResponse({'success': False, 'error': 'El contenido de la respuesta es obligatorio'}, status=400)
    comentario = ReclamoComment.objects.create(
        reclamo=comentario_padre.reclamo,
        usuario=request.user,
        contenido=contenido,
        parent=comentario_padre
    )
    # Notificar al autor del comentario padre si no es el mismo usuario
    if comentario_padre.usuario != request.user:
        Notification.objects.create(
            usuario=comentario_padre.usuario,
            mensaje=f"{request.user.get_full_name() or request.user.username} respondió a tu comentario en el reclamo '{comentario_padre.reclamo.titulo[:40]}{'...' if len(comentario_padre.reclamo.titulo) > 40 else ''}'",
            link=f"/foro/",
            tipo="reclamo_comentario"
        )
    return JsonResponse({'success': True, 'message': 'Respuesta publicada', 'comentario_id': comentario.id})

@login_required
@require_POST
def eliminar_comentario_reclamo(request, comentario_id):
    comentario = get_object_or_404(ReclamoComment, id=comentario_id)
    if comentario.usuario != request.user and comentario.reclamo.usuario_creador != request.user:
        return JsonResponse({'success': False, 'error': 'No tienes permisos para eliminar este comentario'}, status=403)
    comentario.is_deleted = True
    comentario.save(update_fields=['is_deleted'])
    return JsonResponse({'success': True, 'message': 'Comentario eliminado'})

@login_required
@require_POST
def asignar_reclamo(request, reclamo_id):
    import json
    from .models import Reclamo, User
    reclamo = get_object_or_404(Reclamo, id=reclamo_id, is_deleted=False)
    data = json.loads(request.body)
    asignados = data.get('asignados', [])
    users = User.objects.filter(id__in=asignados)
    reclamo.asignados.set(users)
    reclamo.save()
    # --- NOTIFICAR A LOS USUARIOS ASIGNADOS ---
    for usuario in users:
        Notification.objects.create(
            usuario=usuario,
            mensaje=f"{request.user.get_full_name() or request.user.username} te ha asignado al reclamo: {reclamo.titulo}",
            link=f"/foro/",
            tipo="reclamo_estado"
        )
    # --- FIN NOTIFICACION ---
    return JsonResponse({'success': True, 'message': 'Usuarios asignados'})

@login_required
@require_GET
def usuarios_asignables_reclamo(request):
    from .models import User
    usuarios = User.objects.all()
    data = [{'id': u.id, 'nombre': u.get_full_name() or u.username} for u in usuarios]
    return JsonResponse({'usuarios': data})

@login_required
@require_GET
def estados_reclamo(request):
    from .models import Reclamo
    estados = [{'value': e[0], 'display': e[1]} for e in Reclamo.ESTADOS]
    return JsonResponse({'estados': estados})

# --- ENDPOINTS DE NOTIFICACIONES ---
@login_required
def guias_uso(request):
    """Vista para la sección de Guías de uso donde los usuarios pueden subir y ver videos y archivos."""
    # Obtener videos y archivos públicos
    videos = GuiaVideo.objects.filter(estado='publico').order_by('-fecha_subida')
    archivos = GuiaArchivo.objects.filter(estado='publico').order_by('-fecha_subida')
    
    # Búsqueda
    query = request.GET.get('q', '')
    if query:
        videos = videos.filter(titulo__icontains=query)
        archivos = archivos.filter(titulo__icontains=query)
    
    context = {
        'videos': videos,
        'archivos': archivos,
        'query': query,
        'usuario_actual': request.user
    }
    return render(request, 'guias_uso.html', context)


@login_required
def subir_video(request):
    """Vista para subir un nuevo video de guía."""
    if request.method == 'POST':
        form = GuiaVideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.usuario = request.user
            
            # Calcular tamaño del archivo
            if video.archivo_video:
                video.tamanio = video.archivo_video.size

                # Calcular duración real usando OpenCV
                info = get_video_info(video.archivo_video.path)
                if info and info['duration']:
                    # Formatear duración a mm:ss
                    total_seconds = int(info['duration'])
                    minutos = total_seconds // 60
                    segundos = total_seconds % 60
                    video.duracion = f"{minutos:02d}:{segundos:02d}"
                else:
                    video.duracion = "00:00"
            
            video.save()
            
            # Generar thumbnail automáticamente
            print(f"Iniciando proceso de generación de thumbnail para video {video.id}")
            try:
                from .utils import generar_thumbnail_para_guia_video
                success = generar_thumbnail_para_guia_video(video)
                if success:
                    print(f"Thumbnail generado exitosamente para video {video.id}")
                    messages.success(request, 'Video subido exitosamente. Vista previa generada.')
                else:
                    print(f"No se pudo generar thumbnail para video {video.id}")
                    messages.warning(request, 'Video subido exitosamente, pero no se pudo generar la vista previa.')
            except Exception as e:
                print(f"Error generando thumbnail: {e}")
                messages.warning(request, 'Video subido exitosamente, pero hubo un problema al generar la vista previa.')
                # No fallar si no se puede generar el thumbnail
                # Opcional: usar tarea asíncrona
                # from .tasks import generar_thumbnail_async
                # generar_thumbnail_async.delay(video.id)
            
            return redirect('guias_uso')
    else:
        form = GuiaVideoForm()
    
    return render(request, 'subir_video.html', {'form': form})


@login_required
def subir_archivo(request):
    """Vista para subir un nuevo archivo de guía."""
    if request.method == 'POST':
        form = GuiaArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.save(commit=False)
            archivo.usuario = request.user
            
            # Determinar tipo de archivo
            if archivo.archivo:
                extension = archivo.archivo.name.split('.')[-1].lower()
                if extension in ['doc', 'docx']:
                    archivo.tipo_archivo = 'doc'
                elif extension in ['xls', 'xlsx']:
                    archivo.tipo_archivo = 'xls'
                elif extension in ['ppt', 'pptx']:
                    archivo.tipo_archivo = 'ppt'
                elif extension == 'pdf':
                    archivo.tipo_archivo = 'pdf'
                elif extension == 'txt':
                    archivo.tipo_archivo = 'txt'
                else:
                    archivo.tipo_archivo = 'otro'
                
                archivo.tamanio = archivo.archivo.size
            
            archivo.save()
            messages.success(request, 'Archivo subido exitosamente.')
            return redirect('guias_uso')
    else:
        form = GuiaArchivoForm()
    
    return render(request, 'subir_archivo.html', {'form': form})


@login_required
def reproducir_video(request, video_id):
    """Vista para reproducir un video."""
    video = get_object_or_404(GuiaVideo, id=video_id, estado='publico')
    # Incrementar contador de visualizaciones
    video.visualizaciones += 1
    video.save()
    # Listado de otros videos
    videos_list = GuiaVideo.objects.filter(estado='publico').exclude(id=video.id).order_by('-fecha_subida')
    return render(request, 'reproducir_video.html', {'video': video, 'videos_list': videos_list})


@login_required
def descargar_archivo(request, archivo_id):
    """Vista para descargar un archivo."""
    archivo = get_object_or_404(GuiaArchivo, id=archivo_id, estado='publico')
    
    # Incrementar contador de descargas
    archivo.descargas += 1
    archivo.save()
    
    from django.http import FileResponse
    import os
    
    file_path = archivo.archivo.path
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{archivo.archivo.name.split("/")[-1]}"'
        return response
    
    return HttpResponseForbidden("Archivo no encontrado")


@login_required
def descargar_video(request, video_id):
    """Vista para descargar un video."""
    video = get_object_or_404(GuiaVideo, id=video_id, estado='publico')
    
    # Incrementar contador de descargas
    video.descargas += 1
    video.save()
    
    from django.http import FileResponse
    import os
    
    file_path = video.archivo_video.path
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{video.archivo_video.name.split("/")[-1]}"'
        return response
    
    return HttpResponseForbidden("Video no encontrado")


@login_required
def notificaciones_usuario(request):
    """
    Devuelve las notificaciones recientes del usuario autenticado, priorizando las no leídas.
    """
    notificaciones = Notification.objects.filter(usuario=request.user).order_by('leido', '-fecha')[:20]
    data = [
        {
            'id': n.id,
            'mensaje': n.mensaje,
            'link': n.link,
            'leido': n.leido,
            'fecha': n.fecha.strftime('%d/%m/%Y %H:%M'),
            'tipo': n.tipo,
        }
        for n in notificaciones
    ]
    return JsonResponse({'notificaciones': data})

@login_required
@require_POST
def marcar_notificacion_leida(request, notificacion_id):
    """
    Marca una notificación como leída.
    """
    n = get_object_or_404(Notification, id=notificacion_id, usuario=request.user)
    n.leido = True
    n.save(update_fields=['leido'])
    return JsonResponse({'success': True})

@login_required
@require_POST
def marcar_todas_notificaciones_leidas(request):
    Notification.objects.filter(usuario=request.user, leido=False).update(leido=True)
    return JsonResponse({'success': True})

@login_required
def regenerar_thumbnails(request):
    """Vista de administración para regenerar thumbnails de videos existentes."""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta función.')
        return redirect('guias_uso')
    
    if request.method == 'POST':
        try:
            success = regenerar_thumbnails_pendientes()
            if success:
                messages.success(request, 'Proceso de regeneración de thumbnails completado.')
            else:
                messages.warning(request, 'No se pudieron regenerar todos los thumbnails.')
        except Exception as e:
            messages.error(request, f'Error durante la regeneración: {e}')
        
        return redirect('guias_uso')
    
    # Contar videos sin thumbnail
    from .models import GuiaVideo
    videos_sin_thumbnail = GuiaVideo.objects.filter(thumbnail__isnull=True).count()
    total_videos = GuiaVideo.objects.count()
    
    context = {
        'videos_sin_thumbnail': videos_sin_thumbnail,
        'total_videos': total_videos,
    }
    
    return render(request, 'regenerar_thumbnails.html', context)

@login_required
def eliminar_video(request, video_id):
    """Permite eliminar un video solo al dueño o staff."""
    video = get_object_or_404(GuiaVideo, id=video_id)
    if request.user == video.usuario or request.user.is_staff:
        video.delete()
        messages.success(request, 'Video eliminado correctamente.')
    else:
        messages.error(request, 'No tienes permisos para eliminar este video.')
    return redirect('guias_uso')

@login_required
def cargar_liquidacion_lasegundaart(request):
    if request.method == "POST":
        form = LiquidacionPAMIForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_xlsx = request.FILES["archivo"]
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')
            from .utils import procesar_liquidacion_lasegundaart
            registros_creados = procesar_liquidacion_lasegundaart(archivo_xlsx, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_lasegundaart")
    else:
        form = LiquidacionPAMIForm()

    from .models import LiquidacionLaSegundaART
    liquidaciones = LiquidacionLaSegundaART.objects.all().order_by("-fecha_liquidacion")

    archivos_disponibles = list(
        LiquidacionLaSegundaART.objects.values_list('archivo_origen', flat=True).distinct()
    )

    return render(request, "liquidacion_lasegundaart.html", {
        "form": form,
        "liquidaciones": liquidaciones,
        "archivos_disponibles": archivos_disponibles
    })

@csrf_exempt
@login_required
def eliminar_liquidacion_lasegundaart(request):
    if request.method == "POST":
        data = json.loads(request.body)
        archivo_origen = data.get("archivo_origen")

        if archivo_origen:
            LiquidacionLaSegundaART.objects.filter(archivo_origen=archivo_origen).delete()
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)

@login_required
def cargar_liquidacion_osdipp(request):
    from .models import LiquidacionOSDIPP
    from .utils import procesar_liquidacion_osdipp_pdf
    if request.method == "POST":
        # Usar un formulario simple para PDF
        archivo_pdf = request.FILES.get("archivo")
        if archivo_pdf:
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')
            registros_creados = procesar_liquidacion_osdipp_pdf(archivo_pdf, archivo_origen)
            messages.success(request, f"Se cargaron {registros_creados} registros correctamente.")
            return redirect("cargar_liquidacion_osdipp")
    # Listar liquidaciones y archivos disponibles
    liquidaciones = LiquidacionOSDIPP.objects.all().order_by("-fecha_liquidacion")
    archivos_disponibles = list(
        LiquidacionOSDIPP.objects.values_list('archivo_origen', flat=True).distinct()
    )
    return render(request, "liquidacion_osdipp.html", {
        "liquidaciones": liquidaciones,
        "archivos_disponibles": archivos_disponibles
    })

@login_required
@require_GET
def usuario_detalle_json(request, user_id):
    user = get_object_or_404(User, id=user_id)
    farmacia = user.farmacia
    data = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'id_facaf': user.id_facaf,
        'codigo_farmacia': farmacia.codigo_farmacia if farmacia else '',
        'nombre_farmacia': farmacia.nombre if farmacia else '',
        'direccion': farmacia.direccion if farmacia else '',
        'ciudad': farmacia.ciudad if farmacia else '',
        'provincia': farmacia.provincia if farmacia else '',
        'contacto_principal': farmacia.contacto_principal if farmacia else '',
        'email_contacto': farmacia.email_contacto if farmacia else '',
        'telefono_contacto': farmacia.telefono_contacto if farmacia else '',
        'cuit': farmacia.cuit if farmacia else '',
        'cbu': farmacia.cbu if farmacia else '',
        'drogueria': farmacia.drogueria if farmacia else '',
    }
    return JsonResponse(data)

@login_required
@csrf_exempt
def usuario_actualizar_json(request, user_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    user = get_object_or_404(User, id=user_id)
    data = json.loads(request.body)
    # Actualizar campos de User
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.id_facaf = data.get('id_facaf', user.id_facaf)
    if data.get('password'):
        user.set_password(data['password'])
    user.save()
    # Actualizar Farmacia
    farmacia = user.farmacia
    if farmacia:
        farmacia.codigo_farmacia = data.get('codigo_farmacia', farmacia.codigo_farmacia)
        farmacia.nombre = data.get('nombre_farmacia', farmacia.nombre)
        farmacia.direccion = data.get('direccion', farmacia.direccion)
        farmacia.ciudad = data.get('ciudad', farmacia.ciudad)
        farmacia.provincia = data.get('provincia', farmacia.provincia)
        farmacia.contacto_principal = data.get('contacto_principal', farmacia.contacto_principal)
        farmacia.email_contacto = data.get('email_contacto', farmacia.email_contacto)
        farmacia.telefono_contacto = data.get('telefono_contacto', farmacia.telefono_contacto)
        farmacia.cuit = data.get('cuit', farmacia.cuit)
        farmacia.cbu = data.get('cbu', farmacia.cbu)
        farmacia.drogueria = data.get('drogueria', farmacia.drogueria)
        farmacia.save()
    # Actualizar grupo/permiso
    permiso = data.get('permiso')
    if permiso in ['Camara', 'Farmacia']:
        camara_group, _ = Group.objects.get_or_create(name='Camara')
        farmacia_group, _ = Group.objects.get_or_create(name='Farmacia')
        user.groups.clear()
        if permiso == 'Camara':
            user.groups.add(camara_group)
        else:
            user.groups.add(farmacia_group)
    # Notificación
    Notification.objects.create(
        usuario=user,
        mensaje=f"Tus datos han sido actualizados correctamente.",
        link="/usuarios/",
        tipo="foro"
    )
    return JsonResponse({'success': True})

# Ejemplo de aplicación del decorador a vistas del módulo Camara
@login_required
@camara_required
def calendario(request):
    
    #Agregar logica del calendario
    presentaciones = Presentacion.objects.all()

    return render(request, 'calendario.html', {"presentaciones": presentaciones})

@login_required
@camara_required
def home_liquidacion(request):
    obras_sociales = CargaDatos.OBRAS_SOCIALES
    return render(request, 'cargar_liquidaciones.html', {'obras_sociales': obras_sociales})

@login_required
@camara_required
def transferencias_tesorera(request):
    resumen_por_obra, sin_relacion = obtener_transferencias_por_sociedad()
    return render(request, "transferencias.html", {
        "resumen_por_obra": resumen_por_obra,
        "sin_relacion": sin_relacion
    })

@login_required
@camara_required
def lista_usuarios(request):
    usuarios = Farmacia.objects.all()
    return render(request, 'usuarios.html', {'usuarios': usuarios})

@csrf_exempt
@login_required
def eliminar_presentacion_calendario(request, presentacion_id):
    """
    Elimina una presentación del calendario (modelo Presentacion).
    Solo el usuario creador o un superusuario puede eliminarla.
    """
    if request.method == 'DELETE':
        from .models import Presentacion
        try:
            presentacion = Presentacion.objects.get(id=presentacion_id)
            if presentacion.usuario == request.user or request.user.is_superuser:
                presentacion.delete()
                return JsonResponse({'message': 'Presentación eliminada correctamente'}, status=200)
            else:
                return JsonResponse({'error': 'No tienes permisos para eliminar esta presentación.'}, status=403)
        except Presentacion.DoesNotExist:
            return JsonResponse({'error': 'Presentación no encontrada'}, status=404)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
