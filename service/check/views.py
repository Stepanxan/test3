import json
import os
import tempfile
import subprocess

from django.http import HttpResponse
from django.conf import settings
from django.core.files import File
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from django.contrib import messages
import random
import string

from .models import  Check, Point, Printer

def home(request):
    return render(request, 'home.html')


@api_view(['POST'])
def create_check(request):
    if request.method == 'POST':
        printer_id = request.POST['printer_id']
        check_type = request.POST['type']
        order = request.POST['order']
        status = request.POST['status']

        printer = Printer.objects.get(pk=printer_id)

        check = Check(printer_id=printer_id, type=check_type, order=order, status=status)
        check.save()


        check_data = {
            'printer_name': printer.name,
            'type': check_type,
            'order': order,
            'status': status,
        }
        check_json = json.dumps(check_data)


        pdf_bytes = subprocess.check_output(['wkhtmltopdf', '-', '-'], input=check_json.encode())

        # Відправка PDF-файлу як відповідь на запит
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="check.pdf"'
        response.write(pdf_bytes)
        return response

        return render(request, 'create_check.html')


def generate_pdf_check(printer_id, type, order, status):
    printer_id = Check.objects.get(id=printer_id)
    type = Check.objects.get(type=type)
    order = Check.objects.get(order=order)
    status = Check.objects.get(status=status)
    customer = print.customer

    html_template = f"""
        <html>
            <body>
                <h1>{customer.name} Check #{printer_id.id}</h1>
                <p>Type total: {type.total}</p>
                <p>Order total: {order.total}</p>
                <p>Status total: {status.total}</p>           
            </body>
        </html>
        """

    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as html_file:
        with open(html_file.name, 'w') as f:
            f.write(html_template)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as pdf_file:
            cmd = f'wkhtmltopdf {html_file.name} {pdf_file.name}'
            os.system(cmd)
            pdf_file.seek(0)

            path = os.path.join(settings.MEDIA_ROOT, 'pdf')
            os.makedirs(path, exist_ok=True)
            filename = f'{printer_id.id}_{type}.pdf'
            with open(os.path.join(path, filename), 'wb') as f:
                f.write(pdf_file.read())

            # Збереження даних про чек у базі даних
            check = Check.objects.create(
                printer_id=printer_id,
                type=type,
                order=order,
                status=status,
                pdf=File(pdf_file, name=filename)
            )
            check.save()
    os.unlink(html_file.name)
    os.unlink(pdf_file.name)
    return f'Check {check.id} generated'

def add_point(request):
    if request.method == 'POST':
        name_point = request.POST['name_post']
        adress = request.POST['adress']

        if Point.objects.filter(name_point=name_point).exists():
            message = 'Ресторан з таким іменем вже існує'
            return render(request, 'home.html', {'message': message})

        point = Point(name_point=name_point, adress=adress)
        point.save()
        messages.success(request, 'Ресторан був успішно доданий!')
        return redirect('point_list')

    return render(request, 'home.html')

def point_list(request):
    point = Point.objects.all()
    return render(request, 'point_list.html', {'point': point})




def add_printer(request):
    if request.method == 'POST':
        name = request.POST['name']
        check_type = request.POST['check_type']


        if Printer.objects.filter(name=name).exists():
            message = 'Принтер з таким іменем вже існує'
            return render(request, 'home.html', {'message': message})


        api_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))


        printer = Printer(name=name, api_key=api_key, check_type=check_type)
        printer.save()

        messages.success(request, 'Принтер був успішно доданий!')
        return redirect('printer_list')

    return render(request, 'home.html')

def printer_list(request):
    printers = Printer.objects.all()
    return render(request, 'printer_list.html', {'printers': printers})

