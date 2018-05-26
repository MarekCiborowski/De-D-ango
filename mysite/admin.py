from django.contrib import admin
from .models import wybory,osoba,osobaWybory,oddanyGlos
# Register your models here.
admin.site.register(wybory)
admin.site.register(osobaWybory)
admin.site.register(osoba)
admin.site.register(oddanyGlos)