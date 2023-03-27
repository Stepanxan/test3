from django.urls import path
from . import views





urlpatterns = [
    path('', views.home),
    path('printer_list/', views.printer_list, name='printer_list')
]