from django.db import models
import json

class Point(models.Model):
    point_id = models.IntegerField(max_length=50)
    name_point = models.CharField(max_length=50)
    adress = models.CharField(max_length=50)

    def __str__(self):
        return self.point_id



class Printer(models.Model):
    name = models.CharField(max_length=50, unique=True)
    api_key = models.CharField(max_length=50, unique=True)
    check_type = models.CharField(max_length=50)
    point_id = models.ForeignKey(Point, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Check:
    file = "check.json"

    def __init__(self, printer_id, type, order, status, pdf_file):
        self.print_id = printer_id
        self.type = type
        self.order = order
        self.status = status
        self.pdf_file = pdf_file

    def to_dict(self):
        return {
            'printer_id': self.printer_id,
            'type': self.type,
            'order': self.order,
            'status': self.status,
            'pdf_file': self.pdf_file,
        }

    def get_file_data(str, file_name):
        file = open("database/" + file_name, 'r')
        data = json.loads(file.read())
        file.close()
        return data

    def save_to_file(self, data):
        data = json.dumps(data)
        file = open('database/' + self.file, "w")
        file.write(data)
        file.close()

    def save(self):
        car_in_dict_format = self._generate_dict()
        car = self.get_file_data(self.file)
        car.append(car_in_dict_format)
        self.save_to_file(Check)



