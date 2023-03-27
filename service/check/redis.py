import redis
import os
import requests

from django.conf import settings

from .models import Printer

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def add_check_to_redis(printer_id, order_id, type, status):
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
    key = f"{printer_id}_{order_id}"
    value = f"{type}_{status}"
    r.set(key, value)

def get_checks_for_printer_from_redis(printer_id):
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
    keys = r.keys(f"{printer_id}_*")
    check_ids = [key.decode().split("_")[1] for key in keys]
    return check_ids

def get_check_from_redis(printer_id, order):
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
    key = f"{printer_id}_{order}"
    value = r.get(key)
    if value is not None:
        type, status = value.decode().split("_")
        return type, status
    else:
        return None, None

def check_for_new_checks():
    printers = Printer.objects.all()
    for printer in printers:
        printer_id = printer.id

        check_ids = redis_client.lrange(f"printer:{printer_id}:checks", 0, -1)
        for check_id in check_ids:

            if redis_client.hget(f"printer:{printer_id}:checks:{check_id}", "status") == "printed":
                continue

            type = redis_client.hget(f"printer:{printer_id}:checks:{check_id}", "type")
            url = f"http://localhost:8000/checks/{check_id}/download/{type}"
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to download PDF for check {check_id}")
                continue

            filename = f"{check_id}_{type}.pdf"
            filepath = os.path.join(settings.MEDIA_ROOT, "pdf", filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            redis_client.hset(f"printer:{printer_id}:checks:{check_id}", "status", "printed")
            # Send the PDF file to the printer for printing
            send_to_printer(filepath)

# Функція реалізована окремо оскільки вона залежить від специфіки принтера
# Приклад написав в файлі send_to_print
def send_to_printer(filepath):
    pass