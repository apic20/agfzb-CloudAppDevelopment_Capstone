from django.contrib import admin
from .models import *


# Register your models here.

class CarModelInline(admin.StackedInline):
    model = CarModel
    #fields = ['make','name','dealerid','type','year']

class CarModelAdmin(admin.ModelAdmin):
    model = CarModel

class CarMakeAdmin(admin.ModelAdmin):
    model = CarMake
    inlines= [CarModelInline]

# Register models here
admin.site.register(CarMake,CarMakeAdmin)
admin.site.register(CarModel,CarModelAdmin)
