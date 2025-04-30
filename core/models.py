from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Farmacia(models.Model):
    codigo_farmacia = models.CharField(max_length=20, help_text="Código de la farmacia", default="F000")
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    contacto_principal = models.CharField(max_length=255)
    email_contacto = models.EmailField()
    telefono_contacto = models.CharField(max_length=15)
    cuit = models.CharField(max_length=15)
    cbu = models.CharField(max_length=55, default="000000000000000")
    drogueria = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

class User(AbstractUser):
    farmacia = models.OneToOneField(
        Farmacia,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    id_facaf = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="ID único provisto por FACAF para identificación cruzada"
    )

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

class CargaDatos(models.Model):
    OBRAS_SOCIALES = [
        ('OSDIPP', 'OSDIPP'),
        ('SWISS_MEDICAL', 'Swiss Medical'),
        ('GALENO', 'Galeno'),
        ('Ospilampil', 'OspilAmpil'),
        ('Osfatlyf', 'Osfatlyf'),
        ('Jerarquicos', 'Jerarquicos Salud'),
        ('PAMI', 'PAMI'),
        ('PAMI_ONCOLOGICO', 'PAMI Oncológico'),
        ('PAMI_VACUNAS', 'PAMI Vacunas'),
        ('PAMI_PAÑALES', 'PAMI Pañales'),
        ('AVALIAN', 'Avalian'),
        ('Andrina_ART', 'Andina ART'),
        ('Asociart_ART', 'Asociart ART'),
        ('Coloniasuiza', 'Colonia Suiza'),
        ('experta_ART', 'Experta ART'),
        ('Galeno_ART', 'Galeno ART'),
        ('LaSegunda_ART', 'La Segunda ART'),
        ('Prevencion_ART', 'Prevencion ART')
    ]

    ESTADOS = [
        ('Enviada', 'Enviada'),
        ('Recibida', 'Recibida'),
        ('Presentada', 'Presentada'),
        ('Liquidada', 'Liquidada')
    ]

    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE)
    obra_social = models.CharField(max_length=50, choices=OBRAS_SOCIALES, blank=False)
    periodo = models.DateField(max_length=20, blank=False)
    numero_presentacion = models.CharField(max_length=50, null=True, blank=False)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Enviada', blank=False)
    cantidad_lotes = models.IntegerField(null=True, blank=False)
    cantidad_recetas = models.IntegerField(null=True, blank=False)
    importe_100 = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=False)
    importe_a_cargo = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=False)
    total_pvp = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=False)
    total_pvp_pami = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=False)
    importe_bruto_convenio = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=False)
    codigo_facaf = models.CharField(max_length=20, null=True, blank=False)
    codigo_farmalink = models.CharField(max_length=20, null=True, blank=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=False)

    def __str__(self):
        return f"{self.obra_social} - {self.periodo}"


class Presentacion(models.Model):
    OBRAS_SOCIALES = [
        ('OSDIPP', 'OSDIPP'),
        ('SWISS_MEDICAL', 'Swiss Medical'),
        ('GALENO', 'Galeno'),
        ('FARMALINK', 'Farmalink'),
        ('PAMI', 'PAMI'),
        ('AVALIAN', 'Avalian')
    ]

    QUINCENAS = [
        ('1', 'Primera'),
        ('2', 'Segunda'),
        ('mensual', 'Mensual')
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField()
    obra_social = models.CharField(max_length=50, choices=OBRAS_SOCIALES)
    quincena = models.CharField(max_length=40, choices=QUINCENAS)

    def __str__(self):
        return f"{self.obra_social} - {self.fecha}"
    
class Liquidacion(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE)
    obra_social = models.CharField(max_length=50)
    periodo = models.CharField(max_length=20)
    cantidad_recetas = models.IntegerField()
    importe_100 = models.DecimalField(max_digits=10, decimal_places=2)
    importe_a_cargo = models.DecimalField(max_digits=10, decimal_places=2)
    total_pvp = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_carga = models.DateTimeField(auto_now_add=True)

    archivo_origen = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.obra_social} - {self.periodo}"
    
class LiquidacionGaleno(models.Model):
    prestador = models.CharField(max_length=255)  # Nombre y código del prestador
    fecha = models.DateField()  # Fecha de liquidación
    orden_de_pago = models.CharField(max_length=50, unique=True)  # Número de orden de pago
    importe = models.DecimalField(max_digits=15, decimal_places=2)  # Importe total
    retenciones = models.DecimalField(max_digits=15, decimal_places=2)  # Retenciones aplicadas
    credito = models.DecimalField(max_digits=20, decimal_places=2)  # Crédito neto
    liquidacion = models.CharField(max_length=50)  # Código de liquidación
    importe_liquidado = models.DecimalField(max_digits=20, decimal_places=2)  # Importe liquidado

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_galeno')

    archivo_origen = models.CharField(max_length=20, null=True, blank=True)


    def __str__(self):
        return f"{self.prestador} - {self.orden_de_pago}"
    
