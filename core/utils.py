import pandas as pd
from .models import LiquidacionPAMI, LiquidacionJerarquicos, LiquidacionGaleno, LiquidacionOspil, LiquidacionOsfatlyf, LiquidacionPAMIOncologico, LiquidacionPAMIPanales, LiquidacionPAMIVacunas, LiquidacionAndinaART, LiquidacionAsociart, LiquidacionColoniaSuiza, LiquidacionExperta, LiquidacionGalenoART, LiquidacionPrevencionART
from core.models import Farmacia
from django.utils.timezone import now
from collections import defaultdict

def procesar_liquidacion_galeno(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    df = xls.parse(xls.sheet_names[0])

    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    registros_creados = 0

    for _, row in df.iterrows():
        if pd.isna(row['prestador']) or pd.isna(row['fecha']) or pd.isna(row['orden_de_pago']):
            continue

        fecha = row['fecha']
        if isinstance(fecha, pd.Timestamp):
            fecha = fecha.date()

        LiquidacionGaleno.objects.create(
            prestador=row['prestador'],
            fecha=fecha,
            orden_de_pago=row['orden_de_pago'],
            importe=row['importe'],
            retenciones=row['retenciones'],
            credito=row['credito'],
            liquidacion=row['liquidacion'],
            importe_liquidado=row['importe.1'],
            archivo_origen=archivo_origen
        )
        registros_creados += 1

    return registros_creados

def procesar_liquidacion_ospil(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=4)  # Saltear encabezado

    registros_creados = 0

    for _, row in df.iterrows():
        if pd.isna(row[0]) or pd.isna(row[2]) or "Total" in str(row[0]):
            continue  # ⛔ Filtrar filas vacías o resumen

        codigo_farmacia = str(row[0]).strip()  # 🟩 Columna A
        nombre_farmacia = str(row[2]).strip()  # ✅ Columna C → SOCIAL I, etc
        plan = "OSPIL"  # Fijo
        fecha_liquidacion = now().date()

        importe_100 = float(row[4]) if not pd.isna(row[4]) else 0.00
        a_cargo_os = float(row[5]) if not pd.isna(row[5]) else 0.00
        bonificacion = float(row[11]) if not pd.isna(row[11]) else 0.00
        nota_credito = float(row[12]) if not pd.isna(row[12]) else 0.00
        subtotal_pagar = float(row[17]) if not pd.isna(row[17]) else 0.00

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

        LiquidacionOspil.objects.create(
            farmacia=farmacia,
            codigo_farmacia=codigo_farmacia,
            nombre_farmacia=nombre_farmacia,
            plan=plan,
            fecha_liquidacion=fecha_liquidacion,
            importe_100=importe_100,
            a_cargo_os=a_cargo_os,
            bonificacion=bonificacion,
            nota_credito=nota_credito,
            subtotal_pagar=subtotal_pagar,
            archivo_origen=archivo_origen
        )

        registros_creados += 1

    return registros_creados


def procesar_liquidacion_pami(archivo_xlsx, archivo_origen):
    """
    Función para procesar un archivo XLSX de liquidación PAMI y guardarlo en la base de datos.
    """
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]  # Seleccionamos la primera hoja
    df = xls.parse(hoja, skiprows=7)  # Saltamos las primeras 7 filas que son títulos

    registros_creados = 0

    for index, row in df.iterrows():
        # Evitar filas vacías
        if pd.isna(row[0]) or pd.isna(row[2]) or pd.isna(row[14]):
            continue

        codigo_farmacia = str(row[0]).strip()
        nombre_farmacia = str(row[2]).strip()
        plan = str(row[3]).strip()

        # Datos financieros
        importe_100 = float(row[14]) if not pd.isna(row[14]) else 0.00
        a_cargo_os = float(row[15]) if not pd.isna(row[15]) else 0.00
        bonificacion = float(row[16]) if not pd.isna(row[16]) else 0.00
        nota_credito = float(row[17]) if not pd.isna(row[17]) else 0.00
        subtotal_pagar = float(row[23]) if not pd.isna(row[23]) else 0.00

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

        # 💾 Guardar el archivo_origen ahora también
        LiquidacionPAMI.objects.create(
            farmacia=farmacia,
            codigo_farmacia=codigo_farmacia,
            nombre_farmacia=nombre_farmacia,
            plan=plan,
            fecha_liquidacion=now().date(),
            importe_100=importe_100,
            a_cargo_os=a_cargo_os,
            bonificacion=bonificacion,
            nota_credito=nota_credito,
            subtotal_pagar=subtotal_pagar,
            archivo_origen=archivo_origen  # 🧠 IDENTIFICADOR CLAVE
        )

        registros_creados += 1

    return registros_creados

