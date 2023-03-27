import time
import json
import requests
import redis


REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0


CHECKS_URL = 'http://example.com/api/checks'


POLL_INTERVAL = 60


PDF_FOLDER = 'media/pdf/'

redis_conn = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


def get_checks(printer_id):
    response = requests.get(f'{CHECKS_URL}?printer_id={printer_id}')
    checks = json.loads(response.text)
    return checks


def download_pdf(check_id, check_type):
    response = requests.get(f'{CHECKS_URL}/{check_id}/{check_type}')
    with open(f'{PDF_FOLDER}{check_id}_{check_type}.pdf', 'wb') as f:
        f.write(response.content)


def print_check(printer_id, type):
    pass

def poll_checks(printer_id):
    while True:
        checks = get_checks(printer_id)
        for check in checks:
            check_id = check['id']
            type = check['type']
            if not redis_conn.sismember(printer_id, f'{check_id}_{type}'):
                download_pdf(check_id, type)
                redis_conn.sadd(printer_id, f'{check_id}_{type}')
                print_check(check_id, type)
        time.sleep(POLL_INTERVAL)