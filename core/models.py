from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone

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
        ('Enviado', 'Enviado'),
        ('Recibida en Cámara', 'Recibido en Cámara'),
        ('Presentado en obra social', 'Presentado en obra social'),
        ('Liquidada', 'Liquidada')
    ]

    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE)
    obra_social = models.CharField(max_length=50, choices=OBRAS_SOCIALES, blank=False)
    periodo = models.DateField(max_length=50, blank=False, default="none")
    numero_presentacion = models.CharField(max_length=50, null=True, blank=False)
    estado = models.CharField(max_length=100, choices=ESTADOS, default='Enviada', blank=False)
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

    archivo_origen = models.CharField(max_length=50, null=True, blank=True)

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

    archivo_origen = models.CharField(max_length=50, null=True, blank=True)


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
    
    # Nuevos campos agregados para coincidir con el Excel
    debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Débitos OS")
    creditos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Créditos OS")
    inst_pago_drogueria = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Inst. Pago Droguería")
    recuperacion_gastos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Recupero Gastos")

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_pami')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    archivo_origen = models.CharField(max_length=50, null=True, blank=True)

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
    
    # Nuevos campos agregados
    debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    credito = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    gastos_debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_gastos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_jerarquicos')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    archivo_origen = models.CharField(max_length=50, null=True, blank=True)

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
    
    # Nuevos campos agregados
    debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    credito = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    gastos_debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_gastos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_ospil')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    archivo_origen = models.CharField(max_length=50, null=True, blank=True)

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

    # Nuevos campos agregados
    debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_gastos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    subtotal_a_pagar = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_osfatlyf')

    archivo_origen = models.CharField(max_length=50, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.subtotal_a_pagar}"
    
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

    debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_gastos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_pami_oncologico')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    archivo_origen = models.CharField(max_length=50, null=True, blank=True)

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

    debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_gastos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_pami_pañales')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    archivo_origen = models.CharField(max_length=50, null=True, blank=True)

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

    debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_gastos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_pami_vacunas')

    archivo_origen = models.CharField(max_length=50, null=True, blank=True)
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

    # Retenciones
    debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_gastos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_andinaart')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    archivo_origen = models.CharField(max_length=50, null=True, blank=True)

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
    
    # Nuevos campos agregados
    debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_gastos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_asociart')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    archivo_origen = models.CharField(max_length=50, null=True, blank=True)

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
    
    # Nuevos campos agregados
    debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_gastos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_coloniasuiza')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    archivo_origen = models.CharField(max_length=50, null=True, blank=True)

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
    
    # Nuevos campos agregados
    debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_gastos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_experta')

    archivo_origen = models.CharField(max_length=50, null=True, blank=True)
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
    
    # Nuevos campos agregados
    debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    credito = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    gastos_debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_gastos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_galenoart')

    archivo_origen = models.CharField(max_length=50, null=True, blank=True)
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
    
    # Nuevos campos agregados
    debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_ajustes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_gastos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_prevencionart')

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    archivo_origen = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "Liquidación Prevención ART"
        verbose_name_plural = "Liquidaciones Prevención ART"

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.subtotal_pagar}"


class Publication(models.Model):
    """
    Modelo para las publicaciones del foro
    """
    CATEGORIAS = [
        ('obra-social', 'Obra social'),
        ('anuncio', 'Anuncio'),
        ('recordatorio', 'Recordatorio'),
    ]

    # Información básica
    descripcion = models.TextField(help_text="Contenido de la publicación")
    categoria = models.CharField(
        max_length=20, 
        choices=CATEGORIAS, 
        help_text="Categoría de la publicación"
    )
    
    # Archivos adjuntos
    imagen = models.ImageField(
        upload_to='publicaciones/imagenes/', 
        null=True, 
        blank=True,
        help_text="Imagen adjunta a la publicación"
    )
    archivo = models.FileField(
        upload_to='publicaciones/archivos/', 
        null=True, 
        blank=True,
        help_text="Archivo adjunto a la publicación"
    )
    
    # Usuarios y fechas
    usuario_creacion = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='publicaciones_creadas',
        help_text="Usuario que creó la publicación"
    )
    usuario_modificacion = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='publicaciones_modificadas',
        help_text="Usuario que modificó la publicación por última vez"
    )
    
    # Fechas
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de creación"
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        help_text="Fecha y hora de la última modificación"
    )
    
    # Contadores
    likes_count = models.PositiveIntegerField(
        default=0,
        help_text="Número total de likes"
    )
    comentarios_count = models.PositiveIntegerField(
        default=0,
        help_text="Número total de comentarios"
    )

    class Meta:
        verbose_name = "Publicación"
        verbose_name_plural = "Publicaciones"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.usuario_creacion.username} - {self.categoria} - {self.fecha_creacion.strftime('%d/%m/%Y %H:%M')}"

    def get_tiempo_transcurrido(self):
        """
        Retorna el tiempo transcurrido desde la creación en formato legible
        """
        from django.utils import timezone
        from datetime import datetime
        
        ahora = timezone.now()
        diferencia = ahora - self.fecha_creacion
        
        if diferencia.days > 0:
            return f"hace {diferencia.days} día{'s' if diferencia.days != 1 else ''}"
        elif diferencia.seconds >= 3600:
            horas = diferencia.seconds // 3600
            return f"hace {horas} hora{'s' if horas != 1 else ''}"
        elif diferencia.seconds >= 60:
            minutos = diferencia.seconds // 60
            return f"hace {minutos} minuto{'s' if minutos != 1 else ''}"
        else:
            return "ahora mismo"


