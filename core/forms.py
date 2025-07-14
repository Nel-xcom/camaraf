from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.forms import UserCreationForm
from .models import Farmacia, User, CargaDatos
from .models import GuiaVideo, GuiaArchivo

class FarmaciaRegisterForm(UserCreationForm):
    nombre = forms.CharField(max_length=255)
    direccion = forms.CharField(max_length=255)
    ciudad = forms.CharField(max_length=100)
    provincia = forms.CharField(max_length=100)
    contacto_principal = forms.CharField(max_length=255)
    email_contacto = forms.EmailField()
    telefono_contacto = forms.CharField(max_length=15)
    cuit = forms.CharField(max_length=15)
    drogueria = forms.CharField(max_length=255)
    cbu = forms.CharField(max_length=55, required=False)

    class Meta:
        model = User
        fields = ['id_facaf', 'cbu', 'username', 'email', 'password1', 'password2', 
                  'nombre', 'direccion', 'ciudad', 'provincia', 
                  'contacto_principal', 'email_contacto', 
                  'telefono_contacto', 'cuit', 'drogueria']

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Usuario'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contraseña'
    }))

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Correo electrónico'
    }))

class CargaDatosForm(forms.ModelForm):
    class Meta:
        model = CargaDatos
        fields = '__all__'

class CargaDatosFormOSDIPP(forms.ModelForm):
    class Meta:
        model = CargaDatos
        fields = [
            'numero_presentacion', 'periodo', 'cantidad_lotes', 'cantidad_recetas', 'importe_100', 'importe_a_cargo'
        ]

class CargaDatosFormPAMI(forms.ModelForm):
    class Meta:
        model = CargaDatos
        fields = [
            'numero_presentacion', 'periodo', 'cantidad_lotes', 'cantidad_recetas', 'total_pvp', 'total_pvp_pami', 'importe_bruto_convenio'
        ]
        labels = {
            'numero_presentacion': 'Número de carátula'
        }

class CargaDatosFormAvalian(forms.ModelForm):
    class Meta:
        model = CargaDatos
        fields = [
            'periodo', 'cantidad_recetas', 'importe_100', 'importe_a_cargo'
        ]

class LiquidacionGalenoForm(forms.Form):
    archivo = forms.FileField(label="Seleccione un archivo XLSX")

class LiquidacionPAMIForm(forms.Form):
    archivo = forms.FileField(label="Seleccione un archivo XLSX")

class LiquidacionJerarquicosForm(forms.Form):
    archivo = forms.FileField(label="Seleccione un archivo XLSX")

class LiquidacionOsfatlyfForm(forms.Form):
    archivo = forms.FileField(label="Seleccione un archivo XLSX")

class LiquidacionAsociartForm(forms.Form):
    archivo = forms.FileField(label="Seleccione un archivo XLSX")

class LiquidacionPrevencionARTForm(forms.Form):
    archivo = forms.FileField(label="Seleccione un archivo XLSX")


class GuiaVideoForm(forms.ModelForm):
    """
    Formulario para subir videos de guías
    """
    class Meta:
        model = GuiaVideo
        fields = ['titulo', 'descripcion', 'categoria', 'estado', 'archivo_video']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del video'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del video (opcional)',
                'rows': 3
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            }),
            'archivo_video': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*'
            })
        }
    
    def clean_archivo_video(self):
        archivo = self.cleaned_data.get('archivo_video')
        if archivo:
            # Validar tamaño máximo (500MB)
            if archivo.size > 500 * 1024 * 1024:
                raise forms.ValidationError("El archivo es demasiado grande. El tamaño máximo es 500MB.")
            
            # Validar extensiones permitidas
            extensiones_permitidas = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']
            extension = archivo.name.lower()
            if not any(extension.endswith(ext) for ext in extensiones_permitidas):
                raise forms.ValidationError("Formato de video no soportado. Use MP4, AVI, MOV, WMV, FLV, MKV o WEBM.")
        
        return archivo
    



class GuiaArchivoForm(forms.ModelForm):
    """
    Formulario para subir archivos de guías
    """
    class Meta:
        model = GuiaArchivo
        fields = ['titulo', 'descripcion', 'categoria', 'estado', 'archivo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del archivo'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del archivo (opcional)',
                'rows': 3
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
    
    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Validar tamaño máximo (50MB)
            if archivo.size > 50 * 1024 * 1024:
                raise forms.ValidationError("El archivo es demasiado grande. El tamaño máximo es 50MB.")
            
            # Validar extensiones permitidas
            extensiones_permitidas = [
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
                '.ppt', '.pptx', '.txt', '.rtf'
            ]
            extension = archivo.name.lower()
            if not any(extension.endswith(ext) for ext in extensiones_permitidas):
                raise forms.ValidationError(
                    "Formato de archivo no soportado. Use PDF, Word, Excel, PowerPoint o texto."
                )
        
        return archivo