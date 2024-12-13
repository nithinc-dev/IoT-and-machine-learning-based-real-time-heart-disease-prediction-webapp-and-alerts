from django.db import models

class Disease(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
        
    def __str__(self):
        return f"{self.name}"


# from django.db import models
# from django.contrib.auth.models import AbstractUser, BaseUserManager

# class DoctorManager(BaseUserManager):
#     def create_user(self, email, name, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email, name=name, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, name, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')

#         return self.create_user(email, name, password, **extra_fields)

# from django.contrib.auth.hashers import make_password

# class Doctor(AbstractUser):
#     name = models.CharField(max_length=255)
#     qualification = models.CharField(max_length=255)
#     hospital = models.CharField(max_length=255)
#     email = models.EmailField(unique=True, default='default@example.com')
#     password = models.CharField(max_length=250, default=make_password('default_password'))
#     # Remove username field and use email as primary identifier
#     username = None
   
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['name']
   
#     objects = DoctorManager()

#     def __str__(self):
#         return f"{self.name}, {self.qualification} at {self.hospital}"

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.contrib.auth.hashers import make_password

class DoctorManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, name, password, **extra_fields)

class Doctor(AbstractUser):
    name = models.CharField(max_length=255)
    qualification = models.CharField(max_length=255)
    hospital = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    
    # Remove the default password field
    username = None
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    objects = DoctorManager()
    
    groups = models.ManyToManyField(
        Group,
        related_name='doctor_set',
        blank=True,
        verbose_name='groups'
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='doctor_set',
        blank=True,
        verbose_name='user permissions'
    )
    
    def __str__(self):
        return f"{self.name}, {self.qualification} at {self.hospital}"

# class Doctor(models.Model):  # Use PascalCase for class names
#     name = models.CharField(max_length=255)
#     qualification = models.CharField(max_length=255)
#     hospital = models.CharField(max_length=255)  # Corrected typo in 'hospital'
#     email = models.EmailField(max_length=5)
#     password = models.CharField(max_length=250)
    
#     def __str__(self):
#         return f"{self.name}, {self.qualification} at {self.hospital}"

class Patient(models.Model):
    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    dob = models.DateField()
    gender = models.CharField(max_length=50, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])
    profile_picture = models.ImageField(upload_to="images")
    doctor = models.ManyToManyField(Doctor)  # Update to match Doctor model name
    diseases = models.ManyToManyField(Disease)
    patient_email = models.EmailField(max_length=50, default='default@example.com')
    patient_key = models.CharField(max_length=10, default="notdefined")
    care_taker_email1 = models.EmailField(max_length=50, default='default@example.com')
    care_taker_email2 = models.EmailField(max_length=50, default='default@example.com')
    doctor_email = models.EmailField(max_length=50, default='default@example.com')
    
    def __str__(self):
        return self.name

# class ECG(models.Model):
#     patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="ecg_readings")
#     ecg_data = models.DecimalField(max_digits=10, decimal_places=3)
#     timestamp = models.DateTimeField()
   
#     def __str__(self):
#         return f"ECG Data for {self.patient.name} at {self.timestamp}"
 
from django.db import models
from django.utils.translation import gettext_lazy as _

class ECG(models.Model):
    patient = models.ForeignKey(
        'Patient',  
        on_delete=models.CASCADE, 
        related_name="ecg_readings",
        verbose_name=_("Patient")
    )
    ecg_data = models.DecimalField(
        _("ECG Data"), 
        max_digits=10, 
        decimal_places=3
    )
    timestamp = models.DateTimeField(
        _("Timestamp"), 
        auto_now_add=False,  # Allow custom timestamps
        help_text=_("Timestamp with microsecond precision")
    )

    class Meta:
        verbose_name = _("ECG Reading")
        verbose_name_plural = _("ECG Readings")
        ordering = ['-timestamp']

    def __str__(self):
        return f"ECG Data for {self.patient.name} at {self.timestamp.isoformat()}"
    

class Location(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="locations")
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    altitude = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Location for {self.patient.name} at lat: {self.latitude} lon: {self.longitude} time: {self.timestamp}"
# from django.db import models

# class Disease(models.Model):
    
#     name = models.CharField(max_length=255)
#     description = models.TextField(null=True, blank=True)
        
#     def __str__(self):
#         return f"{self.name} "

# class doctor(models.Model):
#     name = models.CharField(max_length=255)
#     qualification = models.CharField(max_length=255)
#     hostpital = models.CharField(max_length=255)
    
#     def __str__(self):
#         return f"{self.name}, {self.qualification} {self.hosptital}"



# class Patient(models.Model):
#     name = models.CharField(max_length=255)
#     age = models.PositiveIntegerField()
#     dob = models.DateField()
#     gender = models.CharField(max_length=50, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])
#     profile_picture = models.ImageField(upload_to="images")
#     doctor = models.ManyToManyField(doctor)
#     diseases = models.ManyToManyField(Disease)
    
    

#     def __str__(self):
#         return self.name


# class ECG(models.Model):
    
#     patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="ecg_readings")
#     ecg_data = models.DecimalField(max_digits=10, decimal_places=3)  # Example: storing voltage data in mV
#     timestamp = models.DateTimeField()
   

#     def __str__(self):
#         return f"ECG Data for {self.patient.name} at {self.timestamp}"


# class Location(models.Model):
#     patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="locations")
#     latitude = models.DecimalField(max_digits=10, decimal_places=8)
#     longitude = models.DecimalField(max_digits=11, decimal_places=8)
#     altitude = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
#     timestamp = models.DateTimeField()

#     def __str__(self):
#         return f"Location for {self.patient.name} at lat {self.latitude} lon {self.longitude} time {self.timestamp}"



