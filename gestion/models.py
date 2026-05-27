from django.db import models

class Ciclo(models.Model):
    ciclo = models.CharField(max_length=255)
    preparacion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.ciclo

class Alumno(models.Model):
    GRADO_CHOICES = [('GS', 'Grado Superior'), ('GM', 'Grado Medio'), ('B', 'Básica'), ('FPB', 'FP Básica')]
    TURNO_CHOICES = [('M', 'Mañana'), ('T', 'Tarde'), ('O', 'Online')]

    dni = models.CharField(max_length=20, unique=True)
    apellidos = models.CharField(max_length=255)
    nombre = models.CharField(max_length=255)
    fecha_nto = models.DateField(null=True, blank=True)
    poblacion = models.CharField(max_length=255, blank=True, null=True)
    tlf_movil = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    ciclo = models.ForeignKey(Ciclo, on_delete=models.CASCADE, null=True, blank=True)
    curso = models.CharField(max_length=50, blank=True, null=True)
    ano = models.CharField(max_length=20, blank=True, null=True)
    grado = models.CharField(max_length=10, choices=GRADO_CHOICES, blank=True, null=True)
    turno = models.CharField(max_length=10, choices=TURNO_CHOICES, blank=True, null=True)
    num_alumno = models.CharField(max_length=50, blank=True, null=True)
    tutor_fct = models.CharField(max_length=255, blank=True, null=True)
    obs = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"

class Empresa(models.Model):
    nombre = models.CharField(max_length=255)
    cif = models.CharField(max_length=20)
    representante = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    cp = models.CharField(max_length=10, blank=True, null=True)
    contacto = models.CharField(max_length=255, blank=True, null=True)
    tutor_empresa = models.CharField(max_length=255, blank=True, null=True)
    tel = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fecha_convenio = models.DateField(null=True, blank=True)
    plazas = models.IntegerField(default=2)

    def __str__(self):
        return self.nombre

class Asignacion(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    tutor_centro = models.CharField(max_length=255, blank=True, null=True)
    inicio = models.DateField()
    fin = models.DateField()
    horas = models.IntegerField(default=400)
    horas_comp = models.IntegerField(default=0)
    obs = models.TextField(blank=True, null=True)
    fecha_firma = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.alumno} en {self.empresa}"