import pandas as pd
from .models import LiquidacionPAMI, LiquidacionJerarquicos, LiquidacionGaleno, LiquidacionOspil, LiquidacionOsfatlyf, LiquidacionPAMIOncologico, LiquidacionPAMIPanales, LiquidacionPAMIVacunas, LiquidacionAndinaART, LiquidacionAsociart, LiquidacionColoniaSuiza, LiquidacionExperta, LiquidacionGalenoART, LiquidacionPrevencionART, User, LiquidacionLaSegundaART
from core.models import Farmacia
from django.utils.timezone import now
from collections import defaultdict

import os
import tempfile
from PIL import Image
from django.core.files import File
from django.conf import settings

import cv2
import uuid

import pdfplumber
from .models import LiquidacionOSDIPP
import re


def procesar_liquidacion_galeno(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    # Saltar 5 filas: fila 6 (índice 5) serán los títulos, fila 7 en adelante los valores
    df = xls.parse(xls.sheet_names[0], skiprows=5)

    # Debug: mostrar nombres de columna y primeras filas
    print('Columnas detectadas:', list(df.columns))
    print('Primeras filas del DataFrame:')
    print(df.head(10))

    # Normalizar nombres de columna
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    registros_creados = 0

    for idx, row in df.iterrows():
        # Validar que existan los campos clave y que sean numéricos
        if pd.isna(row.get('prestador')) or pd.isna(row.get('fecha')) or pd.isna(row.get('orden_de_pago')):
            print(f'Fila {idx} saltada: falta prestador, fecha u orden de pago')
            continue
        if pd.isna(row.get('importe')) or pd.isna(row.get('retenciones')) or pd.isna(row.get('crédito')):
            print(f'Fila {idx} saltada: falta importe, retenciones o crédito')
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
            credito=row['crédito'],
            liquidacion=row['liquidación'] if 'liquidación' in row else '',
            importe_liquidado=row['importe.1'] if 'importe.1' in row else row['importe'],
            archivo_origen=archivo_origen
        )
        registros_creados += 1

    print(f'Total de registros creados: {registros_creados}')
    return registros_creados

def procesar_liquidacion_ospil(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=4)  # Saltear encabezado

    registros_creados = 0

    for _, row in df.iterrows():
        try:
            # Verificar que existan las columnas mínimas necesarias de forma segura
            if len(row) < 3:
                continue
                
            # Verificar que las columnas básicas no sean nulas y no sean totales
            if pd.isna(row.iloc[0]) or pd.isna(row.iloc[2]) or "Total" in str(row.iloc[0]):
                continue  # ⛔ Filtrar filas vacías o resumen

            codigo_farmacia = str(row.iloc[0]).strip()  # 🟩 Columna A
            nombre_farmacia = str(row.iloc[2]).strip()  # ✅ Columna C → SOCIAL I, etc
            plan = "OSPIL"  # Fijo
            fecha_liquidacion = now().date()

            # Campos financieros básicos - acceso seguro
            importe_100 = float(row.iloc[10]) if len(row) > 10 and not pd.isna(row.iloc[10]) else 0.00
            a_cargo_os = float(row.iloc[11]) if len(row) > 11 and not pd.isna(row.iloc[11]) else 0.00
            bonificacion = float(row.iloc[12]) if len(row) > 12 and not pd.isna(row.iloc[12]) else 0.00
            nota_credito = float(row.iloc[13]) if len(row) > 13 and not pd.isna(row.iloc[13]) else 0.00
            subtotal_pagar = float(row.iloc[18]) if len(row) > 18 and not pd.isna(row.iloc[18]) else 0.00
            
            # Nuevos campos - columnas O, P, Q, R (índices 14, 15, 16, 17)
            debitos = float(row.iloc[14]) if len(row) > 14 and not pd.isna(row.iloc[14]) else 0.00  # Columna O
            credito = float(row.iloc[15]) if len(row) > 15 and not pd.isna(row.iloc[15]) else 0.00  # Columna P
            gastos_debitos = float(row.iloc[16]) if len(row) > 16 and not pd.isna(row.iloc[16]) else 0.00  # Columna Q
            recuperacion_gastos = float(row.iloc[17]) if len(row) > 17 and not pd.isna(row.iloc[17]) else 0.00  # Columna R

            farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

            # Buscar el usuario por id_facaf
            codigo = str(codigo_farmacia).strip().upper()
            usuario = User.objects.filter(id_facaf=codigo).first()

            LiquidacionOspil.objects.create(
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
                debitos=debitos,
                credito=credito,
                gastos_debitos=gastos_debitos,
                recuperacion_gastos=recuperacion_gastos,
                archivo_origen=archivo_origen,
                user=usuario  # 👈 Relación con usuario mediante id_facaf
            )

            registros_creados += 1
            
        except (IndexError, KeyError, ValueError, TypeError) as e:
            # Si hay algún error al procesar la fila, la saltamos
            print(f"Error procesando fila: {e}")
            continue

    return registros_creados


