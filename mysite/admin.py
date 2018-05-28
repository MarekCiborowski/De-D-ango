from django.contrib import admin
from django.contrib.auth.models import User

from .models import wybory, osoba, osobaWybory, oddanyGlos, myUser
# Register your models here.
admin.site.register(wybory)
admin.site.register(osobaWybory)
admin.site.register(osoba)
admin.site.register(oddanyGlos)
admin.site.register(myUser)