def procesar_liquidacion_pami_oncologico(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=7)

    registros_creados = 0

    for index, row in df.iterrows():
        if pd.isna(row[0]) or pd.isna(row[2]) or pd.isna(row[14]):
            continue

        codigo_farmacia = str(row[0]).strip()
        nombre_farmacia = str(row[2]).strip()
        plan = str(row[3]).strip()

        importe_100 = float(row[9]) if not pd.isna(row[9]) else 0.00
        a_cargo_os = float(row[10]) if not pd.isna(row[10]) else 0.00
        bonificacion = float(row[11]) if not pd.isna(row[11]) else 0.00
        nota_credito = float(row[12]) if not pd.isna(row[12]) else 0.00
        subtotal_pagar = float(row[17]) if not pd.isna(row[17]) else 0.00

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

        LiquidacionPAMIOncologico.objects.create(
            farmacia=farmacia,
            codigo_farmacia=codigo_farmacia,
            nombre_farmacia=nombre_farmacia,
            plan=plan,
            fecha_liquidacion=now().date(),
            importe_100=importe_100,
            a_cargo_os=a_cargo_os,
            bonificacion=bonificacion,
            nota_credito=nota_credito,
            subtotal_pagar=subtotal_pagar,
            archivo_origen=archivo_origen
        )

        registros_creados += 1

    return registros_creados

def procesar_liquidacion_pami_panales(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=4)  # fila 5 = títulos

    registros_creados = 0
    plan_actual = ""

    for index, row in df.iterrows():
        # Detectar nueva cabecera de plan
        if isinstance(row[0], str) and "PLAN:" in row[0].upper():
            plan_actual = row[0].split("PLAN:")[-1].strip()
            continue

        if pd.isna(row[0]) or pd.isna(row[2]) or pd.isna(row[9]):
            continue

        codigo_farmacia = str(row[0]).strip()
        nombre_farmacia = str(row[2]).strip()

        importe_100 = float(row[9]) if not pd.isna(row[9]) else 0.00
        a_cargo_os = float(row[10]) if not pd.isna(row[10]) else 0.00
        bonificacion = float(row[11]) if not pd.isna(row[11]) else 0.00
        nota_credito = float(row[12]) if not pd.isna(row[12]) else 0.00
        subtotal_pagar = float(row[17]) if not pd.isna(row[17]) else 0.00

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

        LiquidacionPAMIPanales.objects.create(
            farmacia=farmacia,
            codigo_farmacia=codigo_farmacia,
            nombre_farmacia=nombre_farmacia,
            plan=plan_actual,
            fecha_liquidacion=now().date(),
            importe_100=importe_100,
            a_cargo_os=a_cargo_os,
            bonificacion=bonificacion,
            nota_credito=nota_credito,
            subtotal_pagar=subtotal_pagar,
            archivo_origen=archivo_origen
        )

        registros_creados += 1

    return registros_creados