def procesar_liquidacion_pami(archivo_xlsx, archivo_origen):
    """
    Función para procesar un archivo XLSX de liquidación PAMI y guardarlo en la base de datos.
    """
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]  # Seleccionamos la primera hoja
    df = xls.parse(hoja, header=4)  # Usar la fila 5 como encabezado

    # Debug: mostrar nombres de columna y primeras filas
    print('Columnas detectadas:', list(df.columns))
    print('Primeras filas del DataFrame:')
    print(df.head(3))

    # Normalizar nombres de columna para evitar problemas de tildes y espacios
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('%', 'pct').str.replace('.', '').str.replace('á', 'a').str.replace('é', 'e').str.replace('í', 'i').str.replace('ó', 'o').str.replace('ú', 'u').str.replace('ñ', 'n')
    print('Columnas normalizadas:', list(df.columns))

    registros_creados = 0

    for index, row in df.iterrows():
        # Solo mostrar prints de depuración para las primeras filas
        if index < 5:
            print(f'\nProcesando fila {index}:')
            print('Row:', row)
            print('Row type:', type(row))

        # Saltar filas vacías o de totales
        if pd.isna(row.iloc[14]) or pd.isna(row.iloc[15]) or pd.isna(row.iloc[16]):
            continue

        try:
            importe_100 = float(row.iloc[14]) if not pd.isna(row.iloc[14]) else 0.00
            a_cargo_os = float(row.iloc[15]) if not pd.isna(row.iloc[15]) else 0.00
            bonificacion = float(row.iloc[16]) if not pd.isna(row.iloc[16]) else 0.00
            nota_credito = float(row.iloc[17]) if not pd.isna(row.iloc[17]) else 0.00
            debitos = float(row.iloc[18]) if not pd.isna(row.iloc[18]) else 0.00
            creditos = float(row.iloc[19]) if not pd.isna(row.iloc[19]) else 0.00
            inst_pago_drogueria = float(row.iloc[20]) if not pd.isna(row.iloc[20]) else 0.00
            recuperacion_gastos = float(row.iloc[21]) if not pd.isna(row.iloc[21]) else 0.00
            subtotal_pagar = float(row.iloc[22]) if not pd.isna(row.iloc[22]) else 0.00
        except Exception as e:
            print(f'Error accediendo a columnas por posición en fila {index}: {e}')
            continue

        # Extraer datos de farmacia
        codigo_farmacia = str(row.get('nrf_farmapami', '')).strip() if 'nrf_farmapami' in row else ''
        nombre_farmacia = str(row.get('ccdf_farmalink', '')).strip() if 'ccdf_farmalink' in row else ''
        plan = str(row.get('plan', '')) if 'plan' in row else ''

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)
        codigo = codigo_farmacia.strip().upper()
        usuario = User.objects.filter(id_facaf=codigo).first()

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
            debitos=debitos,
            creditos=creditos,
            inst_pago_drogueria=inst_pago_drogueria,
            recuperacion_gastos=recuperacion_gastos,
            subtotal_pagar=subtotal_pagar,
            archivo_origen=archivo_origen,
            user=usuario  
        )

        registros_creados += 1

    return registros_creados

def procesar_liquidacion_pami_oncologico(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, header=4)

    registros_creados = 0

    for index, row in df.iterrows():
        if pd.isna(row.iloc[0]) or pd.isna(row.iloc[2]) or pd.isna(row.iloc[9]):
            continue

        codigo_farmacia = str(row.iloc[0]).strip()
        nombre_farmacia = str(row.iloc[2]).strip()
        plan = str(row.iloc[3]).strip()

        importe_100 = float(row.iloc[9]) if not pd.isna(row.iloc[9]) else 0.00
        a_cargo_os = float(row.iloc[10]) if not pd.isna(row.iloc[10]) else 0.00
        bonificacion = float(row.iloc[11]) if not pd.isna(row.iloc[11]) else 0.00
        nota_credito = float(row.iloc[12]) if not pd.isna(row.iloc[12]) else 0.00
        subtotal_pagar = float(row.iloc[17]) if not pd.isna(row.iloc[17]) else 0.00

        debitos = float(row.iloc[13]) if len(row) > 13 and not pd.isna(row.iloc[13]) else 0.00
        ajustes = float(row.iloc[14]) if len(row) > 14 and not pd.isna(row.iloc[14]) else 0.00
        recuperacion_ajustes = float(row.iloc[15]) if len(row) > 15 and not pd.isna(row.iloc[15]) else 0.00
        recuperacion_gastos = float(row.iloc[16]) if len(row) > 16 and not pd.isna(row.iloc[16]) else 0.00

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)
        codigo = str(codigo_farmacia).strip().upper()
        usuario = User.objects.filter(id_facaf=codigo).first()

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
            debitos=debitos,
            ajustes=ajustes,
            recuperacion_ajustes=recuperacion_ajustes,
            recuperacion_gastos=recuperacion_gastos,
            archivo_origen=archivo_origen,
            user=usuario
        )
        registros_creados += 1
    return registros_creados

def procesar_liquidacion_pami_panales(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, header=4)

    registros_creados = 0
    plan_actual = ""

    for index, row in df.iterrows():
        if isinstance(row[0], str) and "PLAN:" in row[0].upper():
            plan_actual = row[0].split("PLAN:")[-1].strip()
            continue

        if pd.isna(row[0]) or pd.isna(row[2]) or pd.isna(row[9]):
            continue

        codigo_farmacia = str(row[0]).strip()
        nombre_farmacia = str(row[2]).strip()

        importe_100 = float(row[10]) if not pd.isna(row[10]) else 0.00
        a_cargo_os = float(row[11]) if not pd.isna(row[11]) else 0.00
        bonificacion = float(row[12]) if not pd.isna(row[12]) else 0.00
        nota_credito = float(row[13]) if not pd.isna(row[13]) else 0.00
        subtotal_pagar = float(row[19]) if not pd.isna(row[19]) else 0.00

        debitos = float(row[14]) if len(row) > 14 and not pd.isna(row[14]) else 0.00
        ajustes = float(row[15]) if len(row) > 15 and not pd.isna(row[15]) else 0.00
        recuperacion_ajustes = float(row[16]) if len(row) > 16 and not pd.isna(row[16]) else 0.00
        recuperacion_gastos = float(row[17]) if len(row) > 17 and not pd.isna(row[17]) else 0.00

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)
        codigo = str(codigo_farmacia).strip().upper()
        usuario = User.objects.filter(id_facaf=codigo).first()

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
            debitos=debitos,
            ajustes=ajustes,
            recuperacion_ajustes=recuperacion_ajustes,
            recuperacion_gastos=recuperacion_gastos,
            archivo_origen=archivo_origen,
            user=usuario
        )
        registros_creados += 1
    return registros_creados

def procesar_liquidacion_pami_vacunas(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, header=4)

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

        debitos = float(row[13]) if len(row) > 13 and not pd.isna(row[13]) else 0.00
        ajustes = float(row[14]) if len(row) > 14 and not pd.isna(row[14]) else 0.00
        recuperacion_ajustes = float(row[15]) if len(row) > 15 and not pd.isna(row[15]) else 0.00
        recuperacion_gastos = float(row[16]) if len(row) > 16 and not pd.isna(row[16]) else 0.00

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)
        codigo = str(codigo_farmacia).strip().upper()
        usuario = User.objects.filter(id_facaf=codigo).first()

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
            debitos=debitos,
            ajustes=ajustes,
            recuperacion_ajustes=recuperacion_ajustes,
            recuperacion_gastos=recuperacion_gastos,
            archivo_origen=archivo_origen,
            user=usuario
        )
        registros_creados += 1
    return registros_creados


