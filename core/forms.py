from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.forms import UserCreationForm
from .models import Farmacia, User, CargaDatos

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

    class Meta:
        model = User
        fields = ['id_facaf', 'username', 'email', 'password1', 'password2', 
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