class PublicationLike(models.Model):
    """
    Modelo para los likes de las publicaciones
    """
    publicacion = models.ForeignKey(
        Publication, 
        on_delete=models.CASCADE,
        related_name='likes',
        help_text="Publicación que recibió el like"
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='likes_dados',
        help_text="Usuario que dio el like"
    )
    fecha_like = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora del like"
    )

    class Meta:
        verbose_name = "Like de Publicación"
        verbose_name_plural = "Likes de Publicaciones"
        unique_together = ['publicacion', 'usuario']  # Un usuario solo puede dar like una vez
        ordering = ['-fecha_like']

    def __str__(self):
        return f"{self.usuario.username} → {self.publicacion}"

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para actualizar el contador de likes
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Incrementar contador de likes
            self.publicacion.likes_count += 1
            self.publicacion.save(update_fields=['likes_count'])

    def delete(self, *args, **kwargs):
        """
        Sobrescribe el método delete para actualizar el contador de likes
        """
        # Decrementar contador de likes
        self.publicacion.likes_count = max(0, self.publicacion.likes_count - 1)
        self.publicacion.save(update_fields=['likes_count'])
        super().delete(*args, **kwargs)


class PublicationComment(models.Model):
    """
    Modelo para los comentarios de las publicaciones
    """
    publicacion = models.ForeignKey(
        Publication, 
        on_delete=models.CASCADE,
        related_name='comentarios',
        help_text="Publicación a la que pertenece el comentario"
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='comentarios_realizados',
        help_text="Usuario que realizó el comentario"
    )
    contenido = models.TextField(
        help_text="Contenido del comentario"
    )
    fecha_comentario = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora del comentario"
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        help_text="Comentario padre si es una respuesta"
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text="Indica si el comentario fue eliminado (borrado lógico)"
    )

    class Meta:
        verbose_name = "Comentario de Publicación"
        verbose_name_plural = "Comentarios de Publicaciones"
        ordering = ['fecha_comentario']

    def __str__(self):
        if self.is_deleted:
            return f"[Eliminado]"
        return f"{self.usuario.username} → {self.publicacion} - {self.fecha_comentario.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para actualizar el contador de comentarios
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new and not self.is_deleted:
            # Incrementar contador de comentarios
            self.publicacion.comentarios_count += 1
            self.publicacion.save(update_fields=['comentarios_count'])

    def delete(self, *args, **kwargs):
        """
        Sobrescribe el método delete para actualizar el contador de comentarios
        """
        # Decrementar contador de comentarios
        self.publicacion.comentarios_count = max(0, self.publicacion.comentarios_count - 1)
        self.publicacion.save(update_fields=['comentarios_count'])
        super().delete(*args, **kwargs)

