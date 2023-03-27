from django.contrib import admin
from .models import Point, Printer

class PrinterAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_key', 'check_type')


admin.site.register(Printer, PrinterAdmin)

class PointAdmin(admin.ModelAdmin):
    list_display = ('name_point', 'adress')

admin.site.register(Point, PointAdmin)