def procesar_liquidacion_jerarquicos(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=7)

    registros_creados = 0

    for index, row in df.iterrows():
        try:
            # Verificar que existan las columnas mínimas necesarias de forma segura
            if len(row) < 3:
                continue
                
            # Verificar que las columnas básicas no sean nulas
            if pd.isna(row.iloc[0]) or pd.isna(row.iloc[2]) or pd.isna(row.iloc[4]):
                continue

            codigo_farmacia = str(row.iloc[0]).strip()
            nombre_farmacia = str(row.iloc[2]).strip()
            plan = str(row.iloc[3]).strip() if len(row) > 3 and not pd.isna(row.iloc[3]) else "JERARQUICOS"

            # Campos financieros básicos - acceso seguro
            importe_100 = float(row.iloc[10]) if len(row) > 10 and not pd.isna(row.iloc[10]) else 0.00
            a_cargo_os = float(row.iloc[11]) if len(row) > 11 and not pd.isna(row.iloc[11]) else 0.00
            bonificacion = float(row.iloc[12]) if len(row) > 12 and not pd.isna(row.iloc[12]) else 0.00
            nota_credito = float(row.iloc[13]) if len(row) > 13 and not pd.isna(row.iloc[13]) else 0.00
            subtotal_pagar = float(row.iloc[18]) if len(row) > 18 and not pd.isna(row.iloc[18]) else 0.00
            
            # Nuevos campos - columnas O, P, Q, R (índices 14, 15, 16, 17)
            debitos = float(row.iloc[14]) if len(row) > 14 and not pd.isna(row.iloc[14]) else 0.00  # Columna O
            credito = float(row.iloc[15]) if len(row) > 15 and not pd.isna(row.iloc[15]) else 0.00  # Columna P
            gastos_debitos = float(row.iloc[16]) if len(row) > 16 and not pd.isna(row.iloc[16]) else 0.00  # Columna Q
            recuperacion_gastos = float(row.iloc[17]) if len(row) > 17 and not pd.isna(row.iloc[17]) else 0.00  # Columna R

            farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

            # Buscar el usuario por id_facaf
            codigo = str(codigo_farmacia).strip().upper()
            usuario = User.objects.filter(id_facaf=codigo).first()

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
                debitos=debitos,
                credito=credito,
                gastos_debitos=gastos_debitos,
                recuperacion_gastos=recuperacion_gastos,
                archivo_origen=archivo_origen,
                user=usuario  # 👈 Relación correcta
            )

            registros_creados += 1
            
        except (IndexError, KeyError, ValueError, TypeError) as e:
            # Si hay algún error al procesar la fila, la saltamos
            print(f"Error procesando fila: {e}")
            continue

    return registros_creados

def procesar_liquidacion_osfatlyf(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    df = xls.parse(xls.sheet_names[0], skiprows=4)  # Fila 5 contiene los títulos

    registros_creados = 0

    for index, row in df.iterrows():
        try:
            # Validación de campos clave
            if len(row) < 3 or pd.isna(row.iloc[0]) or pd.isna(row.iloc[2]):
                continue

            codigo_farmacia = str(row.iloc[0]).strip()
            nombre_farmacia = str(row.iloc[2]).strip()  # Columna C = nombre de farmacia
            plan = "OSFATLYF"
            fecha_liquidacion = now().date()

            importe_100 = float(row.iloc[9]) if len(row) > 9 and not pd.isna(row.iloc[9]) else 0.00  # Columna J = Liquidado total
            a_cargo_os = float(row.iloc[10]) if len(row) > 10 and not pd.isna(row.iloc[10]) else 0.00  # Columna K
            bonificacion = float(row.iloc[11]) if len(row) > 11 and not pd.isna(row.iloc[11]) else 0.00  # Columna L
            nota_credito = float(row.iloc[12]) if len(row) > 12 and not pd.isna(row.iloc[12]) else 0.00  # Columna M

            # Nuevos campos
            debitos = float(row.iloc[13]) if len(row) > 13 and not pd.isna(row.iloc[13]) else 0.00  # Columna N
            ajustes = float(row.iloc[14]) if len(row) > 14 and not pd.isna(row.iloc[14]) else 0.00  # Columna O
            recuperacion_ajustes = float(row.iloc[15]) if len(row) > 15 and not pd.isna(row.iloc[15]) else 0.00  # Columna P
            recuperacion_gastos = float(row.iloc[16]) if len(row) > 16 and not pd.isna(row.iloc[16]) else 0.00  # Columna Q
            subtotal_a_pagar = float(row.iloc[17]) if len(row) > 17 and not pd.isna(row.iloc[17]) else 0.00  # Columna R

            farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

            LiquidacionOsfatlyf.objects.create(
                farmacia=farmacia,
                codigo_farmacia=codigo_farmacia,
                nombre_farmacia=nombre_farmacia,
                plan=plan,
                fecha_liquidacion=fecha_liquidacion,
                importe_100=importe_100,
                a_cargo_os=a_cargo_os,
                bonificacion=bonificacion,
                nota_credito=nota_credito,
                debitos=debitos,
                ajustes=ajustes,
                recuperacion_ajustes=recuperacion_ajustes,
                recuperacion_gastos=recuperacion_gastos,
                subtotal_a_pagar=subtotal_a_pagar,
                archivo_origen=archivo_origen
            )

            registros_creados += 1
        except (IndexError, KeyError, ValueError, TypeError) as e:
            print(f"Error procesando fila: {e}")
            continue

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

        # Nuevos campos
        debitos = float(row[13]) if len(row) > 13 and not pd.isna(row[13]) else 0.00  # N
        ajustes = float(row[14]) if len(row) > 14 and not pd.isna(row[14]) else 0.00  # O
        recuperacion_ajustes = float(row[15]) if len(row) > 15 and not pd.isna(row.iloc[15]) else 0.00  # P
        recuperacion_gastos = float(row.iloc[16]) if len(row) > 16 and not pd.isna(row.iloc[16]) else 0.00  # Q

        farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

        # Buscar el usuario por id_facaf
        codigo = str(codigo_farmacia).strip().upper()
        usuario = User.objects.filter(id_facaf=codigo).first()

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
            debitos=debitos,
            ajustes=ajustes,
            recuperacion_ajustes=recuperacion_ajustes,
            recuperacion_gastos=recuperacion_gastos,
            archivo_origen=archivo_origen,
            user=usuario  # ✅ Relación automática
        )

        registros_creados += 1

    return registros_creados