def procesar_liquidacion_pami_vacunas(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=7)

    registros_creados = 0

    for index, row in df.iterrows():
        if pd.isna(row[0]) or pd.isna(row[2]) or pd.isna(row[9]):
            continue

        codigo_farmacia = str(row[0]).strip()
        nombre_farmacia = str(row[2]).strip()
        plan = str(row[3]).strip()

        importe_100 = float(row[9]) if not pd.isna(row[9]) else 0.00
        a_cargo_os = float(row[10]) if not pd.isna(row[10]) else 0.00
        bonificacion = float(row[11]) if not pd.isna(row[11]) else 0.00
        nota_credito = float(row[12]) if not pd.isna(row[12]) else 0.00
        subtotal_pagar = float(row[17]) if not pd.isna(row[17]) else 0.00

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

        LiquidacionPAMIVacunas.objects.create(
            farmacia=farmacia,
            codigo_farmacia=codigo_farmacia,
            nombre_farmacia=nombre_farmacia,
            plan=plan,
            fecha_liquidacion=now().date(),
            importe_100=importe_100,
            a_cargo_os=a_cargo_os,
            bonificacion=bonificacion,
            nota_credito=nota_credito,
            subtotal_pagar=subtotal_pagar,
            archivo_origen=archivo_origen
        )

        registros_creados += 1

    return registros_creados


def procesar_liquidacion_jerarquicos(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=7)

    registros_creados = 0

    for index, row in df.iterrows():
        if pd.isna(row[0]) or pd.isna(row[2]) or pd.isna(row[4]):
            continue

        codigo_farmacia = str(row[0]).strip()
        nombre_farmacia = str(row[2]).strip()
        plan = str(row[3]).strip()

        importe_100 = float(row[4]) if not pd.isna(row[4]) else 0.00
        a_cargo_os = float(row[5]) if not pd.isna(row[5]) else 0.00
        bonificacion = float(row[11]) if not pd.isna(row[11]) else 0.00
        nota_credito = float(row[12]) if not pd.isna(row[12]) else 0.00
        subtotal_pagar = float(row[17]) if not pd.isna(row[17]) else 0.00

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

        LiquidacionJerarquicos.objects.create(
            farmacia=farmacia,
            codigo_farmacia=codigo_farmacia,
            nombre_farmacia=nombre_farmacia,
            plan=plan,
            fecha_liquidacion=now().date(),
            importe_100=importe_100,
            a_cargo_os=a_cargo_os,
            bonificacion=bonificacion,
            nota_credito=nota_credito,
            subtotal_pagar=subtotal_pagar,
            archivo_origen=archivo_origen  # ✅ Aquí lo agregamos
        )

        registros_creados += 1

    return registros_creados