class Reclamo(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En progreso'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
    ]
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    usuario_creador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reclamos_creados')
    usuario_asignado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reclamos_asignados')
    asignados = models.ManyToManyField(User, related_name='reclamos_asignados_multiple', blank=True, help_text='Usuarios asignados a este reclamo (múltiples)')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    ultima_actualizacion_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reclamos_actualizados')
    notificaciones_activas = models.BooleanField(default=True)
    es_publico = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='reclamos/imagenes/', null=True, blank=True)
    archivo = models.FileField(upload_to='reclamos/archivos/', null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Reclamo'
        verbose_name_plural = 'Reclamos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo} ({self.get_estado_display()})"

class ReclamoComment(models.Model):
    reclamo = models.ForeignKey(
        'Reclamo',
        on_delete=models.CASCADE,
        related_name='comentarios',
        help_text="Reclamo al que pertenece el comentario"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reclamo_comentarios_realizados',
        help_text="Usuario que realizó el comentario"
    )
    contenido = models.TextField(help_text="Contenido del comentario")
    fecha_comentario = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora del comentario")
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        help_text="Comentario padre si es una respuesta"
    )
    imagen = models.ImageField(upload_to='reclamos/comentarios/imagenes/', null=True, blank=True)
    archivo = models.FileField(upload_to='reclamos/comentarios/archivos/', null=True, blank=True)
    is_deleted = models.BooleanField(default=False, help_text="Indica si el comentario fue eliminado (borrado lógico)")

    class Meta:
        verbose_name = "Comentario de Reclamo"
        verbose_name_plural = "Comentarios de Reclamos"
        ordering = ['fecha_comentario']

    def __str__(self):
        if self.is_deleted:
            return f"[Eliminado]"
        return f"{self.usuario.username} → {self.reclamo} - {self.fecha_comentario.strftime('%d/%m/%Y %H:%M')}"

class Notification(models.Model):
    """
    Notificación interna para usuarios (foro, reclamos, etc)
    """
    TIPOS = [
        ("reclamo_estado", "Cambio de estado de reclamo"),
        ("reclamo_comentario", "Nuevo comentario en reclamo"),
        ("foro", "Notificación de foro"),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificaciones")
    mensaje = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)
    leido = models.BooleanField(default=False)
    fecha = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(max_length=32, choices=TIPOS, default="foro")

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Notificación para {self.usuario}: {self.mensaje[:40]}..."


class GuiaVideo(models.Model):
    """
    Modelo para videos de guías de uso
    """
    CATEGORIAS = [
        ('tutorial', 'Tutorial'),
        ('manual', 'Manual'),
        ('explicacion', 'Explicación'),
        ('demo', 'Demostración'),
        ('otro', 'Otro'),
    ]
    
    ESTADOS = [
        ('publico', 'Público'),
        ('privado', 'Privado'),
    ]
    
    # Información básica
    titulo = models.CharField(max_length=200, help_text="Título del video")
    descripcion = models.TextField(blank=True, help_text="Descripción del video")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='tutorial')
    estado = models.CharField(max_length=10, choices=ESTADOS, default='publico')
    
    # Archivo de video
    archivo_video = models.FileField(
        upload_to='guias/videos/',
        help_text="Archivo de video (MP4, AVI, MOV, etc.)"
    )
    
    # Thumbnail generado automáticamente
    thumbnail = models.ImageField(
        upload_to='guias/thumbnails/',
        null=True,
        blank=True,
        help_text="Imagen de vista previa generada automáticamente del video"
    )
    
    # Metadatos del video
    duracion = models.CharField(max_length=10, blank=True, help_text="Duración del video (HH:MM:SS)")
    tamanio = models.BigIntegerField(null=True, blank=True, help_text="Tamaño del archivo en bytes")
    
    # Usuario y fechas
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='videos_subidos',
        help_text="Usuario que subió el video"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    # Contadores
    visualizaciones = models.PositiveIntegerField(default=0, help_text="Número de visualizaciones")
    descargas = models.PositiveIntegerField(default=0, help_text="Número de descargas")
    
    class Meta:
        verbose_name = "Video de Guía"
        verbose_name_plural = "Videos de Guías"
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return self.titulo
    
    def get_duracion_formateada(self):
        """Retorna la duración en formato legible"""
        if self.duracion:
            return self.duracion
        return "00:00"
    
    def get_tamanio_formateado(self):
        """Retorna el tamaño en formato legible"""
        if not self.tamanio:
            return "0 KB"
        
        for unidad in ['B', 'KB', 'MB', 'GB']:
            if self.tamanio < 1024.0:
                return f"{self.tamanio:.1f} {unidad}"
            self.tamanio /= 1024.0
        return f"{self.tamanio:.1f} TB"