def procesar_liquidacion_asociart(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=7)

    registros_creados = 0

    for index, row in df.iterrows():
        try:
            if len(row) < 3 or pd.isna(row.iloc[0]) or pd.isna(row.iloc[2]) or pd.isna(row.iloc[9]):
                continue

            codigo_farmacia = str(row.iloc[0]).strip()
            nombre_farmacia = str(row.iloc[2]).strip()
            plan = str(row.iloc[3]).strip() if len(row) > 3 and not pd.isna(row.iloc[3]) else "ASOCIART"

            importe_100 = float(row.iloc[9]) if len(row) > 9 and not pd.isna(row.iloc[9]) else 0.00
            a_cargo_os = float(row.iloc[10]) if len(row) > 10 and not pd.isna(row.iloc[10]) else 0.00
            bonificacion = float(row.iloc[11]) if len(row) > 11 and not pd.isna(row.iloc[11]) else 0.00
            nota_credito = float(row.iloc[12]) if len(row) > 12 and not pd.isna(row.iloc[12]) else 0.00
            subtotal_pagar = float(row.iloc[18]) if len(row) > 18 and not pd.isna(row.iloc[18]) else 0.00

            # Nuevos campos
            debitos = float(row.iloc[13]) if len(row) > 13 and not pd.isna(row.iloc[13]) else 0.00  # Columna N
            ajustes = float(row.iloc[14]) if len(row) > 14 and not pd.isna(row.iloc[14]) else 0.00  # Columna O
            recuperacion_ajustes = float(row.iloc[15]) if len(row) > 15 and not pd.isna(row.iloc[15]) else 0.00  # Columna P
            recuperacion_gastos = float(row.iloc[16]) if len(row) > 16 and not pd.isna(row.iloc[16]) else 0.00  # Columna Q

            farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

            # Buscar el usuario por id_facaf
            codigo = str(codigo_farmacia).strip().upper()
            usuario = User.objects.filter(id_facaf=codigo).first()

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
                debitos=debitos,
                ajustes=ajustes,
                recuperacion_ajustes=recuperacion_ajustes,
                recuperacion_gastos=recuperacion_gastos,
                archivo_origen=archivo_origen,
                user=usuario  # ✅ Relación automática
            )

            registros_creados += 1
        except (IndexError, KeyError, ValueError, TypeError) as e:
            print(f"Error procesando fila: {e}")
            continue

    return registros_creados

def procesar_liquidacion_coloniasuiza(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=7)

    plan_sheet = xls.parse(hoja, skiprows=1, nrows=1)
    plan = str(plan_sheet.iloc[0, 0]).replace("Plan: ", "").strip()

    registros_creados = 0
    for index, row in df.iterrows():
        try:
            if len(row) < 3 or pd.isna(row.iloc[0]) or pd.isna(row.iloc[2]) or pd.isna(row.iloc[9]):
                continue

            codigo_farmacia = str(row.iloc[0]).strip()
            nombre_farmacia = str(row.iloc[2]).strip()

            importe_100 = float(row.iloc[9]) if len(row) > 9 and not pd.isna(row.iloc[9]) else 0.00
            a_cargo_os = float(row.iloc[10]) if len(row) > 10 and not pd.isna(row.iloc[10]) else 0.00
            bonificacion = float(row.iloc[11]) if len(row) > 11 and not pd.isna(row.iloc[11]) else 0.00
            nota_credito = float(row.iloc[12]) if len(row) > 12 and not pd.isna(row.iloc[12]) else 0.00
            subtotal_pagar = float(row.iloc[16]) if len(row) > 16 and not pd.isna(row.iloc[16]) else 0.00

            # Nuevos campos
            debitos = float(row.iloc[13]) if len(row) > 13 and not pd.isna(row.iloc[13]) else 0.00  # Columna N
            ajustes = float(row.iloc[14]) if len(row) > 14 and not pd.isna(row.iloc[14]) else 0.00  # Columna O
            recuperacion_ajustes = float(row.iloc[15]) if len(row) > 15 and not pd.isna(row.iloc[15]) else 0.00  # Columna P
            recuperacion_gastos = float(row.iloc[16]) if len(row) > 16 and not pd.isna(row.iloc[16]) else 0.00  # Columna Q

            farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

            # Buscar el usuario por id_facaf
            codigo = str(codigo_farmacia).strip().upper()
            usuario = User.objects.filter(id_facaf=codigo).first()

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
                debitos=debitos,
                ajustes=ajustes,
                recuperacion_ajustes=recuperacion_ajustes,
                recuperacion_gastos=recuperacion_gastos,
                archivo_origen=archivo_origen,
                user=usuario  # ✅ Relación automática
            )

            registros_creados += 1
        except (IndexError, KeyError, ValueError, TypeError) as e:
            print(f"Error procesando fila: {e}")
            continue

    return registros_creados

def procesar_liquidacion_experta(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=7)

    plan = "01 - AMBULATORIOS 100%"  # Fila 6
    registros_creados = 0

    for index, row in df.iterrows():
        try:
            if len(row) < 3 or pd.isna(row.iloc[0]) or pd.isna(row.iloc[2]) or pd.isna(row.iloc[4]):
                continue

            codigo_farmacia = str(row.iloc[0]).strip()
            nombre_farmacia = str(row.iloc[2]).strip()

            importe_100 = float(row.iloc[9]) if len(row) > 9 and not pd.isna(row.iloc[4]) else 0.00
            a_cargo_os = float(row.iloc[10]) if len(row) > 10 and not pd.isna(row.iloc[9]) else 0.00
            bonificacion = float(row.iloc[11]) if len(row) > 11 and not pd.isna(row.iloc[10]) else 0.00
            nota_credito = float(row.iloc[12]) if len(row) > 12 and not pd.isna(row.iloc[11]) else 0.00
            subtotal_pagar = float(row.iloc[17]) if len(row) > 17 and not pd.isna(row.iloc[17]) else 0.00

            # Nuevos campos
            debitos = float(row.iloc[13]) if len(row) > 13 and not pd.isna(row.iloc[13]) else 0.00  # Columna N
            ajustes = float(row.iloc[14]) if len(row) > 14 and not pd.isna(row.iloc[14]) else 0.00  # Columna O
            recuperacion_ajustes = float(row.iloc[15]) if len(row) > 15 and not pd.isna(row.iloc[15]) else 0.00  # Columna P
            recuperacion_gastos = float(row.iloc[16]) if len(row) > 16 and not pd.isna(row.iloc[16]) else 0.00  # Columna Q

            farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

            # Buscar el usuario por id_facaf
            codigo = str(codigo_farmacia).strip().upper()
            usuario = User.objects.filter(id_facaf=codigo).first()

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
                debitos=debitos,
                ajustes=ajustes,
                recuperacion_ajustes=recuperacion_ajustes,
                recuperacion_gastos=recuperacion_gastos,
                archivo_origen=archivo_origen,
                user=usuario  # ✅ Relación automática
            )

            registros_creados += 1
        except (IndexError, KeyError, ValueError, TypeError) as e:
            print(f"Error procesando fila: {e}")
            continue

    return registros_creados