def procesar_liquidacion_osfatlyf(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    df = xls.parse(xls.sheet_names[0], skiprows=4)  # Fila 5 contiene los títulos

    registros_creados = 0

    for index, row in df.iterrows():
        # Validación de campos clave
        if pd.isna(row[0]) or pd.isna(row[2]) or pd.isna(row[9]):
            continue

        codigo_farmacia = str(row[0]).strip()

        nombre_farmacia = str(row[2]).strip()  # Columna C = nombre de farmacia
        plan = "OSFATLYF"
        fecha_liquidacion = now().date()

        importe_100 = float(row[9]) if not pd.isna(row[9]) else 0.00  # Columna J = Liquidado total
        a_cargo_os = float(row[10]) if not pd.isna(row[10]) else 0.00  # Columna K
        bonificacion = float(row[11]) if not pd.isna(row[11]) else 0.00  # Columna L

        # Crear farmacia si no existe
        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

        # Guardar registro
        LiquidacionOsfatlyf.objects.create(
            farmacia=farmacia,
            codigo_farmacia=codigo_farmacia,
            nombre_farmacia=nombre_farmacia,
            plan=plan,
            fecha_liquidacion=fecha_liquidacion,
            importe_100=importe_100,
            a_cargo_os=a_cargo_os,
            bonificacion=bonificacion,
            nota_credito=0,
            archivo_origen=archivo_origen
        )

        registros_creados += 1

    return registros_creados

def procesar_liquidacion_andina_art(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=7)

    registros_creados = 0

    for index, row in df.iterrows():
        if pd.isna(row[0]) or pd.isna(row[2]) or pd.isna(row[4]):
            continue

        codigo_farmacia = str(row[0]).strip()
        nombre_farmacia = str(row[2]).strip()
        plan = "AMBULATORIO 100%"  # Ya se conoce por contexto, está en la fila 6

        importe_100 = float(row[4]) if not pd.isna(row[4]) else 0.00
        a_cargo_os = float(row[9]) if not pd.isna(row[9]) else 0.00
        bonificacion = float(row[10]) if not pd.isna(row[10]) else 0.00
        nota_credito = float(row[11]) if not pd.isna(row[11]) else 0.00
        subtotal_pagar = float(row[17]) if not pd.isna(row[17]) else 0.00

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

        LiquidacionAndinaART.objects.create(
            farmacia=farmacia,
            codigo_farmacia=codigo_farmacia,
            nombre_farmacia=nombre_farmacia,
            plan=plan,
            fecha_liquidacion=now().date(),
            importe_100=importe_100,
            a_cargo_os=a_cargo_os,
            bonificacion=bonificacion,
            nota_credito=nota_credito,
            subtotal_pagar=subtotal_pagar,
            archivo_origen=archivo_origen
        )

        registros_creados += 1

    return registros_creados

def procesar_liquidacion_asociart(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=7)

    registros_creados = 0

    for index, row in df.iterrows():
        if pd.isna(row[0]) or pd.isna(row[2]) or pd.isna(row[9]):
            continue

        codigo_farmacia = str(row[0]).strip()
        nombre_farmacia = str(row[2]).strip()
        plan = str(row[3]).strip()

        importe_100 = float(row[9]) if not pd.isna(row[9]) else 0.00
        a_cargo_os = float(row[10]) if not pd.isna(row[10]) else 0.00
        bonificacion = float(row[11]) if not pd.isna(row[11]) else 0.00
        nota_credito = float(row[12]) if not pd.isna(row[12]) else 0.00
        subtotal_pagar = float(row[17]) if not pd.isna(row[17]) else 0.00

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

        LiquidacionAsociart.objects.create(
            farmacia=farmacia,
            codigo_farmacia=codigo_farmacia,
            nombre_farmacia=nombre_farmacia,
            plan=plan,
            fecha_liquidacion=now().date(),
            importe_100=importe_100,
            a_cargo_os=a_cargo_os,
            bonificacion=bonificacion,
            nota_credito=nota_credito,
            subtotal_pagar=subtotal_pagar,
            archivo_origen=archivo_origen
        )

        registros_creados += 1

    return registros_creados

def procesar_liquidacion_coloniasuiza(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=7)

    plan_sheet = xls.parse(hoja, skiprows=1, nrows=1)
    plan = str(plan_sheet.iloc[0, 0]).replace("Plan: ", "").strip()

    registros_creados = 0
    for index, row in df.iterrows():
        if pd.isna(row[0]) or pd.isna(row[2]) or pd.isna(row[9]):
            continue

        codigo_farmacia = str(row[0]).strip()
        nombre_farmacia = str(row[2]).strip()

        importe_100 = float(row[9]) if not pd.isna(row[9]) else 0.00
        a_cargo_os = float(row[10]) if not pd.isna(row[10]) else 0.00
        bonificacion = float(row[11]) if not pd.isna(row[11]) else 0.00
        nota_credito = float(row[12]) if not pd.isna(row[12]) else 0.00
        subtotal_pagar = float(row[16]) if not pd.isna(row[16]) else 0.00

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

        LiquidacionColoniaSuiza.objects.create(
            farmacia=farmacia,
            codigo_farmacia=codigo_farmacia,
            nombre_farmacia=nombre_farmacia,
            plan=plan,
            fecha_liquidacion=now().date(),
            importe_100=importe_100,
            a_cargo_os=a_cargo_os,
            bonificacion=bonificacion,
            nota_credito=nota_credito,
            subtotal_pagar=subtotal_pagar,
            archivo_origen=archivo_origen
        )

        registros_creados += 1

    return registros_creados

def procesar_liquidacion_experta(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=7)

    plan = "01 - AMBULATORIOS 100%"  # Fila 6
    registros_creados = 0

    for index, row in df.iterrows():
        if pd.isna(row[0]) or pd.isna(row[2]) or pd.isna(row[4]):
            continue

        codigo_farmacia = str(row[0]).strip()
        nombre_farmacia = str(row[2]).strip()

        importe_100 = float(row[9]) if not pd.isna(row[4]) else 0.00
        a_cargo_os = float(row[10]) if not pd.isna(row[9]) else 0.00
        bonificacion = float(row[11]) if not pd.isna(row[10]) else 0.00
        nota_credito = float(row[12]) if not pd.isna(row[11]) else 0.00
        subtotal_pagar = float(row[17]) if not pd.isna(row[17]) else 0.00

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

        LiquidacionExperta.objects.create(
            farmacia=farmacia,
            codigo_farmacia=codigo_farmacia,
            nombre_farmacia=nombre_farmacia,
            plan=plan,
            fecha_liquidacion=now().date(),
            importe_100=importe_100,
            a_cargo_os=a_cargo_os,
            bonificacion=bonificacion,
            nota_credito=nota_credito,
            subtotal_pagar=subtotal_pagar,
            archivo_origen=archivo_origen
        )
        registros_creados += 1

    return registros_creados

def procesar_liquidacion_galenoart(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=7)

    registros_creados = 0

    for _, row in df.iterrows():
        if pd.isna(row[0]) or pd.isna(row[2]) or pd.isna(row[9]):
            continue

        codigo_farmacia = str(row[0]).strip()
        nombre_farmacia = str(row[2]).strip()
        plan = str(row[3]).strip()

        importe_100 = float(row[9]) if not pd.isna(row[9]) else 0.00
        a_cargo_os = float(row[10]) if not pd.isna(row[10]) else 0.00
        bonificacion = float(row[11]) if not pd.isna(row[11]) else 0.00
        nota_credito = float(row[12]) if not pd.isna(row[12]) else 0.00
        subtotal_pagar = float(row[17]) if not pd.isna(row[17]) else 0.00

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

        LiquidacionGalenoART.objects.create(
            farmacia=farmacia,
            codigo_farmacia=codigo_farmacia,
            nombre_farmacia=nombre_farmacia,
            plan=plan,
            fecha_liquidacion=now().date(),
            importe_100=importe_100,
            a_cargo_os=a_cargo_os,
            bonificacion=bonificacion,
            nota_credito=nota_credito,
            subtotal_pagar=subtotal_pagar,
            archivo_origen=archivo_origen,
        )

        registros_creados += 1

    return registros_creados

def procesar_liquidacion_prevencion_art(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=7)

    registros_creados = 0

    for index, row in df.iterrows():
        if pd.isna(row[0]) or pd.isna(row[2]) or pd.isna(row[4]):
            continue

        codigo_farmacia = str(row[0]).strip()
        nombre_farmacia = str(row[2]).strip()
        plan = "Plan: 01 - Ambulatorio 100%"

        importe_100 = float(row[4]) if not pd.isna(row[4]) else 0.00
        a_cargo_os = float(row[9]) if not pd.isna(row[9]) else 0.00
        bonificacion = float(row[10]) if not pd.isna(row[10]) else 0.00
        nota_credito = float(row[11]) if not pd.isna(row[11]) else 0.00
        subtotal_pagar = float(row[17]) if not pd.isna(row[17]) else 0.00

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

        LiquidacionPrevencionART.objects.create(
            farmacia=farmacia,
            codigo_farmacia=codigo_farmacia,
            nombre_farmacia=nombre_farmacia,
            plan=plan,
            fecha_liquidacion=now().date(),
            importe_100=importe_100,
            a_cargo_os=a_cargo_os,
            bonificacion=bonificacion,
            nota_credito=nota_credito,
            subtotal_pagar=subtotal_pagar,
            archivo_origen=archivo_origen
        )

        registros_creados += 1

    return registros_creados


def obtener_detalle_transferencias():
    """
    Obtiene el detalle de los montos a transferir por grupo de farmacias y por liquidación,
    agrupándolos correctamente.
    """
    transferencias_por_obra = {
        "PAMI": defaultdict(float),
        "Galeno": defaultdict(float),
        "Jerárquicos Salud": defaultdict(float)
    }

    # Recorrer liquidaciones PAMI
    for liquidacion in LiquidacionPAMI.objects.all():
        nombre_farmacia = liquidacion.nombre_farmacia.strip().lower()
        transferencias_por_obra["PAMI"][(nombre_farmacia, liquidacion.fecha_liquidacion)] += float(liquidacion.subtotal_pagar)

    # Recorrer liquidaciones Galeno
    for liquidacion in LiquidacionGaleno.objects.all():
        nombre_farmacia = liquidacion.prestador.strip().lower()
        transferencias_por_obra["Galeno"][(nombre_farmacia, liquidacion.fecha)] += float(liquidacion.importe_liquidado)

    # Recorrer liquidaciones Jerárquicos
    for liquidacion in LiquidacionJerarquicos.objects.all():
        nombre_farmacia = liquidacion.nombre_farmacia.strip().lower()
        transferencias_por_obra["Jerárquicos Salud"][(nombre_farmacia, liquidacion.fecha_liquidacion)] += float(liquidacion.subtotal_pagar)

    # Convertimos a un formato adecuado para la plantilla
    resultado = {
        obra_social: [{"nombre_farmacia": k[0].title(), "fecha": k[1], "total_transferir": v} for k, v in data.items()]
        for obra_social, data in transferencias_por_obra.items()
    }

    return resultado

def obtener_datos_panel():
    """
    Genera los datos necesarios para el panel de liquidaciones con manejo de valores vacíos.
    """
    data = {
        "total_facturado": 0,
        "total_liquidado": 0,
        "retenciones_totales": 0,
        "bonificaciones_totales": 0,
        "pendientes_pago": 0,
        "pagos_por_obra": {},
        "evolucion_pagos": {},
    }

    liquidaciones_pami = LiquidacionPAMI.objects.all()
    liquidaciones_galeno = LiquidacionGaleno.objects.all()
    liquidaciones_jerarquicos = LiquidacionJerarquicos.objects.all()

    if not (liquidaciones_pami.exists() or liquidaciones_galeno.exists() or liquidaciones_jerarquicos.exists()):
        return data  # Devolvemos datos vacíos si no hay liquidaciones

    # Procesar PAMI
    for liquidacion in liquidaciones_pami:
        mes_año = liquidacion.fecha_liquidacion.strftime("%Y-%m")
        data["pagos_por_obra"].setdefault("PAMI", 0)
        data["pagos_por_obra"]["PAMI"] += float(liquidacion.subtotal_pagar)
        data["evolucion_pagos"].setdefault(mes_año, 0)
        data["evolucion_pagos"][mes_año] += float(liquidacion.subtotal_pagar)

    # Procesar Galeno
    for liquidacion in liquidaciones_galeno:
        mes_año = liquidacion.fecha.strftime("%Y-%m")
        data["pagos_por_obra"].setdefault("Galeno", 0)
        data["pagos_por_obra"]["Galeno"] += float(liquidacion.importe_liquidado)
        data["evolucion_pagos"].setdefault(mes_año, 0)
        data["evolucion_pagos"][mes_año] += float(liquidacion.importe_liquidado)

    # Procesar Jerárquicos
    for liquidacion in liquidaciones_jerarquicos:
        mes_año = liquidacion.fecha_liquidacion.strftime("%Y-%m")
        data["pagos_por_obra"].setdefault("Jerárquicos", 0)
        data["pagos_por_obra"]["Jerárquicos"] += float(liquidacion.subtotal_pagar)
        data["evolucion_pagos"].setdefault(mes_año, 0)
        data["evolucion_pagos"][mes_año] += float(liquidacion.subtotal_pagar)

    return data