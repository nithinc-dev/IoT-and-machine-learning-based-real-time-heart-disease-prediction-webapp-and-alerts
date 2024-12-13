from django.contrib import admin
from .models import Disease, Doctor, Patient, ECG, Location

# Register models in Django admin
admin.site.register(Disease)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(ECG)
admin.site.register(Location)