def procesar_liquidacion_galenoart(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=4)  # Saltar 4 filas para que los datos empiecen en la fila 5

    registros_creados = 0

    for _, row in df.iterrows():
        try:
            # Verificar que existan las columnas mínimas necesarias de forma segura
            if len(row) < 3:
                continue
                
            # Verificar que las columnas básicas no sean nulas
            if pd.isna(row.iloc[0]) or pd.isna(row.iloc[2]):
                continue

            codigo_farmacia = str(row.iloc[0]).strip()
            nombre_farmacia = str(row.iloc[2]).strip()
            plan = str(row.iloc[3]).strip() if len(row) > 3 and not pd.isna(row.iloc[3]) else "GALENO ART"

            # Campos financieros básicos - acceso seguro
            importe_100 = float(row.iloc[9]) if len(row) > 9 and not pd.isna(row.iloc[9]) else 0.00
            a_cargo_os = float(row.iloc[10]) if len(row) > 10 and not pd.isna(row.iloc[10]) else 0.00
            bonificacion = float(row.iloc[11]) if len(row) > 11 and not pd.isna(row.iloc[11]) else 0.00
            nota_credito = float(row.iloc[12]) if len(row) > 12 and not pd.isna(row.iloc[12]) else 0.00
            subtotal_pagar = float(row.iloc[18]) if len(row) > 18 and not pd.isna(row.iloc[18]) else 0.00
            
            # Nuevos campos - columnas O, P, Q, R (índices 14, 15, 16, 17)
            debitos = float(row.iloc[14]) if len(row) > 14 and not pd.isna(row.iloc[14]) else 0.00  # Columna O
            credito = float(row.iloc[15]) if len(row) > 15 and not pd.isna(row.iloc[15]) else 0.00  # Columna P
            gastos_debitos = float(row.iloc[16]) if len(row) > 16 and not pd.isna(row.iloc[16]) else 0.00  # Columna Q
            recuperacion_gastos = float(row.iloc[17]) if len(row) > 17 and not pd.isna(row.iloc[17]) else 0.00  # Columna R

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
                debitos=debitos,
                credito=credito,
                gastos_debitos=gastos_debitos,
                recuperacion_gastos=recuperacion_gastos,
                archivo_origen=archivo_origen,
            )

            registros_creados += 1
            
        except (IndexError, KeyError, ValueError, TypeError) as e:
            # Si hay algún error al procesar la fila, la saltamos
            print(f"Error procesando fila: {e}")
            continue

    return registros_creados

def procesar_liquidacion_prevencion_art(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=7)

    registros_creados = 0

    for index, row in df.iterrows():
        try:
            if len(row) < 3 or pd.isna(row.iloc[0]) or pd.isna(row.iloc[2]) or pd.isna(row.iloc[4]):
                continue

            codigo_farmacia = str(row.iloc[0]).strip()
            nombre_farmacia = str(row.iloc[2]).strip()
            plan = "Plan: 01 - Ambulatorio 100%"

            importe_100 = float(row.iloc[4]) if len(row) > 4 and not pd.isna(row.iloc[4]) else 0.00
            a_cargo_os = float(row.iloc[9]) if len(row) > 9 and not pd.isna(row.iloc[9]) else 0.00
            bonificacion = float(row.iloc[10]) if len(row) > 10 and not pd.isna(row.iloc[10]) else 0.00
            nota_credito = float(row.iloc[11]) if len(row) > 11 and not pd.isna(row.iloc[11]) else 0.00
            subtotal_pagar = float(row.iloc[17]) if len(row) > 17 and not pd.isna(row.iloc[17]) else 0.00

            # Nuevos campos
            debitos = float(row.iloc[13]) if len(row) > 13 and not pd.isna(row.iloc[13]) else 0.00  # Columna N
            ajustes = float(row.iloc[14]) if len(row) > 14 and not pd.isna(row.iloc[14]) else 0.00  # Columna O
            recuperacion_ajustes = float(row.iloc[15]) if len(row) > 15 and not pd.isna(row.iloc[15]) else 0.00  # Columna P
            recuperacion_gastos = float(row.iloc[16]) if len(row) > 16 and not pd.isna(row.iloc[16]) else 0.00  # Columna Q

            farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)

            # Buscar el usuario por id_facaf
            codigo = str(codigo_farmacia).strip().upper()
            usuario = User.objects.filter(id_facaf=codigo).first()

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
                debitos=debitos,
                ajustes=ajustes,
                recuperacion_ajustes=recuperacion_ajustes,
                recuperacion_gastos=recuperacion_gastos,
                archivo_origen=archivo_origen,
                user=usuario  # ✅ Asociación automática
            )

            registros_creados += 1
        except (IndexError, KeyError, ValueError, TypeError) as e:
            print(f"Error procesando fila: {e}")
            continue

    return registros_creados


