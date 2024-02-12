from django.contrib import admin
from .models import Securetech

# Register your models here.
@admin.register(Securetech)

class SecuretechAdmin(admin.ModelAdmin): #to display list in admin
    list_display = ('name','email','password')
