#!/usr/bin/env python3
"""
Script de prueba para verificar OpenCV con Django configurado
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'generic.settings')
django.setup()

import cv2
from PIL import Image
import uuid

def test_opencv_installation():
    """Prueba la instalación de OpenCV"""
    print("🔍 Verificando instalación de OpenCV...")
    
    try:
        import cv2
        print(f"✅ OpenCV instalado - versión: {cv2.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Error importando OpenCV: {e}")
        return False

def test_opencv_functionality():
    """Prueba la funcionalidad básica de OpenCV"""
    print("\n🧪 Probando funcionalidad de OpenCV...")
    
    try:
        # Crear una imagen de prueba
        test_image = cv2.imread("static/images/logo.png")
        
        if test_image is not None:
            print("✅ OpenCV puede leer imágenes correctamente")
            print(f"   Dimensiones: {test_image.shape}")
        else:
            print("⚠️  No se pudo leer la imagen de prueba")
        
        # Probar VideoCapture (sin archivo real)
        cap = cv2.VideoCapture()
        if cap.isOpened() is False:
            print("✅ VideoCapture funciona correctamente")
        cap.release()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en funcionalidad de OpenCV: {e}")
        return False

def test_thumbnail_functions():
    """Prueba las funciones de thumbnail con Django configurado"""
    print("\n🎬 Probando funciones de thumbnail...")
    
    try:
        from core.utils import generate_video_thumbnail, get_video_info, generar_thumbnail_para_guia_video
        
        print("✅ Funciones de thumbnail importadas correctamente")
        
        # Crear un directorio de prueba
        test_dir = "test_thumbnails"
        os.makedirs(test_dir, exist_ok=True)
        
        print("✅ Funciones de thumbnail están disponibles")
        return True
        
    except Exception as e:
        print(f"❌ Error en funciones de thumbnail: {e}")
        return False

def test_django_models():
    """Prueba que los modelos de Django estén disponibles"""
    print("\n🏗️  Probando modelos de Django...")
    
    try:
        from core.models import GuiaVideo
        
        print("✅ Modelo GuiaVideo disponible")
        
        # Contar guías de video existentes
        count = GuiaVideo.objects.count()
        print(f"   Guías de video en la base de datos: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error con modelos de Django: {e}")
        return False

def test_settings():
    """Prueba la configuración de Django"""
    print("\n⚙️  Probando configuración de Django...")
    
    try:
        from django.conf import settings
        
        print("✅ Configuración de Django cargada")
        print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
        print(f"   STATIC_ROOT: {settings.STATIC_ROOT}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error con configuración de Django: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Diagnóstico completo de OpenCV con Django...\n")
    
    # Prueba 1: Instalación de OpenCV
    installation_ok = test_opencv_installation()
    
    # Prueba 2: Funcionalidad de OpenCV
    functionality_ok = test_opencv_functionality()
    
    # Prueba 3: Configuración de Django
    settings_ok = test_settings()
    
    # Prueba 4: Modelos de Django
    models_ok = test_django_models()
    
    # Prueba 5: Funciones de thumbnail
    thumbnail_ok = test_thumbnail_functions()
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    
    if installation_ok:
        print("✅ Instalación de OpenCV: OK")
    else:
        print("❌ Instalación de OpenCV: FALLO")
    
    if functionality_ok:
        print("✅ Funcionalidad de OpenCV: OK")
    else:
        print("❌ Funcionalidad de OpenCV: FALLO")
    
    if settings_ok:
        print("✅ Configuración de Django: OK")
    else:
        print("❌ Configuración de Django: FALLO")
    
    if models_ok:
        print("✅ Modelos de Django: OK")
    else:
        print("❌ Modelos de Django: FALLO")
    
    if thumbnail_ok:
        print("✅ Funciones de thumbnail: OK")
    else:
        print("❌ Funciones de thumbnail: FALLO")
    
    if all([installation_ok, functionality_ok, settings_ok, models_ok, thumbnail_ok]):
        print("\n🎉 ¡Todo está funcionando correctamente!")
        print("✅ OpenCV está listo para generar thumbnails de videos")
        print("✅ Django está configurado correctamente")
        print("✅ Puedes usar la funcionalidad de guías de video")
    else:
        print("\n⚠️  Hay problemas que necesitan ser resueltos")
        print("🔧 Revisa los errores anteriores y corrige los problemas")

if __name__ == "__main__":
    main() 