"""def obtener_transferencias_pami_por_sociedad():

    datos = defaultdict(lambda: {
        "sociedad": None,
        "nombre_fantasia": None,
        "cuit": None,
        "cbu": None,
        "importe_total": 0,
        "comision": 0,
        "total_transferir": 0
    })

    no_asociadas = []

    # Solo analizamos la liquidación más reciente
    ultimo_archivo = (
        LiquidacionPAMI.objects.values_list("archivo_origen", flat=True)
        .order_by("-creado_en")
        .first()
    )

    if not ultimo_archivo:
        return [], []

    liquidaciones = LiquidacionPAMI.objects.filter(archivo_origen=ultimo_archivo)

    for lq in liquidaciones:
        user = getattr(lq, "user", None)

        if user and user.farmacia:
            sociedad = user.farmacia.nombre
            datos[sociedad]["sociedad"] = sociedad
            datos[sociedad]["nombre_fantasia"] = user.username
            datos[sociedad]["cuit"] = user.farmacia.cuit
            datos[sociedad]["cbu"] = user.farmacia.cbu  # Asumimos que drogueria contiene CBU
            datos[sociedad]["importe_total"] += float(lq.subtotal_pagar)
        else:
            no_asociadas.append(lq)

    for item in datos.values():
        item["comision"] = round(item["importe_total"] * 0.0075, 2)
        item["total_transferir"] = round(item["importe_total"] - item["comision"], 2)

    return list(datos.values()), no_asociadas
"""

def obtener_transferencias_por_sociedad():
    """
    Devuelve un diccionario agrupado por obra social,
    y dentro de cada obra social agrupa por sociedad (nombre de Farmacia).
    Excluye Galeno y OSFATLYF.
    """
    from .models import (
        LiquidacionPAMI, LiquidacionJerarquicos, LiquidacionOspil,
        LiquidacionPAMIOncologico, LiquidacionPAMIPanales, LiquidacionPAMIVacunas,
        LiquidacionAndinaART, LiquidacionAsociart, LiquidacionColoniaSuiza,
        LiquidacionExperta, LiquidacionGalenoART, LiquidacionPrevencionART, User, LiquidacionLaSegundaART
    )

    MODELOS = {
        "PAMI": LiquidacionPAMI,
        "Jerárquicos Salud": LiquidacionJerarquicos,
        "OSPIL": LiquidacionOspil,
        "PAMI Oncológico": LiquidacionPAMIOncologico,
        "PAMI Pañales": LiquidacionPAMIPanales,
        "PAMI Vacunas": LiquidacionPAMIVacunas,
        "Andina ART": LiquidacionAndinaART,
        "Asociart": LiquidacionAsociart,
        "Colonia Suiza": LiquidacionColoniaSuiza,
        "Experta ART": LiquidacionExperta,
        "Galeno ART": LiquidacionGalenoART,
        "Prevención ART": LiquidacionPrevencionART,
        "La Segunda ART": LiquidacionLaSegundaART,
    }

    resultado = {}
    no_asociadas_total = {}

    for nombre_obra, Modelo in MODELOS.items():
        datos = defaultdict(lambda: {
            "sociedad": None,
            "nombre_fantasia": None,
            "cuit": None,
            "cbu": None,
            "importe_total": 0,
            "comision": 0,
            "total_transferir": 0
        })
        no_asociadas = []

        # Obtener último archivo cargado
        ultimo_archivo = Modelo.objects.values_list("archivo_origen", flat=True).order_by("-creado_en").first()
        if not ultimo_archivo:
            continue

        registros = Modelo.objects.filter(archivo_origen=ultimo_archivo)

        for lq in registros:
            user = getattr(lq, "user", None)
            if user and user.farmacia:
                sociedad = user.farmacia.nombre
                datos[sociedad]["sociedad"] = sociedad
                datos[sociedad]["nombre_fantasia"] = user.username
                datos[sociedad]["cuit"] = user.farmacia.cuit
                datos[sociedad]["cbu"] = user.farmacia.cbu
                datos[sociedad]["importe_total"] += float(lq.subtotal_pagar)
            else:
                no_asociadas.append(lq)

        for item in datos.values():
            if nombre_obra in ["PAMI Oncológico", "PAMI Vacunas", "PAMI Pañales"]:
                item["comision"] = 0
            else:
                item["comision"] = round(item["importe_total"] * 0.0060, 2)
            item["total_transferir"] = round(item["importe_total"] - item["comision"], 2)


        resultado[nombre_obra] = list(datos.values())
        no_asociadas_total[nombre_obra] = no_asociadas

    return resultado, no_asociadas_total


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


def generate_video_thumbnail(video_path, output_path=None, time_position=1.0):
    """
    Genera un thumbnail de un video usando OpenCV.
    
    Args:
        video_path (str): Ruta al archivo de video
        output_path (str): Ruta donde guardar el thumbnail (opcional)
        time_position (float): Posición en segundos para tomar el frame (default: 1 segundo)
    
    Returns:
        str: Ruta del thumbnail generado
    """
    try:
        # Abrir el video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise Exception("No se pudo abrir el archivo de video")
        
        # Obtener información del video
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calcular el frame a capturar
        frame_position = int(fps * time_position)
        frame_position = min(frame_position, total_frames - 1)  # Asegurar que no exceda el total
        
        # Ir al frame específico
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)
        
        # Leer el frame
        ret, frame = cap.read()
        
        if not ret:
            raise Exception("No se pudo leer el frame del video")
        
        # Liberar el video
        cap.release()
        
        # Convertir de BGR a RGB (OpenCV usa BGR por defecto)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convertir a PIL Image para redimensionar
        pil_image = Image.fromarray(frame_rgb)
        
        # Redimensionar manteniendo proporción
        max_size = (300, 200)
        pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Generar nombre único para el thumbnail
        if output_path is None:
            filename = f"thumbnail_{uuid.uuid4().hex[:8]}.jpg"
            output_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', filename)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Guardar el thumbnail
        pil_image.save(output_path, 'JPEG', quality=85)
        
        return output_path
        
    except Exception as e:
        print(f"Error generando thumbnail: {str(e)}")
        return None

def get_video_info(video_path):
    """
    Obtiene información básica de un video usando OpenCV.
    
    Args:
        video_path (str): Ruta al archivo de video
    
    Returns:
        dict: Información del video (duración, fps, dimensiones)
    """
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None
        
        # Obtener información
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Calcular duración
        duration = total_frames / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            'duration': duration,
            'fps': fps,
            'width': width,
            'height': height,
            'total_frames': total_frames
        }
        
    except Exception as e:
        print(f"Error obteniendo información del video: {str(e)}")
        return None