class LiquidacionPAMI(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name="liquidaciones_pami")
    codigo_farmacia = models.CharField(max_length=20, help_text="Código de la farmacia en PAMI")
    nombre_farmacia = models.CharField(max_length=255, help_text="Nombre de la farmacia")
    plan = models.CharField(max_length=255, help_text="Plan de la obra social")
    fecha_liquidacion = models.DateField(help_text="Fecha en la que se procesó la liquidación")
    
    # Datos financieros
    importe_100 = models.DecimalField(max_digits=15, decimal_places=2, help_text="Importe total de la presentación")
    a_cargo_os = models.DecimalField(max_digits=15, decimal_places=2, help_text="Importe a cargo de la obra social")
    bonificacion = models.DecimalField(max_digits=15, decimal_places=2, help_text="Bonificación aplicada")
    nota_credito = models.DecimalField(max_digits=15, decimal_places=2, help_text="Nota de crédito aplicada")
    subtotal_pagar = models.DecimalField(max_digits=15, decimal_places=2, help_text="Subtotal a pagar")
    
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_pami')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    archivo_origen = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Liquidación PAMI"
        verbose_name_plural = "Liquidaciones PAMI"

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.subtotal_pagar}"
    
class LiquidacionJerarquicos(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name="liquidaciones_jerarquicos")
    codigo_farmacia = models.CharField(max_length=20, help_text="Código de la farmacia")
    nombre_farmacia = models.CharField(max_length=255, help_text="Nombre de la farmacia")
    plan = models.CharField(max_length=255, help_text="Plan de la obra social")
    fecha_liquidacion = models.DateField(help_text="Fecha de la liquidación")

    # Datos financieros
    importe_100 = models.DecimalField(max_digits=15, decimal_places=2, help_text="Importe total de la presentación")
    a_cargo_os = models.DecimalField(max_digits=15, decimal_places=2, help_text="Importe a cargo de la obra social")
    bonificacion = models.DecimalField(max_digits=15, decimal_places=2, help_text="Bonificación aplicada")
    nota_credito = models.DecimalField(max_digits=15, decimal_places=2, help_text="Nota de crédito aplicada")
    subtotal_pagar = models.DecimalField(max_digits=15, decimal_places=2, help_text="Subtotal a pagar")

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_jerarquicos')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    archivo_origen = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Liquidación Jerárquicos"
        verbose_name_plural = "Liquidaciones Jerárquicos"

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.subtotal_pagar}"

class LiquidacionOspil(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name="liquidaciones_ospil")
    codigo_farmacia = models.CharField(max_length=20)
    nombre_farmacia = models.CharField(max_length=255)
    plan = models.CharField(max_length=255)
    fecha_liquidacion = models.DateField()

    importe_100 = models.DecimalField(max_digits=15, decimal_places=2)
    a_cargo_os = models.DecimalField(max_digits=15, decimal_places=2)
    bonificacion = models.DecimalField(max_digits=15, decimal_places=2)
    nota_credito = models.DecimalField(max_digits=15, decimal_places=2)
    subtotal_pagar = models.DecimalField(max_digits=15, decimal_places=2)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_ospil')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    archivo_origen = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.subtotal_pagar}"

class LiquidacionOsfatlyf(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name="liquidaciones_osfatlyf")
    codigo_farmacia = models.CharField(max_length=20)
    nombre_farmacia = models.CharField(max_length=255)
    plan = models.CharField(max_length=255)
    fecha_liquidacion = models.DateField()

    importe_100 = models.DecimalField(max_digits=15, decimal_places=2)
    a_cargo_os = models.DecimalField(max_digits=15, decimal_places=2)
    bonificacion = models.DecimalField(max_digits=15, decimal_places=2)
    nota_credito = models.DecimalField(max_digits=15, decimal_places=2)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_osfatlyf')

    archivo_origen = models.CharField(max_length=20, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.subtotal_pagar}"
    