class GuiaArchivo(models.Model):
    """
    Modelo para archivos de guías de uso (PDF, Word, etc.)
    """
    TIPOS_ARCHIVO = [
        ('pdf', 'PDF'),
        ('doc', 'Word'),
        ('docx', 'Word'),
        ('xls', 'Excel'),
        ('xlsx', 'Excel'),
        ('ppt', 'PowerPoint'),
        ('pptx', 'PowerPoint'),
        ('txt', 'Texto'),
        ('otro', 'Otro'),
    ]
    
    CATEGORIAS = [
        ('manual', 'Manual'),
        ('procedimiento', 'Procedimiento'),
        ('formulario', 'Formulario'),
        ('guia', 'Guía'),
        ('faq', 'Preguntas Frecuentes'),
        ('otro', 'Otro'),
    ]
    
    ESTADOS = [
        ('publico', 'Público'),
        ('privado', 'Privado'),
    ]
    
    # Información básica
    titulo = models.CharField(max_length=200, help_text="Título del archivo")
    descripcion = models.TextField(blank=True, help_text="Descripción del archivo")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='manual')
    estado = models.CharField(max_length=10, choices=ESTADOS, default='publico')
    
    # Archivo
    archivo = models.FileField(
        upload_to='guias/archivos/',
        help_text="Archivo (PDF, Word, Excel, etc.)"
    )
    
    # Metadatos del archivo
    tipo_archivo = models.CharField(max_length=10, choices=TIPOS_ARCHIVO, default='pdf')
    tamanio = models.BigIntegerField(null=True, blank=True, help_text="Tamaño del archivo en bytes")
    
    # Usuario y fechas
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='archivos_subidos',
        help_text="Usuario que subió el archivo"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    # Contadores
    descargas = models.PositiveIntegerField(default=0, help_text="Número de descargas")
    visualizaciones = models.PositiveIntegerField(default=0, help_text="Número de visualizaciones")
    
    class Meta:
        verbose_name = "Archivo de Guía"
        verbose_name_plural = "Archivos de Guías"
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return self.titulo
    
    def get_tamanio_formateado(self):
        """Retorna el tamaño en formato legible"""
        if not self.tamanio:
            return "0 KB"
        
        tamanio = self.tamanio
        for unidad in ['B', 'KB', 'MB', 'GB']:
            if tamanio < 1024.0:
                return f"{tamanio:.1f} {unidad}"
            tamanio /= 1024.0
        return f"{tamanio:.1f} TB"
    
    def get_extension(self):
        """Retorna la extensión del archivo"""
        if self.archivo:
            return self.archivo.name.split('.')[-1].upper()
        return ""


class LiquidacionLaSegundaART(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name="liquidaciones_lasegundaart")
    codigo_farmacia = models.CharField(max_length=20)
    nombre_farmacia = models.CharField(max_length=255)
    plan = models.CharField(max_length=255)
    fecha_liquidacion = models.DateField()

    importe_100 = models.DecimalField(max_digits=15, decimal_places=2)
    a_cargo_os = models.DecimalField(max_digits=15, decimal_places=2)
    bonificacion = models.DecimalField(max_digits=15, decimal_places=2)
    nota_credito = models.DecimalField(max_digits=15, decimal_places=2)
    subtotal_pagar = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Nuevos campos agregados
    debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    credito = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    gastos_debitos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recuperacion_gastos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_lasegundaart')

    archivo_origen = models.CharField(max_length=50, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Liquidación La Segunda ART"
        verbose_name_plural = "Liquidaciones La Segunda ART"

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.subtotal_pagar}"


class LiquidacionOSDIPP(models.Model):
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name="liquidaciones_osdipp")
    codigo_farmacia = models.CharField(max_length=20, help_text="Código de la farmacia")
    nombre_farmacia = models.CharField(max_length=255, help_text="Nombre de la farmacia")
    plan = models.CharField(max_length=255, help_text="Plan de la obra social", default="OSDIPP")
    fecha_liquidacion = models.DateField(help_text="Fecha de la liquidación")

    # Datos financieros principales (ajustar según los datos del PDF)
    recetas_presentadas = models.IntegerField(default=0)
    importe_total_presentado = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    importe_entregado_presentado = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    recetas_aceptadas = models.IntegerField(default=0)
    importe_total_aceptado = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    importe_entregado_aceptado = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    aporte_farmacia = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    gastos_auditoria = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    importe_neto = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    gastos_recs = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    ajustes_anteriores = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    ajuste_credito_anticipado = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    importe_a_pagar = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    importe_efectivo = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    ajustes_posteriores = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    # Archivo y usuario
    archivo_origen = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='liquidaciones_osdipp')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Liquidación OSDIPP"
        verbose_name_plural = "Liquidaciones OSDIPP"

    def __str__(self):
        return f"{self.farmacia} - {self.fecha_liquidacion} - {self.importe_a_pagar}"
