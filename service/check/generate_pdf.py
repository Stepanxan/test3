from celery import shared_task
import os
import subprocess

@shared_task
def generate_pdf(printer_id, type):
    file_name = f"{printer_id}_{type}.pdf"
    file_path = f"media/pdf/{file_name}"
    html_path = "path/to/html/template.html"

    # Generate PDF
    subprocess.call(["wkhtmltopdf", html_path, file_path])

    # Check if file was generated
    if os.path.isfile(file_path):
        return True
    else:
        return False