class LiquidacionPAMIOncologico(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name="liquidaciones_pami_oncologico")
    codigo_farmacia = models.CharField(max_length=20, help_text="Código de la farmacia en PAMI Oncológico")
    nombre_farmacia = models.CharField(max_length=255, help_text="Nombre de la farmacia")
    plan = models.CharField(max_length=255, help_text="Plan de la obra social")
    fecha_liquidacion = models.DateField(help_text="Fecha en la que se procesó la liquidación")

    # Datos financieros
    importe_100 = models.DecimalField(max_digits=15, decimal_places=2, help_text="Importe total de la presentación")
    a_cargo_os = models.DecimalField(max_digits=15, decimal_places=2, help_text="Importe a cargo de la obra social")
    bonificacion = models.DecimalField(max_digits=15, decimal_places=2, help_text="Bonificación aplicada")
    nota_credito = models.DecimalField(max_digits=15, decimal_places=2, help_text="Nota de crédito aplicada")
    subtotal_pagar = models.DecimalField(max_digits=15, decimal_places=2, help_text="Subtotal a pagar")

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_pami_oncologico')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    archivo_origen = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Liquidación PAMI Oncológico"
        verbose_name_plural = "Liquidaciones PAMI Oncológico"

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.subtotal_pagar}"
    
class LiquidacionPAMIPanales(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name="liquidaciones_pami_panales")
    codigo_farmacia = models.CharField(max_length=20, help_text="Código de la farmacia en PAMI")
    nombre_farmacia = models.CharField(max_length=255, help_text="Nombre de la farmacia")
    plan = models.CharField(max_length=255, help_text="Plan de la obra social")
    fecha_liquidacion = models.DateField(help_text="Fecha en la que se procesó la liquidación")

    # Datos financieros
    importe_100 = models.DecimalField(max_digits=15, decimal_places=2, help_text="Importe total de la presentación")
    a_cargo_os = models.DecimalField(max_digits=15, decimal_places=2, help_text="Importe a cargo de la obra social")
    bonificacion = models.DecimalField(max_digits=15, decimal_places=2, help_text="Bonificación aplicada")
    nota_credito = models.DecimalField(max_digits=15, decimal_places=2, help_text="Nota de crédito aplicada")
    subtotal_pagar = models.DecimalField(max_digits=15, decimal_places=2, help_text="Subtotal a pagar")

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_pami_pañales')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    archivo_origen = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Liquidación PAMI Pañales"
        verbose_name_plural = "Liquidaciones PAMI Pañales"

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.subtotal_pagar}"

class LiquidacionPAMIVacunas(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name="liquidaciones_pami_vacunas")
    codigo_farmacia = models.CharField(max_length=20)
    nombre_farmacia = models.CharField(max_length=255)
    plan = models.CharField(max_length=255)
    fecha_liquidacion = models.DateField()

    importe_100 = models.DecimalField(max_digits=15, decimal_places=2)
    a_cargo_os = models.DecimalField(max_digits=15, decimal_places=2)
    bonificacion = models.DecimalField(max_digits=15, decimal_places=2)
    nota_credito = models.DecimalField(max_digits=15, decimal_places=2)
    subtotal_pagar = models.DecimalField(max_digits=15, decimal_places=2)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_pami_vacunas')

    archivo_origen = models.CharField(max_length=20, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.subtotal_pagar}"

class LiquidacionAndinaART(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name="liquidaciones_andina_art")
    codigo_farmacia = models.CharField(max_length=20, help_text="Código de la farmacia en Andina ART")
    nombre_farmacia = models.CharField(max_length=255, help_text="Nombre de la farmacia")
    plan = models.CharField(max_length=255, help_text="Plan de la obra social")
    fecha_liquidacion = models.DateField(help_text="Fecha en la que se procesó la liquidación")

    # Datos financieros
    importe_100 = models.DecimalField(max_digits=15, decimal_places=2)
    a_cargo_os = models.DecimalField(max_digits=15, decimal_places=2)
    bonificacion = models.DecimalField(max_digits=15, decimal_places=2)
    nota_credito = models.DecimalField(max_digits=15, decimal_places=2)
    subtotal_pagar = models.DecimalField(max_digits=15, decimal_places=2)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_andinaart')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    archivo_origen = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Liquidación Andina ART"
        verbose_name_plural = "Liquidaciones Andina ART"

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.subtotal_pagar}"

