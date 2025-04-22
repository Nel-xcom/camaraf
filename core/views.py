# ────────────────────────────────
# 🧩 Standard Library
# ────────────────────────────────
import calendar
import openpyxl
import pandas as pd
from collections import Counter, defaultdict
from datetime import datetime, date, timedelta
import json

# ────────────────────────────────
# 🔧 Django Core & Utilities
# ────────────────────────────────
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.models import Permission
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
from django.views.decorators.http import require_http_methods, require_POST

# ────────────────────────────────
# 📦 Local Imports
# ────────────────────────────────
from .forms import (
    CargaDatosForm, CargaDatosFormAvalian, CargaDatosFormOSDIPP, CargaDatosFormPAMI,
    CustomLoginForm, CustomPasswordResetForm,
    FarmaciaRegisterForm, LiquidacionPAMIForm, LiquidacionJerarquicosForm,
    LiquidacionGalenoForm, LiquidacionOsfatlyfForm, LiquidacionAsociartForm,
    LiquidacionPrevencionARTForm
)
from .models import (
    CargaDatos, Presentacion, User, Farmacia,
    Liquidacion, LiquidacionGaleno, LiquidacionPAMI, LiquidacionJerarquicos,
    LiquidacionOspil, LiquidacionOsfatlyf, LiquidacionPAMIOncologico,
    LiquidacionPAMIPanales, LiquidacionPAMIVacunas, LiquidacionAndinaART,
    LiquidacionAsociart, LiquidacionColoniaSuiza, LiquidacionExperta,
    LiquidacionGalenoART, LiquidacionPrevencionART
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
    obtener_transferencias_por_sociedad
)

#----

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
    # Filtrar solo las presentaciones del usuario actual
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
        # Concatenar first_name y last_name para búsquedas combinadas
        usuarios = Farmacia.objects.annotate(
            full_name=Concat('first_name', Value(' '), 'last_name', output_field=CharField())
        ).filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(full_name__icontains=query)  # Buscar en el nombre completo concatenado
        ).distinct()
    else:
        # Return-- > result
        # Retornar los usuarios más recientes
        usuarios = Farmacia.objects.all().order_by('-date_joined')[:10]

    results = [
        {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'sector': user.sectores.first().nombre if user.sectores.exists() else "Sin asignar",
        }
        for user in usuarios
    ]
    return JsonResponse({'results': results})


@login_required
def actualizar_usuario(request):
    user = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu información se ha actualizado correctamente.")
            return redirect('actualizar_usuario')
        else:
            messages.error(request, "Ocurrió un error al actualizar tu información.")
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'actualizar_usuario.html', {'form': form})

@login_required
def calendario(request):
    # Obtener presentaciones del mes actual
    today = now()
    presentaciones = Presentacion.objects.filter(
        fecha__year=today.year, fecha__month=today.month
    ).order_by('fecha')

    return render(request, 'calendario.html', {"presentaciones": presentaciones})

@login_required
def calendar_farmacias(request):
    today = now()
    year, month = today.year, today.month

    # Obtener la cantidad de días del mes actual
    num_dias = calendar.monthrange(year, month)[1]
    
    # Generar una lista con todas las fechas del mes
    dias_del_mes = [f"{year}-{month:02d}-{dia:02d}" for dia in range(1, num_dias + 1)]

    return render(request, 'calendar_farmacias.html', {
        "dias_del_mes": dias_del_mes,  # Enviamos la lista de fechas
        "mes_actual": today.strftime('%Y-%m'),  # Enviamos el mes actual formateado
    })

@login_required
def get_presentaciones(request):
    year = request.GET.get("year")
    month = request.GET.get("month")

    if not year or not month:
        return JsonResponse([], safe=False)  # Si no se reciben parámetros, devolver lista vacía

    try:
        year = int(year)
        month = int(month)
    except ValueError:
        return JsonResponse([], safe=False)  # Evitar errores si los parámetros son inválidos

    presentaciones = Presentacion.objects.filter(
        usuario__farmacia=request.user.farmacia,
        fecha__year=year,
        fecha__month=month
    ).order_by('fecha')

    data = [
        {
            "fecha": p.fecha.strftime('%Y-%m-%d'),
            "obra_social": p.obra_social
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
        Presentacion.objects.create(
            usuario=request.user,
            fecha=fecha,
            obra_social=obra_social,
            quincena=quincena
        )

        messages.success(request, "Presentación guardada exitosamente.")
        return redirect("calendario")

    return redirect("calendario")

@csrf_exempt
@login_required
def eliminar_presentacion(request, presentacion_id):
    if request.method == 'DELETE':
        try:
            presentacion = Presentacion.objects.get(id=presentacion_id, usuario=request.user)
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
        periodo = p.periodo.strip() if p.periodo else ""

        # Convertir periodo de CargaDatos a formato YYYY-MM para comparar con LiquidacionGaleno.fecha
        if len(periodo) >= 7 and periodo[:4].isdigit() and periodo[-2:].isdigit():
            year = int(periodo[:4])
            month = int(periodo[-2:])
        else:
            year = None
            month = None

        liquidacion = None
        importe_liquidado = 0

        if year and month:
            liquidacion = LiquidacionGaleno.objects.filter(
                prestador=p.obra_social, 
                fecha__year=year, 
                fecha__month=month
            ).first()

            # Solo asignar importe_liquidado si el período de CargaDatos coincide con LiquidacionGaleno.fecha
            if liquidacion and liquidacion.fecha.year == year and liquidacion.fecha.month == month:
                importe_liquidado = float(liquidacion.importe_liquidado)

        chart_data.append({
            "importe_100": float(p.importe_100 or 0),
            "importe_liquidado": importe_liquidado
        })

    print(f"DEBUG: {chart_data}")  # <-- Verificar en consola del servidor si el importe_liquidado es correcto

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
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')  
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
            archivo_origen = 'lq_' + datetime.now().strftime('%d%m%y_%H%M%S%f')  # ✅ Identificador único
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
    datos_panel = obtener_datos_panel()

    return render(request, "panel_liquidaciones.html", {"datos_panel": datos_panel})