def generar_thumbnail_para_guia_video(guia_video):
    """
    Genera un thumbnail automático para una guía de video.
    
    Args:
        guia_video: Instancia del modelo GuiaVideo
    
    Returns:
        bool: True si se generó exitosamente, False en caso contrario
    """
    try:
        # Verificar que el video existe
        if not guia_video.archivo_video or not os.path.exists(guia_video.archivo_video.path):
            print(f"El archivo de video no existe: {guia_video.archivo_video.path}")
            return False
        
        video_path = guia_video.archivo_video.path
        
        # Generar el thumbnail
        thumbnail_path = generate_video_thumbnail(video_path)
        
        if thumbnail_path and os.path.exists(thumbnail_path):
            # Guardar el thumbnail en el modelo
            with open(thumbnail_path, 'rb') as thumbnail_file:
                from django.core.files import File
                guia_video.thumbnail.save(
                    os.path.basename(thumbnail_path),
                    File(thumbnail_file),
                    save=True
                )
            
            print(f"Thumbnail generado exitosamente para: {guia_video.titulo}")
            return True
        else:
            print(f"No se pudo generar thumbnail para: {guia_video.titulo}")
            return False
            
    except Exception as e:
        print(f"Error generando thumbnail para {guia_video.titulo}: {str(e)}")
        return False

def regenerar_thumbnails_pendientes():
    """
    Regenera thumbnails para todos los videos que no los tienen.
    Útil para videos subidos antes de implementar la generación automática.
    """
    from .models import GuiaVideo
    
    # Buscar videos sin thumbnail
    videos_sin_thumbnail = GuiaVideo.objects.filter(thumbnail__isnull=True)
    
    if not videos_sin_thumbnail.exists():
        print("No hay videos pendientes de thumbnail.")
        return True
    
    print(f"Encontrados {videos_sin_thumbnail.count()} videos sin thumbnail.")
    
    exitosos = 0
    fallidos = 0
    
    for video in videos_sin_thumbnail:
        try:
            if generar_thumbnail_para_guia_video(video):
                exitosos += 1
                print(f"✓ Thumbnail regenerado para video {video.id}: {video.titulo}")
            else:
                fallidos += 1
                print(f"✗ No se pudo regenerar thumbnail para video {video.id}: {video.titulo}")
        except Exception as e:
            fallidos += 1
            print(f"✗ Error regenerando thumbnail para video {video.id}: {e}")
    
    print(f"Proceso completado: {exitosos} exitosos, {fallidos} fallidos")
    return exitosos > 0

def regenerar_duracion_videos():
    """
    Regenera la duración de todos los videos que tengan duración vacía o 00:00.
    """
    from .models import GuiaVideo
    videos = GuiaVideo.objects.filter(duracion__isnull=True) | GuiaVideo.objects.filter(duracion="") | GuiaVideo.objects.filter(duracion="00:00")
    print(f"Encontrados {videos.count()} videos sin duración o con duración 00:00.")
    exitosos = 0
    for video in videos:
        if video.archivo_video and video.archivo_video.path:
            info = get_video_info(video.archivo_video.path)
            if info and info['duration']:
                total_seconds = int(info['duration'])
                minutos = total_seconds // 60
                segundos = total_seconds % 60
                video.duracion = f"{minutos:02d}:{segundos:02d}"
                video.save(update_fields=["duracion"])
                exitosos += 1
                print(f"✓ Duración actualizada para video {video.id}: {video.titulo} -> {video.duracion}")
            else:
                print(f"✗ No se pudo calcular duración para video {video.id}: {video.titulo}")
    print(f"Proceso completado: {exitosos} videos actualizados.")
    return exitosos > 0


def procesar_liquidacion_lasegundaart(archivo_xlsx, archivo_origen):
    xls = pd.ExcelFile(archivo_xlsx)
    hoja = xls.sheet_names[0]
    df = xls.parse(hoja, skiprows=4)  # Saltar 4 filas para que los datos empiecen en la fila 5

    registros_creados = 0

    # Debug: mostrar las primeras filas leídas
    print("Primeras filas del DataFrame:")
    print(df.head(10))

    for idx, row in df.iterrows():
        try:
            # Solo procesar filas que tengan datos numéricos en la columna J (índice 9)
            if len(row) < 18:
                print(f"Fila {idx} saltada: menos de 18 columnas")
                continue
            if pd.isna(row.iloc[9]) or not isinstance(row.iloc[9], (int, float)):
                print(f"Fila {idx} saltada: columna J vacía o no numérica")
                continue

            # Extraer valores de J a R (índices 9 a 17)
            importe_100 = float(row.iloc[9]) if not pd.isna(row.iloc[9]) and isinstance(row.iloc[9], (int, float)) else 0.00
            a_cargo_os = float(row.iloc[10]) if not pd.isna(row.iloc[10]) and isinstance(row.iloc[10], (int, float)) else 0.00
            bonificacion = float(row.iloc[11]) if not pd.isna(row.iloc[11]) and isinstance(row.iloc[11], (int, float)) else 0.00
            nota_credito = float(row.iloc[12]) if not pd.isna(row.iloc[12]) and isinstance(row.iloc[12], (int, float)) else 0.00
            debitos = float(row.iloc[13]) if not pd.isna(row.iloc[13]) and isinstance(row.iloc[13], (int, float)) else 0.00
            credito = float(row.iloc[14]) if not pd.isna(row.iloc[14]) and isinstance(row.iloc[14], (int, float)) else 0.00
            gastos_debitos = float(row.iloc[15]) if not pd.isna(row.iloc[15]) and isinstance(row.iloc[15], (int, float)) else 0.00
            recuperacion_gastos = float(row.iloc[16]) if not pd.isna(row.iloc[16]) and isinstance(row.iloc[16], (int, float)) else 0.00
            subtotal_pagar = float(row.iloc[17]) if not pd.isna(row.iloc[17]) and isinstance(row.iloc[17], (int, float)) else 0.00

            # Extraer datos de farmacia y plan
            codigo_farmacia = str(row.iloc[0]).strip() if not pd.isna(row.iloc[0]) else ""
            nombre_farmacia = str(row.iloc[2]).strip() if not pd.isna(row.iloc[2]) else ""
            plan = "LA SEGUNDA ART"

            if not codigo_farmacia or not nombre_farmacia:
                print(f"Fila {idx} saltada: código o nombre de farmacia vacío")
                continue

            farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia)
            codigo = codigo_farmacia.strip().upper()
            usuario = User.objects.filter(id_facaf=codigo).first()

            LiquidacionLaSegundaART.objects.create(
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
                debitos=debitos,
                credito=credito,
                gastos_debitos=gastos_debitos,
                recuperacion_gastos=recuperacion_gastos,
                archivo_origen=archivo_origen,
                user=usuario
            )
            registros_creados += 1
        except Exception as e:
            print(f"Error procesando fila {idx}: {e}")
            continue
    print(f"Total de registros creados: {registros_creados}")
    return registros_creados