class LiquidacionAsociart(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name="liquidaciones_asociart")
    codigo_farmacia = models.CharField(max_length=20, help_text="Código de la farmacia en ASOCIART")
    nombre_farmacia = models.CharField(max_length=255, help_text="Nombre de la farmacia")
    plan = models.CharField(max_length=255, help_text="Plan de la obra social")
    fecha_liquidacion = models.DateField(help_text="Fecha en la que se procesó la liquidación")

    # Datos financieros
    importe_100 = models.DecimalField(max_digits=15, decimal_places=2, help_text="Importe total de la presentación")
    a_cargo_os = models.DecimalField(max_digits=15, decimal_places=2, help_text="Importe a cargo de la obra social")
    bonificacion = models.DecimalField(max_digits=15, decimal_places=2, help_text="Bonificación aplicada")
    nota_credito = models.DecimalField(max_digits=15, decimal_places=2, help_text="Nota de crédito aplicada")
    subtotal_pagar = models.DecimalField(max_digits=15, decimal_places=2, help_text="Subtotal a pagar")

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_asociart')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    archivo_origen = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Liquidación Asociart"
        verbose_name_plural = "Liquidaciones Asociart"

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.subtotal_pagar}"

class LiquidacionColoniaSuiza(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name="liquidaciones_coloniasuiza")
    codigo_farmacia = models.CharField(max_length=20)
    nombre_farmacia = models.CharField(max_length=255)
    plan = models.CharField(max_length=255)
    fecha_liquidacion = models.DateField()
    
    importe_100 = models.DecimalField(max_digits=15, decimal_places=2)
    a_cargo_os = models.DecimalField(max_digits=15, decimal_places=2)
    bonificacion = models.DecimalField(max_digits=15, decimal_places=2)
    nota_credito = models.DecimalField(max_digits=15, decimal_places=2)
    subtotal_pagar = models.DecimalField(max_digits=15, decimal_places=2)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_coloniasuiza')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    archivo_origen = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Liquidación Colonia Suiza"
        verbose_name_plural = "Liquidaciones Colonia Suiza"

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.subtotal_pagar}"

class LiquidacionExperta(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name="liquidaciones_experta")
    codigo_farmacia = models.CharField(max_length=20, help_text="Código de la farmacia")
    nombre_farmacia = models.CharField(max_length=255, help_text="Nombre de la farmacia")
    plan = models.CharField(max_length=255, help_text="Plan de la obra social")
    fecha_liquidacion = models.DateField(help_text="Fecha de la liquidación")
    
    importe_100 = models.DecimalField(max_digits=15, decimal_places=2)
    a_cargo_os = models.DecimalField(max_digits=15, decimal_places=2)
    bonificacion = models.DecimalField(max_digits=15, decimal_places=2)
    nota_credito = models.DecimalField(max_digits=15, decimal_places=2)
    subtotal_pagar = models.DecimalField(max_digits=15, decimal_places=2)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_experta')

    archivo_origen = models.CharField(max_length=20, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Liquidación Experta ART"
        verbose_name_plural = "Liquidaciones Experta ART"

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.subtotal_pagar}"

class LiquidacionGalenoART(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name="liquidaciones_galenoart")
    codigo_farmacia = models.CharField(max_length=20)
    nombre_farmacia = models.CharField(max_length=255)
    plan = models.CharField(max_length=255)
    fecha_liquidacion = models.DateField()

    importe_100 = models.DecimalField(max_digits=15, decimal_places=2)
    a_cargo_os = models.DecimalField(max_digits=15, decimal_places=2)
    bonificacion = models.DecimalField(max_digits=15, decimal_places=2)
    nota_credito = models.DecimalField(max_digits=15, decimal_places=2)
    subtotal_pagar = models.DecimalField(max_digits=15, decimal_places=2)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_galenoart')

    archivo_origen = models.CharField(max_length=20, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Liquidación Galeno ART"
        verbose_name_plural = "Liquidaciones Galeno ART"

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.subtotal_pagar}"

class LiquidacionPrevencionART(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name="liquidaciones_prevencion")
    codigo_farmacia = models.CharField(max_length=20, help_text="Código de la farmacia")
    nombre_farmacia = models.CharField(max_length=255, help_text="Nombre de la farmacia")
    plan = models.CharField(max_length=255, help_text="Plan de la obra social")
    fecha_liquidacion = models.DateField(help_text="Fecha en la que se procesó la liquidación")

    # Datos financieros
    importe_100 = models.DecimalField(max_digits=15, decimal_places=2)
    a_cargo_os = models.DecimalField(max_digits=15, decimal_places=2)
    bonificacion = models.DecimalField(max_digits=15, decimal_places=2)
    nota_credito = models.DecimalField(max_digits=15, decimal_places=2)
    subtotal_pagar = models.DecimalField(max_digits=15, decimal_places=2)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_prevencionart')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    archivo_origen = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Liquidación Prevención ART"
        verbose_name_plural = "Liquidaciones Prevención ART"