def procesar_liquidacion_osdipp_pdf(archivo_pdf, archivo_origen):
    """
    Procesa un PDF de liquidación OSDIPP, asociando cada bloque de datos a la farmacia de la última fila 'Fcia:',
    tomando las siguientes 2-3 filas de datos (ignorando vacías) y, para cada columna, buscando hacia abajo el primer valor no vacío.
    Así se guarda un solo registro por farmacia, robusto ante desplazamientos verticales.
    """
    import re
    registros_creados = 0
    nombre_farmacia = ''
    codigo_farmacia = ''
    with pdfplumber.open(archivo_pdf) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table_num, table in enumerate(tables):
                if not table or len(table) < 3:
                    continue
                cabecera_idx = None
                for idx, fila in enumerate(table):
                    if fila and any(isinstance(cell, str) and 'Recetas' in cell for cell in fila):
                        cabecera_idx = idx
                        break
                if cabecera_idx is None or cabecera_idx+1 >= len(table):
                    continue
                i = cabecera_idx + 1
                while i < len(table):
                    row = table[i]
                    if not row or not row[0]:
                        i += 1
                        continue
                    # Detectar fila de farmacia
                    if isinstance(row[0], str) and row[0].strip().startswith('Fcia:'):
                        match = re.match(r'Fcia:\s*(\d+)\s*(.*)', row[0].strip())
                        if match:
                            codigo_farmacia = match.group(1)
                            nombre_farmacia = match.group(2).strip()
                        else:
                            codigo_farmacia = ''
                            nombre_farmacia = ''
                        # Buscar las siguientes 3 filas de datos (ignorando vacías)
                        datos_filas = []
                        j = i + 1
                        while j < len(table) and len(datos_filas) < 3:
                            datos = table[j]
                            if datos and any(cell not in [None, '', ' '] for cell in datos):
                                datos_filas.append(datos)
                            j += 1
                        # Para cada columna, buscar hacia abajo el primer valor no vacío
                        num_cols = max(len(f) for f in datos_filas) if datos_filas else 0
                        valores = []
                        for col in range(num_cols):
                            val = None
                            for fila in datos_filas:
                                if len(fila) > col and fila[col] not in [None, '', ' ']:
                                    val = fila[col]
                                    break
                            valores.append(val)
                        try:
                            from core.models import Farmacia, User
                            farmacia, _ = Farmacia.objects.get_or_create(nombre=nombre_farmacia or codigo_farmacia)
                            codigo = codigo_farmacia.strip().upper()
                            usuario = User.objects.filter(id_facaf=codigo).first()
                            def parse_float(val):
                                try:
                                    return float(str(val).replace('.', '').replace(',', '.').strip() or 0)
                                except: return 0.0
                            def parse_int(val):
                                try:
                                    return int(str(val).replace('.', '').replace(',', '').strip() or 0)
                                except: return 0
                            recetas_presentadas = parse_int(valores[0]) if len(valores) > 0 else 0
                            importe_total_presentado = parse_float(valores[1]) if len(valores) > 1 else 0.0
                            importe_entregado_presentado = parse_float(valores[2]) if len(valores) > 2 else 0.0
                            recetas_aceptadas = parse_int(valores[3]) if len(valores) > 3 else 0
                            importe_total_aceptado = parse_float(valores[4]) if len(valores) > 4 else 0.0
                            importe_entregado_aceptado = parse_float(valores[5]) if len(valores) > 5 else 0.0
                            aporte_farmacia = parse_float(valores[6]) if len(valores) > 6 else 0.0
                            gastos_auditoria = parse_float(valores[7]) if len(valores) > 7 else 0.0
                            importe_neto = parse_float(valores[8]) if len(valores) > 8 else 0.0
                            gastos_recs = parse_float(valores[9]) if len(valores) > 9 else 0.0
                            ajustes_anteriores = parse_float(valores[10]) if len(valores) > 10 else 0.0
                            ajuste_credito_anticipado = parse_float(valores[11]) if len(valores) > 11 else 0.0
                            importe_a_pagar = parse_float(valores[12]) if len(valores) > 12 else 0.0
                            importe_efectivo = parse_float(valores[16]) if len(valores) > 16 else 0.0
                            ajustes_posteriores = parse_float(valores[17]) if len(valores) > 17 else 0.0
                            from django.utils.timezone import now
                            fecha_liquidacion = now().date()
                            from core.models import LiquidacionOSDIPP
                            LiquidacionOSDIPP.objects.create(
                                farmacia=farmacia,
                                codigo_farmacia=codigo_farmacia,
                                nombre_farmacia=nombre_farmacia,
                                plan="OSDIPP",
                                fecha_liquidacion=fecha_liquidacion,
                                recetas_presentadas=recetas_presentadas,
                                importe_total_presentado=importe_total_presentado,
                                importe_entregado_presentado=importe_entregado_presentado,
                                recetas_aceptadas=recetas_aceptadas,
                                importe_total_aceptado=importe_total_aceptado,
                                importe_entregado_aceptado=importe_entregado_aceptado,
                                aporte_farmacia=aporte_farmacia,
                                gastos_auditoria=gastos_auditoria,
                                importe_neto=importe_neto,
                                gastos_recs=gastos_recs,
                                ajustes_anteriores=ajustes_anteriores,
                                ajuste_credito_anticipado=ajuste_credito_anticipado,
                                importe_a_pagar=importe_a_pagar,
                                importe_efectivo=importe_efectivo,
                                ajustes_posteriores=ajustes_posteriores,
                                archivo_origen=archivo_origen,
                                user=usuario
                            )
                            registros_creados += 1
                            print(f"[OSDIPP] Guardado: {nombre_farmacia} ({codigo_farmacia}) - {valores}")
                        except Exception as e:
                            print(f"Error procesando fila de datos para {nombre_farmacia}: {e}")
                        i = j  # Saltar a la siguiente farmacia
                    else:
                        i += 1
    print(f"[OSDIPP] Total de registros creados: {registros_creados}")
    return registros_creados
